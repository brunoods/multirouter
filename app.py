import ttkbootstrap as tk
from ttkbootstrap import ttk
from ttkbootstrap.style import Bootstyle
from PIL import Image, ImageTk

# Importa as nossas "páginas" e a "lógica"
from ui.overview_page import OverviewPage
from ui.interfaces_page import InterfacesPage
from ui.vlans_page import VlansPage
from ui.routing_page import RoutingPage
from ui.security_page import SecurityPage
from ui.inventory_page import InventoryPage
from ui.mass_commands_page import MassCommandsPage
from ui.config_diff_page import ConfigDiffPage
from ui.diagnostics_page import DiagnosticsPage
from ui.alerts_page import AlertsPage
from ui.templates_page import TemplatesPage
from ui.ipam_page import IPAMPage
from ui.compliance_page import CompliancePage
from ui.discovery_page import DiscoveryPage
from logic.connection import connect_and_read_config
from logic.configuration import save_configuration, export_configuration, restore_configuration
from logic.inventory_manager import load_inventory
from logic.monitoring import toggle_monitoring

from vendors import cisco_ios, juniper_junos, mikrotik_routeros

VENDOR_MODULES = {
    "Switch Cisco IOS": cisco_ios,
    "Roteador Cisco IOS": cisco_ios,
    "Switch Juniper Junos": juniper_junos,
    "Mikrotik RouterOS": mikrotik_routeros,
}

# --- Função Auxiliar para Carregar Ícones ---
def load_icon(filename, size=(16, 16)):
    """Carrega um ícone, redimensiona-o e trata erros se o ficheiro não for encontrado."""
    try:
        path = f"assets/icons/{filename}"
        image = Image.open(path).resize(size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(image)
    except FileNotFoundError:
        print(f"Aviso: Ícone não encontrado em '{path}'")
        return None

class NetConfigApp(tk.Window):
    def __init__(self):
        super().__init__(themename="vapor")
        
        self.title("Configurador de Rede Profissional")
        self.state('zoomed') # Inicia a janela maximizada

        # --- Personalização Avançada de Estilos ---

        # --- Carregar Ícones ---
        self.icons = {
            'connect': load_icon('connect.png'), 'save': load_icon('save.png'),
            'export': load_icon('export.png'), 'restore': load_icon('restore.png'),
            'overview': load_icon('dashboard.png'), 'inventory': load_icon('inventory.png'),
            'ipam': load_icon('ipam.png'), 'alerts': load_icon('alert.png'),
            'templates': load_icon('templates.png'), 'mass_commands': load_icon('mass_command.png'),
            'diff': load_icon('diff.png'), 'diagnostics': load_icon('diagnostics.png'),
            'interfaces': load_icon('interface.png'), 'vlans': load_icon('vlan.png'),
            'routing': load_icon('route.png'), 'security': load_icon('security.png'),
            'compliance': load_icon('compliance.png'), 'discovery': load_icon('discovery.png')
        }

        # --- Variáveis de Controle ---
        self.VENDOR_MODULES = VENDOR_MODULES
        self.sim_mode = tk.BooleanVar(value=True)
        self.raw_command_outputs = {}
        self.inventory = []
        self.is_monitoring = False

        # --- Estrutura Principal da GUI ---
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        toolbar_frame = ttk.Frame(self, padding=5)
        toolbar_frame.grid(row=0, column=0, sticky="ew")
        self.create_toolbar_widgets(toolbar_frame)
        
        main_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_pane.grid(row=1, column=0, sticky="nsew")

        menu_frame = ttk.Frame(main_pane, width=260)
        menu_frame.pack_propagate(False)
        main_pane.add(menu_frame, weight=0) 
        
        self.create_menu_widgets(menu_frame)
        
        content_frame = ttk.Frame(self)
        main_pane.add(content_frame, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.pages = {
            "OverviewPage": OverviewPage, "InventoryPage": InventoryPage, "IPAMPage": IPAMPage,
            "DiscoveryPage": DiscoveryPage, "MassCommandsPage": MassCommandsPage, "ConfigDiffPage": ConfigDiffPage,
            "DiagnosticsPage": DiagnosticsPage, "AlertsPage": AlertsPage, "TemplatesPage": TemplatesPage,
            "CompliancePage": CompliancePage, "InterfacesPage": InterfacesPage, 
            "VlansPage": VlansPage, "RoutingPage": RoutingPage, "SecurityPage": SecurityPage
        }
        for F_class in self.pages.values():
            frame = F_class(content_frame, self)
            self.frames[F_class] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.status_label = ttk.Label(self, text="Pronto.", relief="sunken", anchor="w", padding=5)
        self.status_label.grid(row=2, column=0, columnspan=2, sticky="ew")

        overview_page = self.frames[OverviewPage]
        if hasattr(overview_page, 'interfaces_tree'):
            overview_page.interfaces_tree.bind('<<TreeviewSelect>>', self.on_interface_select_overview)
        if hasattr(overview_page, 'monitor_button'):
            overview_page.monitor_button.config(command=lambda: toggle_monitoring(self))

        self.update_connection_menu()
        self.show_frame(OverviewPage)

    def create_toolbar_widgets(self, parent):
        """Cria os widgets da barra de ferramentas superior."""
        ttk.Label(parent, text="Dispositivo:").pack(side="left", padx=(5, 2))
        self.device_combobox = ttk.Combobox(parent, state="readonly", width=25)
        self.device_combobox.pack(side="left", padx=(0, 10))
        
        ttk.Button(parent, text="Conectar", image=self.icons.get('connect'), compound="left", command=lambda: connect_and_read_config(self), bootstyle="primary").pack(side="left")
        
        ttk.Separator(parent, orient="vertical").pack(side="left", padx=10, fill="y")
        
        ttk.Button(parent, text="Salvar", image=self.icons.get('save'), compound="left", command=lambda: save_configuration(self), bootstyle="primary").pack(side="left", padx=2)

        ttk.Button(parent, text="Exportar", image=self.icons.get('export'), compound="left", command=lambda: export_configuration(self), bootstyle="primary").pack(side="left", padx=2)

        ttk.Button(parent, text="Restaurar", image=self.icons.get('restore'), compound="left", command=lambda: restore_configuration(self), bootstyle="primary").pack(side="left", padx=2)

        ttk.Separator(parent, orient="vertical").pack(side="left", padx=10, fill="y")
        ttk.Checkbutton(parent, text="Modo Simulação", variable=self.sim_mode, bootstyle="round-toggle").pack(side="left", padx=10)

    def create_menu_widgets(self, parent):
        """Cria os widgets de navegação no menu da esquerda."""
        nav_frame = ttk.LabelFrame(parent, text="Gestão e Visualização")
        nav_frame.pack(fill="x", padx=10, pady=10)
        ttk.Button(nav_frame, text="Visão Geral", image=self.icons.get('overview'), compound="left", command=lambda: self.show_frame(OverviewPage), style="Left.light.TButton").pack(fill="x")
        ttk.Button(nav_frame, text="Inventário", image=self.icons.get('inventory'), compound="left", command=lambda: self.show_frame(InventoryPage), style="Left.light.TButton").pack(fill="x")
        ttk.Button(nav_frame, text="Descoberta de Rede", image=self.icons.get('discovery'), compound="left", command=lambda: self.show_frame(DiscoveryPage), style="Left.light.TButton").pack(fill="x")
        ttk.Button(nav_frame, text="Gestão de IPs (IPAM)", image=self.icons.get('ipam'), compound="left", command=lambda: self.show_frame(IPAMPage), style="Left.light.TButton").pack(fill="x")
        ttk.Button(nav_frame, text="Alertas", image=self.icons.get('alerts'), compound="left", command=lambda: self.show_frame(AlertsPage), style="Left.light.TButton").pack(fill="x")
        
        tools_frame = ttk.LabelFrame(parent, text="Ferramentas e Automação")
        tools_frame.pack(fill="x", padx=10, pady=10)
        ttk.Button(tools_frame, text="Templates", image=self.icons.get('templates'), compound="left", command=lambda: self.show_frame(TemplatesPage), style="Left.light.TButton").pack(fill="x")
        ttk.Button(tools_frame, text="Comandos em Massa", image=self.icons.get('mass_commands'), compound="left", command=lambda: self.show_frame(MassCommandsPage), style="Left.light.TButton").pack(fill="x")
        ttk.Button(tools_frame, text="Comparar Configs", image=self.icons.get('diff'), compound="left", command=lambda: self.show_frame(ConfigDiffPage), style="Left.light.TButton").pack(fill="x")
        ttk.Button(tools_frame, text="Diagnóstico", image=self.icons.get('diagnostics'), compound="left", command=lambda: self.show_frame(DiagnosticsPage), style="Left.light.TButton").pack(fill="x")

        config_frame = ttk.LabelFrame(parent, text="Configuração e Auditoria")
        config_frame.pack(fill="x", padx=10, pady=10)
        ttk.Button(config_frame, text="Interfaces", image=self.icons.get('interfaces'), compound="left", command=lambda: self.show_frame(InterfacesPage), style="Left.light.TButton").pack(fill="x")
        ttk.Button(config_frame, text="VLANs", image=self.icons.get('vlans'), compound="left", command=lambda: self.show_frame(VlansPage), style="Left.light.TButton").pack(fill="x")
        ttk.Button(config_frame, text="Roteamento", image=self.icons.get('routing'), compound="left", command=lambda: self.show_frame(RoutingPage), style="Left.light.TButton").pack(fill="x")
        ttk.Button(config_frame, text="Segurança", image=self.icons.get('security'), compound="left", command=lambda: self.show_frame(SecurityPage), style="Left.light.TButton").pack(fill="x")
        ttk.Button(config_frame, text="Auditoria", image=self.icons.get('compliance'), compound="left", command=lambda: self.show_frame(CompliancePage), style="Left.light.TButton").pack(fill="x")

    def show_frame(self, cont):
        """Mostra um frame (página) específico."""
        frame = self.frames[cont]
        if cont == InventoryPage: frame.populate_inventory()
        if cont == MassCommandsPage: frame.populate_device_list()
        if cont == AlertsPage:
            frame.populate_rules()
            frame.device_combobox['values'] = [d['name'] for d in self.inventory]
        if cont == TemplatesPage: frame.populate_template_list()
        if cont == IPAMPage: frame.populate_subnet_list()
        frame.tkraise()
    
    def get_selected_vendor_module(self):
        """Obtém o módulo do fabricante com base no dispositivo selecionado no inventário."""
        selected_name = self.device_combobox.get()
        if not selected_name or "Nenhum dispositivo" in selected_name: return None
        device_details = next((d for d in self.inventory if d['name'] == selected_name), None)
        return self.VENDOR_MODULES.get(device_details['type_name']) if device_details else None

    def update_connection_menu(self):
        """Atualiza o menu suspenso de conexão com os dispositivos do inventário."""
        self.inventory = load_inventory()
        device_names = [d['name'] for d in self.inventory]
        self.device_combobox['values'] = device_names
        if device_names: self.device_combobox.set(device_names[0])
        else: self.device_combobox.set("Nenhum dispositivo no inventário")
            
    def update_overview_page(self, parsed_config, parsed_vlans, parsed_routes, parsed_acls):
        """Passa os dados para a página de visão geral para que ela atualize suas tabelas."""
        overview_page = self.frames[OverviewPage]
        interface_page = self.frames[InterfacesPage]
        security_page = self.frames[SecurityPage]
        
        overview_page.hostname_value.config(text=parsed_config.get('hostname', 'N/A'))
        
        trees_data = [
            (overview_page.interfaces_tree, parsed_config.get('interfaces', [])),
            (overview_page.vlans_tree, parsed_vlans),
            (overview_page.rotas_tree, parsed_routes),
            (overview_page.acls_tree, parsed_acls)
        ]
        for tree, data in trees_data:
            for i in tree.get_children(): tree.delete(i)
            if data:
                for item in data: tree.insert("", "end", values=list(item.values()))
        
        if hasattr(interface_page, 'vlan_combobox'):
            vlan_display_list = [f"{v['id']} - {v['name']}" for v in parsed_vlans]
            interface_page.vlan_combobox['values'] = ["Nenhuma"] + vlan_display_list
        
        if hasattr(security_page, 'acl_combobox'):
            acl_display_list = [f"{acl['name_id']} ({acl['type']})" for acl in parsed_acls]
            security_page.acl_combobox['values'] = acl_display_list
            if acl_display_list:
                security_page.acl_combobox.set(acl_display_list[0])
            else:
                security_page.acl_combobox.set("Selecione uma ACL...")
            
    def on_interface_select_overview(self, event):
        """Chamado quando uma interface é selecionada na tabela de Visão Geral."""
        overview_page = self.frames[OverviewPage]
        interface_page = self.frames[InterfacesPage]
        selected_item = overview_page.interfaces_tree.focus()
        if not selected_item: return
        
        item_values = overview_page.interfaces_tree.item(selected_item, 'values')
        if not item_values or len(item_values) < 5: return

        if_name, ip_addr, status, description, access_vlan = item_values
        
        interface_page.selected_interface_name = if_name
        interface_page.if_config_label.config(text=f"Interface: {if_name}")
        interface_page.entry_if_desc.delete(0, tk.END); interface_page.entry_if_desc.insert(0, description)
        interface_page.if_status_var.set("on" if status == "no shutdown" else "off")
        
        vlan_to_select = "Nenhuma"
        if hasattr(interface_page, 'vlan_combobox'):
            for item in interface_page.vlan_combobox['values']:
                if item.startswith(f"{access_vlan} "):
                    vlan_to_select = item
                    break
            interface_page.vlan_combobox.set(vlan_to_select)

# Bloco para executar a aplicação
if __name__ == "__main__":
    app = NetConfigApp()
    app.mainloop()