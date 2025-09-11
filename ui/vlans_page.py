# ui/vlans_page.py
import tkinter as tk
from tkinter import ttk
from logic.configuration import create_vlan


class VlansPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # --- Widgets de Configuração ---
        config_frame = ttk.LabelFrame(self, text="4. Gerenciamento de VLANs")
        config_frame.pack(padx=20, pady=20, fill="x", anchor="n")

        ttk.Label(config_frame, text="ID da VLAN:").grid(
            row=0, column=0, sticky="w", pady=5, padx=5
        )
        self.entry_vlan_id = ttk.Entry(config_frame, width=25)
        self.entry_vlan_id.grid(row=0, column=1, pady=5, padx=5)

        ttk.Label(config_frame, text="Nome da VLAN:").grid(
            row=1, column=0, sticky="w", pady=5, padx=5
        )
        self.entry_vlan_name = ttk.Entry(config_frame, width=25)
        self.entry_vlan_name.grid(row=1, column=1, pady=5, padx=5)

        ttk.Button(
            config_frame,
            text="Criar/Atualizar VLAN",
            style="primary",
            command=lambda: create_vlan(self.controller),
        ).grid(row=2, columnspan=2, pady=10)
