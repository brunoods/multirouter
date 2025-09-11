import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import os

# Importe todas as suas páginas aqui
from ui.overview_page import OverviewPage
from ui.inventory_page import InventoryPage
from ui.mass_commands_page import MassCommandsPage
from ui.discovery_page import DiscoveryPage
from ui.diagnostics_page import DiagnosticsPage
from ui.templates_page import TemplatesPage
from ui.ipam_page import IPAMPage
from ui.compliance_page import CompliancePage
from ui.alerts_page import AlertsPage
from ui.security_page import SecurityPage
from ui.config_diff_page import ConfigDiffPage
from ui.interfaces_page import InterfacesPage
from ui.routing_page import RoutingPage
from ui.vlans_page import VLANsPage  # <-- CORREÇÃO AQUI (era VlansPage)


class MultiRouterApp(tb.Window):
    def __init__(self):
        super().__init__(themename="darkly")
        self.title("Multi-Router Management Tool")
        self.geometry("1280x800")
        
        try:
            self.iconpath = os.path.join(os.path.dirname(__file__), 'assets', 'icons', 'dashboard.png')
            self.iconphoto = tk.PhotoImage(file=self.iconpath)
            self.tk.call('wm', 'iconphoto', self._w, self.iconphoto)
        except tk.TclError:
            print(f"Não foi possível carregar o ícone: {self.iconpath}")

        self.pages = {}
        self._create_widgets()

    def _create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=BOTH, expand=True)

        self.sidebar_frame = ttk.Frame(main_frame, width=220, style='secondary.TFrame')
        self.sidebar_frame.pack(side=LEFT, fill=Y)
        self.sidebar_frame.pack_propagate(False)

        self.main_frame = ttk.Frame(main_frame)
        self.main_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)

        self.sidebar_buttons = {}
        
        button_info = {
            "Visão Geral": OverviewPage,
            "Inventário": InventoryPage,
            "Comandos em Massa": MassCommandsPage,
            "Descoberta de Rede": DiscoveryPage,
            "Diagnósticos": DiagnosticsPage,
            "Templates": TemplatesPage,
            "IPAM": IPAMPage,
            "Compliance": CompliancePage,
            "Alertas": AlertsPage,
            "Segurança": SecurityPage,
            "Comparar Configs": ConfigDiffPage,
            "Interfaces": InterfacesPage,
            "Roteamento": RoutingPage,
            "VLANs": VLANsPage,  # <-- CORREÇÃO AQUI (era VlansPage)
        }

        for name, page_class in button_info.items():
            button = ttk.Button(
                self.sidebar_frame,
                text=name,
                command=lambda p=name: self.show_page(p),
                style='primary.Outline.TButton'
            )
            button.pack(fill=X, pady=5, padx=10)
            self.sidebar_buttons[name] = button

            page = page_class(self.main_frame, self)
            self.pages[name] = page
            page.grid(row=0, column=0, sticky="nsew")

        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        self.show_page("Visão Geral")

    def show_page(self, page_name):
        page = self.pages[page_name]
        # Adiciona um método para que as páginas possam ser atualizadas ao serem exibidas
        if hasattr(page, 'on_show'):
            page.on_show()
        page.tkraise()
        
        for name, button in self.sidebar_buttons.items():
            if name == page_name:
                button.config(style='primary.TButton')
            else:
                button.config(style='primary.Outline.TButton')

if __name__ == "__main__":
    app = MultiRouterApp()
    app.mainloop()