import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from ttkbootstrap.scrolled import ScrolledFrame
import logging
import os
from PIL import Image, ImageTk

from logic.logger_config import setup_logging
from logic.inventory_manager import InventoryManager
from logic.connection import connect, disconnect, get_connection, get_connection_status
from logic.configuration import get_config
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

class NetConfigApp(tb.Window):
    def __init__(self):
        super().__init__(themename="darkly")
        setup_logging()
        logging.info("Aplicação NetConfig iniciada.")
        self.title("NetConfig Tool")
        self.geometry("1280x800")
        self.minsize(1024, 768)
        self.inventory_manager = InventoryManager()
        self.pages = {}
        self.create_widgets()
        self.show_page("overview")
        self.update_device_list()

    def create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)
        self.create_toolbar(main_frame)
        self.content_frame = ttk.Frame(main_frame)
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.create_pages()

    def create_toolbar(self, parent):
        sidebar_frame = ttk.Frame(parent, width=240)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0), pady=5)
        sidebar_frame.pack_propagate(False)
        scrolled_frame = ScrolledFrame(sidebar_frame, autohide=True, bootstyle="light")
        scrolled_frame.pack(fill=tk.BOTH, expand=True)
        toolbar = scrolled_frame.container
        self.load_icons()
        buttons = {
            "overview": ("Visão Geral", self.dashboard_icon), "inventory": ("Inventário", self.inventory_icon),
            "interfaces": ("Interfaces", self.interface_icon), "routing": ("Roteamento", self.route_icon),
            "vlans": ("VLANs", self.vlan_icon), "security": ("Segurança", self.security_icon),
            "mass_commands": ("Comandos", self.mass_command_icon), "config_diff": ("Comparar", self.diff_icon),
            "discovery": ("Descoberta", self.discovery_icon), "diagnostics": ("Diagnóstico", self.diagnostics_icon),
            "templates": ("Templates", self.templates_icon), "ipam": ("IPAM", self.ipam_icon),
            "compliance": ("Compliance", self.compliance_icon), "alerts": ("Alertas", self.alert_icon),
        }
        for name, (text, icon) in buttons.items():
            btn = ttk.Button(toolbar, text=text, image=icon, compound=tk.LEFT, bootstyle="link", command=lambda n=name: self.show_page(n))
            btn.pack(fill=tk.X, padx=15, pady=10)

    def load_icons(self):
        icon_path = "assets/icons/"
        icon_size = (24, 24)
        self.icon_map = {}
        icons_to_load = [
            "dashboard", "inventory", "mass_command", "diff", "discovery", "diagnostics",
            "templates", "ipam", "compliance", "alert", "interface", "route", "vlan", "security"
        ]
        for icon_name in icons_to_load:
            try:
                filepath = os.path.join(icon_path, f"{icon_name}.png")
                img = Image.open(filepath)
                img_resized = img.resize(icon_size, Image.Resampling.LANCZOS)
                self.icon_map[icon_name] = ImageTk.PhotoImage(img_resized)
            except (FileNotFoundError, Exception) as e:
                logging.error(f"Erro ao carregar ou redimensionar ícone {filepath}: {e}")
                empty_img = Image.new('RGBA', icon_size, (0, 0, 0, 0))
                self.icon_map[icon_name] = ImageTk.PhotoImage(empty_img)
        self.dashboard_icon = self.icon_map["dashboard"]
        self.inventory_icon = self.icon_map["inventory"]
        self.mass_command_icon = self.icon_map["mass_command"]
        self.diff_icon = self.icon_map["diff"]
        self.discovery_icon = self.icon_map["discovery"]
        self.diagnostics_icon = self.icon_map["diagnostics"]
        self.templates_icon = self.icon_map["templates"]
        self.ipam_icon = self.icon_map["ipam"]
        self.compliance_icon = self.icon_map["compliance"]
        self.alert_icon = self.icon_map["alert"]
        self.interface_icon = self.icon_map["interface"]
        self.route_icon = self.icon_map["route"]
        self.vlan_icon = self.icon_map["vlan"]
        self.security_icon = self.icon_map["security"]

    def create_pages(self):
        pages_classes = {
            "overview": OverviewPage, "inventory": InventoryPage, "interfaces": InterfacesPage,
            "routing": RoutingPage, "vlans": VLANsPage, "security": SecurityPage,
            "mass_commands": MassCommandsPage, "config_diff": ConfigDiffPage, "discovery": DiscoveryPage,
            "diagnostics": DiagnosticsPage, "templates": TemplatesPage, "ipam": IPAMPage,
            "compliance": CompliancePage, "alerts": AlertsPage,
        }
        for name, PageClass in pages_classes.items():
            page = PageClass(self.content_frame, self)
            self.pages[name] = page
            page.grid(row=0, column=0, sticky="nsew")

    def show_page(self, page_name):
        page = self.pages.get(page_name)
        if page:
            page.tkraise()
            if hasattr(page, "refresh"):
                page.refresh()

    def update_device_list(self):
        devices = self.inventory_manager.get_devices()
        for page in self.pages.values():
            if hasattr(page, "update_device_list"):
                page.update_device_list(devices)

    def get_selected_device(self):
        inventory_page = self.pages.get("inventory")
        return inventory_page.get_selected_device() if inventory_page else None
    
    def connect_to_selected_device(self):
        device = self.get_selected_device()
        if device and connect(device):
            self.pages["overview"].refresh()

    def disconnect_from_selected_device(self):
        device = self.get_selected_device()
        if device:
            disconnect(device)
            self.pages["overview"].refresh()

    def show_config_for_selected_device(self):
        device = self.get_selected_device()
        conn = get_connection(device)
        if conn:
            config = get_config(device, conn)
            self.pages["overview"].update_config_display(config)

if __name__ == "__main__":
    app = NetConfigApp()
    app.mainloop()