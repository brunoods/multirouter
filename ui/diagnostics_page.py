# ui/diagnostics_page.py
import tkinter as tk
from tkinter import ttk, scrolledtext
from logic.diagnostics import run_diagnostic_command

class DiagnosticsPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # --- Frame Principal ---
        main_frame = ttk.LabelFrame(self, text="Ferramentas de Diagnóstico de Rede")
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)
        main_frame.grid_rowconfigure(2, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # --- Frame de Controlo ---
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(control_frame, text="Endereço IP de Destino:").pack(side="left", padx=(0, 10))
        self.target_ip_entry = ttk.Entry(control_frame, width=30)
        self.target_ip_entry.pack(side="left", padx=10, fill="x", expand=True)
        self.target_ip_entry.insert(0, "8.8.8.8")

        # --- Frame de Botões ---
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, pady=10)

        self.ping_button = ttk.Button(button_frame, text="Executar Ping", 
                                    style="primary",    command=lambda: run_diagnostic_command(self.controller, 'ping'))
        self.ping_button.pack(side="left", padx=10)

        self.trace_button = ttk.Button(button_frame, text="Executar Traceroute", 
                                    style="primary",     command=lambda: run_diagnostic_command(self.controller, 'traceroute'))
        self.trace_button.pack(side="left", padx=10)

        # --- Frame de Resultados ---
        results_frame = ttk.LabelFrame(main_frame, text="Resultados")
        results_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, font=("Consolas", 9), state="disabled", background="#ffffff")
        self.results_text.pack(fill="both", expand=True, padx=5, pady=5)