# ui/overview_page.py
import tkinter as tk
from tkinter import ttk
# A lógica de monitorização é importada e chamada pelo app.py, não diretamente aqui

class OverviewPage(ttk.Frame):
    """Página de Visão Geral com todas as tabelas de resumo e controlos de monitorização."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        
        self.controller = controller

        # --- Frame de Controlo Superior ---
        top_frame = ttk.Frame(self)
        top_frame.pack(fill="x", padx=7, pady=5)
        
        # Informações Gerais (Esquerda)
        info_frame = ttk.Frame(top_frame)
        info_frame.pack(side="left")
        ttk.Label(info_frame, text="Hostname:", font=('Segoe UI', 10, 'bold')).pack(side="left")
        self.hostname_value = ttk.Label(info_frame, text="N/A", font=('Segoe UI', 10))
        self.hostname_value.pack(side="left", padx=5)

        # Controlo de Monitorização (Direita)
        monitor_controls_frame = ttk.Frame(top_frame)
        monitor_controls_frame.pack(side="right")
        ttk.Label(monitor_controls_frame, text="Intervalo (s):").pack(side="left", padx=(10, 2))
        self.interval_entry = ttk.Entry(monitor_controls_frame, width=5)
        self.interval_entry.pack(side="left")
        self.interval_entry.insert(0, "300") # Padrão de 5 minutos
        
        # O comando deste botão será definido no app.py
        self.monitor_button = ttk.Button(monitor_controls_frame, text="Iniciar Monitorização",  style="primary" )
        self.monitor_button.pack(side="left", padx=10)


        # Notebook para as tabelas de resumo
        summary_notebook = ttk.Notebook(self)
        summary_notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Abas e tabelas
        self.interfaces_tree = self.create_treeview_tab(summary_notebook, "Interfaces", ("Interface", "IP", "Status", "Descrição", "VLAN Access"))
        self.vlans_tree = self.create_treeview_tab(summary_notebook, "VLANs", ("ID", "Nome", "Status"))
        self.rotas_tree = self.create_treeview_tab(summary_notebook, "Rotas", ("Destino", "Próximo Salto"))
        self.acls_tree = self.create_treeview_tab(summary_notebook, "ACLs", ("Tipo", "Nome/ID"))

    def create_treeview_tab(self, notebook, text, columns):
        """Cria uma aba com uma tabela (Treeview) dentro e retorna a tabela."""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=text)
        
        tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor="w")
        tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        return tree