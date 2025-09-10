# ui/routing_page.py
import tkinter as tk
from tkinter import ttk
from logic.configuration import add_static_route

class RoutingPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # --- Widgets de Configuração ---
        config_frame = ttk.LabelFrame(self, text="5. Rotas Estáticas")
        config_frame.pack(padx=20, pady=20, fill="x", anchor="n")
        
        ttk.Label(config_frame, text="Rede Destino:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.entry_route_net = ttk.Entry(config_frame, width=25)
        self.entry_route_net.grid(row=0, column=1, pady=5, padx=5)

        ttk.Label(config_frame, text="Máscara/Prefixo:").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.entry_route_mask = ttk.Entry(config_frame, width=25)
        self.entry_route_mask.grid(row=1, column=1, pady=5, padx=5)

        ttk.Label(config_frame, text="Próximo Salto:").grid(row=2, column=0, sticky="w", pady=5, padx=5)
        self.entry_route_nexthop = ttk.Entry(config_frame, width=25)
        self.entry_route_nexthop.grid(row=2, column=1, pady=5, padx=5)

        ttk.Button(config_frame, text="Adicionar Rota", command=lambda: add_static_route(self.controller)).grid(row=3, columnspan=2, pady=10)