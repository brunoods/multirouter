import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from .base_page import BasePage
from logic.vlan_manager import get_device_vlans, create_vlan
from logic.inventory_manager import InventoryManager

class VLANsPage(BasePage):
    def __init__(self, parent, app):
        super().__init__(parent, app, page_title="Gestão de VLANs")

    def create_content(self):
        self.inventory_manager = InventoryManager()
        self.devices = [] # Para guardar a lista de dispositivos

        # Frame de ações com seletor de dispositivo
        action_frame = ttk.Labelframe(self, text="Selecione um Dispositivo", padding=10)
        action_frame.pack(fill="x", padx=10, pady=5)

        self.device_selector = ttk.Combobox(action_frame, state="readonly", width=40)
        self.device_selector.pack(side="left", fill="x", expand=True)

        load_btn = ttk.Button(action_frame, text="Carregar VLANs", command=self.load_vlans)
        load_btn.pack(side="left", padx=10)
        
        create_btn = ttk.Button(action_frame, text="Criar Nova VLAN", command=self.create_vlan_action, style="success.TButton")
        create_btn.pack(side="left")

        # Treeview para exibir as VLANs
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.vlans_tree = ttk.Treeview(tree_frame, columns=("id", "name", "status"), show="headings")
        self.vlans_tree.heading("id", text="ID da VLAN")
        self.vlans_tree.heading("name", text="Nome")
        self.vlans_tree.heading("status", text="Status")
        self.vlans_tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.vlans_tree.yview)
        self.vlans_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        self.refresh_device_list()

    def on_show(self):
        """Chamado sempre que a página é exibida."""
        self.refresh_device_list()

    def refresh_device_list(self):
        """Atualiza a lista de dispositivos no seletor."""
        self.devices = self.inventory_manager.get_devices()
        device_names = [f"{d['name']} ({d['ip']})" for d in self.devices]
        self.device_selector['values'] = device_names
        if device_names:
            self.device_selector.current(0)

    def get_selected_device(self):
        """Obtém o dicionário do dispositivo selecionado no combobox."""
        selected_index = self.device_selector.current()
        if selected_index == -1:
            return None
        return self.devices[selected_index]

    def load_vlans(self):
        """Busca e exibe as VLANs do dispositivo selecionado."""
        for item in self.vlans_tree.get_children():
            self.vlans_tree.delete(item)

        device = self.get_selected_device()
        if not device:
            messagebox.showinfo("Aviso", "Por favor, selecione um dispositivo na lista.")
            return

        vlans = get_device_vlans(device)
        if vlans:
            for vlan in vlans:
                self.vlans_tree.insert("", "end", values=(vlan.get("id"), vlan.get("name"), vlan.get("status")))
        else:
            messagebox.showinfo("Informação", f"Nenhuma VLAN encontrada ou erro ao comunicar com {device['name']}.")

    def create_vlan_action(self):
        device = self.get_selected_device()
        if not device:
            messagebox.showerror("Erro", "Nenhum dispositivo selecionado.")
            return

        vlan_id = simpledialog.askstring("Criar VLAN", "Insira o ID da nova VLAN:", parent=self)
        if not vlan_id or not vlan_id.isdigit():
            if vlan_id is not None: # Não mostra aviso se o utilizador clicou em "Cancelar"
                messagebox.showwarning("Inválido", "O ID da VLAN deve ser um número.")
            return

        vlan_name = simpledialog.askstring("Criar VLAN", f"Insira o nome para a VLAN {vlan_id}:", parent=self)
        if not vlan_name:
            return

        create_vlan(device, vlan_id, vlan_name)
        self.after(1000, self.load_vlans) # Atualiza a lista após 1 segundo