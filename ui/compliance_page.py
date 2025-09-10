# ui/compliance_page.py
import tkinter as tk
from tkinter import ttk
from logic.compliance_manager import run_compliance_audit

class CompliancePage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # --- Frame Principal ---
        main_frame = ttk.LabelFrame(self, text="Auditoria de Conformidade de Rede")
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # --- Frame de Controlo ---
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=0, column=0, pady=10)
        
        self.run_button = ttk.Button(control_frame, text="Executar Auditoria em Todos os Dispositivos", style="primary", command=lambda: run_compliance_audit(self.controller))
        self.run_button.pack()

        # --- Tabela de Resultados ---
        results_frame = ttk.Frame(main_frame)
        results_frame.grid(row=1, column=0, sticky="nsew")
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)
        
        cols = ("Dispositivo", "Regra", "Estado", "Detalhes")
        self.tree = ttk.Treeview(results_frame, columns=cols, show="headings")
        for col in cols: self.tree.heading(col, text=col)

        self.tree.column("Dispositivo", width=150)
        self.tree.column("Regra", width=200)
        self.tree.column("Estado", width=100, anchor="center")
        self.tree.column("Detalhes", width=300)
        
        self.tree.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")