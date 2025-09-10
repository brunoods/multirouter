# ui/interfaces_page.py
import tkinter as tk
from tkinter import ttk
from logic.configuration import configure_interface

class InterfacesPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.selected_interface_name = None # Guarda o nome da interface selecionada

        # --- Widgets de Configuração ---
        config_frame = ttk.LabelFrame(self, text="3. Configurar Interface Selecionada")
        config_frame.pack(padx=20, pady=20, fill="x")

        self.if_config_label = ttk.Label(config_frame, text="Interface: (Selecione na Visão Geral)", font=('Segoe UI', 10, 'bold'))
        self.if_config_label.grid(row=0, columnspan=2, sticky="w", pady=(0, 10), padx=5)

        ttk.Label(config_frame, text="Descrição:").grid(row=1, column=0, sticky="w", pady=2, padx=5)
        self.entry_if_desc = ttk.Entry(config_frame, width=30)
        self.entry_if_desc.grid(row=1, column=1, pady=2, padx=5)
        
        self.vlan_access_label = ttk.Label(config_frame, text="VLAN de Acesso:")
        self.vlan_access_label.grid(row=2, column=0, sticky="w", pady=2, padx=5)
        self.vlan_combobox = ttk.Combobox(config_frame, width=27, state="readonly")
        self.vlan_combobox.grid(row=2, column=1, pady=2, padx=5)

        status_frame = ttk.Frame(config_frame)
        status_frame.grid(row=4, columnspan=2, pady=5, sticky="w", padx=5)
        self.if_status_var = tk.StringVar(value="off")
        ttk.Radiobutton(status_frame, text="Habilitada", variable=self.if_status_var, value="on").pack(side="left")
        ttk.Radiobutton(status_frame, text="Desabilitada", variable=self.if_status_var, value="off").pack(side="left", padx=10)
        
        # O botão agora chama a função de lógica, passando a instância principal do app
        ttk.Button(config_frame, text="Aplicar Config. da Interface", style="primary",  command=lambda: configure_interface(self.controller)).grid(row=5, columnspan=2, pady=10)