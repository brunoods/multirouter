import tkinter as tk
from tkinter import ttk, PhotoImage
import ttkbootstrap as tb
from ttkbootstrap.scrolled import ScrolledFrame

from ui.overview_page import OverviewPage
from ui.inventory_page import InventoryPage
from ui.mass_commands_page import MassCommandsPage
from ui.config_diff_page import ConfigDiffPage
from ui.discovery_page import DiscoveryPage
from ui.diagnostics_page import DiagnosticsPage
from ui.templates_page import TemplatesPage
from ui.ipam_page import IPAMPage
from ui.compliance_page import CompliancePage
from ui.alerts_page import AlertsPage
from ui.interfaces_page import InterfacesPage
from ui.routing_page import RoutingPage
from ui.vlans_page import VLANsPage
from ui.security_page import SecurityPage
from logic.logger_config import setup_logging

from logic.inventory_manager import InventoryManager
from logic.connection import connect, disconnect, get_connection_status
from logic.configuration import (
    save_config,
    export_config,
    restore_config,
    get_config,
)

# Mapeamento de fabricantes para os seus módulos de lógica
VENDOR_MODULES = {
    "cisco_ios": "vendors.cisco_ios",
    "juniper_junos": "vendors.juniper_junos",
    "mikrotik_routeros": "vendors.mikrotik_routeros",
}


class NetConfigApp(tb.Window):
    """
    Classe principal da aplicação de gestão de redes (NetConfig).

    Esta classe inicializa a janela principal, a interface do utilizador
    e gere a navegação entre as diferentes páginas da aplicação.
    """

    def __init__(self):
        super().__init__(themename="darkly")
        setup_logging()
        logging.info("Aplicação NetConfig iniciada.")
        self.title("NetConfig Tool")
        self.geometry("1200x800")
        self.inventory_manager = InventoryManager()

        self.pages = {}
        self.create_widgets()
        self.show_page("overview")
        self.update_device_list()

    def create_widgets(self):
        """Cria os widgets principais da interface, como a barra de ferramentas e o menu."""
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Barra de ferramentas lateral
        self.create_toolbar(main_frame)

        # Frame de conteúdo
        self.content_frame = ttk.Frame(main_frame)
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.create_pages()

    def create_toolbar(self, parent):
        """Cria a barra de ferramentas lateral com os botões de navegação."""
        scrolled_frame = ScrolledFrame(parent, autohide=True)
        scrolled_frame.pack(side=tk.LEFT, fill=tk.Y)
        toolbar = scrolled_frame.container
        toolbar.configure(bootstyle="secondary")

        # Ícones
        self.load_icons()

        # Botões da barra de ferramentas
        buttons = {
            "overview": ("Visão Geral", self.dashboard_icon),
            "inventory": ("Inventário", self.inventory_icon),
            "interfaces": ("Interfaces", self.interface_icon),
            "routing": ("Roteamento", self.route_icon),
            "vlans": ("VLANs", self.vlan_icon),
            "security": ("Segurança", self.security_icon),
            "mass_commands": ("Comandos em Massa", self.mass_command_icon),
            "config_diff": ("Comparar Configs", self.diff_icon),
            "discovery": ("Descoberta", self.discovery_icon),
            "diagnostics": ("Diagnóstico", self.diagnostics_icon),
            "templates": ("Templates", self.templates_icon),
            "ipam": ("IPAM", self.ipam_icon),
            "compliance": ("Compliance", self.compliance_icon),
            "alerts": ("Alertas", self.alert_icon),
        }

        for name, (text, icon) in buttons.items():
            btn = ttk.Button(
                toolbar,
                text=text,
                image=icon,
                compound=tk.LEFT,
                bootstyle="secondary",
                command=lambda n=name: self.show_page(n),
            )
            btn.pack(fill=tk.X, padx=5, pady=5)

    def load_icons(self):
        """Carrega os ícones utilizados na interface."""
        self.dashboard_icon = PhotoImage(file="assets/icons/dashboard.png")
        self.inventory_icon = PhotoImage(file="assets/icons/inventory.png")
        self.mass_command_icon = PhotoImage(file="assets/icons/mass_command.png")
        self.diff_icon = PhotoImage(file="assets/icons/diff.png")
        self.discovery_icon = PhotoImage(file="assets/icons/discovery.png")
        self.diagnostics_icon = PhotoImage(file="assets/icons/diagnostics.png")
        self.templates_icon = PhotoImage(file="assets/icons/templates.png")
        self.ipam_icon = PhotoImage(file="assets/icons/ipam.png")
        self.compliance_icon = PhotoImage(file="assets/icons/compliance.png")
        self.alert_icon = PhotoImage(file="assets/icons/alert.png")
        self.interface_icon = PhotoImage(file="assets/icons/interface.png")
        self.route_icon = PhotoImage(file="assets/icons/route.png")
        self.vlan_icon = PhotoImage(file="assets/icons/vlan.png")
        self.security_icon = PhotoImage(file="assets/icons/security.png")

    def create_pages(self):
        """Inicializa todas as páginas da aplicação."""
        pages_classes = {
            "overview": OverviewPage,
            "inventory": InventoryPage,
            "mass_commands": MassCommandsPage,
            "config_diff": ConfigDiffPage,
            "discovery": DiscoveryPage,
            "diagnostics": DiagnosticsPage,
            "templates": TemplatesPage,
            "ipam": IPAMPage,
            "compliance": CompliancePage,
            "alerts": AlertsPage,
            "interfaces": InterfacesPage,
            "routing": RoutingPage,
            "vlans": VLANsPage,
            "security": SecurityPage,
        }

        for name, PageClass in pages_classes.items():
            page = PageClass(self.content_frame, self)
            self.pages[name] = page
            page.grid(row=0, column=0, sticky="nsew")

    def show_page(self, page_name):
        """Mostra a página solicitada no frame de conteúdo."""
        page = self.pages.get(page_name)
        if page:
            page.tkraise()
            if hasattr(page, "refresh"):
                page.refresh()

    def update_device_list(self):
        """Atualiza a lista de dispositivos em todas as páginas relevantes."""
        devices = self.inventory_manager.get_devices()
        for page in self.pages.values():
            if hasattr(page, "update_device_list"):
                page.update_device_list(devices)

    def get_selected_device(self):
        """Retorna o dispositivo atualmente selecionado na página de inventário."""
        inventory_page = self.pages.get("inventory")
        if inventory_page:
            return inventory_page.get_selected_device()
        return None

    def connect_to_device(self):
        """Conecta-se ao dispositivo selecionado."""
        device = self.get_selected_device()
        if device:
            connect(device)
            self.update_connection_status()
            self.show_page("overview")

    def disconnect_from_device(self):
        """Desconecta-se do dispositivo selecionado."""
        device = self.get_selected_device()
        if device:
            disconnect(device)
            self.update_connection_status()

    def update_connection_status(self):
        """Atualiza o status da conexão na interface."""
        device = self.get_selected_device()
        status = get_connection_status(device) if device else "Não conectado"
        self.pages["overview"].update_connection_status_label(status)

    # Funções de gestão de configuração
    def save_device_config(self):
        """Salva a configuração do dispositivo selecionado."""
        device = self.get_selected_device()
        if device and get_connection_status(device) == "Conectado":
            save_config(device)

    def export_device_config(self):
        """Exporta a configuração do dispositivo selecionado."""
        device = self.get_selected_device()
        if device and get_connection_status(device) == "Conectado":
            export_config(device)

    def restore_device_config(self):
        """Restaura a configuração do dispositivo selecionado."""
        device = self.get_selected_device()
        if device and get_connection_status(device) == "Conectado":
            restore_config(device)

    def show_device_config(self):
        """Mostra a configuração atual do dispositivo."""
        device = self.get_selected_device()
        if device and get_connection_status(device) == "Conectado":
            config = get_config(device)
            self.pages["overview"].update_config_display(config)


if __name__ == "__main__":
    app = NetConfigApp()
    app.mainloop()
