import tkinter as tk
from tkinter import ttk
from ui.base_page import BasePage # <-- MUDANÇA AQUI
from .device_form import DeviceForm
from logic.inventory_manager import InventoryManager

class InventoryPage(BasePage):
    def __init__(self, parent, app):
        super().__init__(parent, app, page_title="Gestão de Inventário")

    def create_content(self):
        self.inventory_manager = InventoryManager()
        
        # Frame para a Treeview e a scrollbar
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Treeview para exibir os dispositivos
        self.tree = ttk.Treeview(tree_frame, columns=("ID", "Nome", "IP", "Tipo"), show='headings')
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("IP", text="Endereço IP")
        self.tree.heading("Tipo", text="Tipo de Dispositivo")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Frame para os botões
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        # Botões
        add_button = ttk.Button(button_frame, text="Adicionar Dispositivo", command=self.add_device, style='success.TButton')
        add_button.pack(side=tk.LEFT, padx=5)

        edit_button = ttk.Button(button_frame, text="Editar Dispositivo", command=self.edit_device, style='info.TButton')
        edit_button.pack(side=tk.LEFT, padx=5)

        delete_button = ttk.Button(button_frame, text="Remover Dispositivo", command=self.delete_device, style='danger.TButton')
        delete_button.pack(side=tk.LEFT, padx=5)
        
        self.refresh()

    def refresh(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        devices = self.inventory_manager.get_devices()
        for device in devices:
            self.tree.insert("", "end", values=(device['id'], device['name'], device['ip'], device['type']))

    def add_device(self):
        DeviceForm(self, self.app, self.refresh)

    def edit_device(self):
        selected_item = self.tree.selection()
        if selected_item:
            device_id = self.tree.item(selected_item, "values")[0]
            device = self.inventory_manager.get_device(device_id)
            DeviceForm(self, self.app, self.refresh, device=device)
        else:
            tk.messagebox.showwarning("Aviso", "Selecione um dispositivo para editar.")

    def delete_device(self):
        selected_item = self.tree.selection()
        if selected_item:
            device_id = self.tree.item(selected_item, "values")[0]
            if tk.messagebox.askyesno("Confirmar", "Tem a certeza que deseja remover este dispositivo?"):
                self.inventory_manager.delete_device(device_id)
                self.refresh()
        else:
            tk.messagebox.showwarning("Aviso", "Selecione um dispositivo para remover.")