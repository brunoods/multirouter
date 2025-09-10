# ui/inventory_page.py
import tkinter as tk
from tkinter import ttk, messagebox
from logic.inventory_manager import load_inventory, remove_device
from ui.device_form import DeviceForm

class InventoryPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        table_frame = ttk.LabelFrame(self, text="Inventário de Dispositivos")
        table_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # --- NOVAS COLUNAS ADICIONADAS ---
        cols = ("Nome Apelido", "Endereço IP", "Tipo", "Versão do SO", "Modelo")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")
        for col in cols:
            self.tree.heading(col, text=col)
        
        # Ajusta a largura das colunas
        self.tree.column("Nome Apelido", width=150)
        self.tree.column("Endereço IP", width=120)
        self.tree.column("Tipo", width=150)
        self.tree.column("Versão do SO", width=200)
        self.tree.column("Modelo", width=150)

        self.tree.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Adicionar Novo...", command=self.open_add_form).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Editar Selecionado...", command=self.open_edit_form).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Remover Selecionado", command=self.delete_selected).pack(side="left", padx=10)
        
        self.populate_inventory()

    def populate_inventory(self):
        """Carrega os dispositivos do ficheiro e preenche a tabela."""
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        self.inventory_data = load_inventory()
        for device in self.inventory_data:
            # Garante que os campos existam antes de os tentar aceder
            os_version = device.get('os_version', 'N/A')
            model = device.get('model', 'N/A')
            self.tree.insert("", "end", iid=device['id'], values=(
                device['name'], device['host'], device['type_name'], os_version, model
            ))

    def open_add_form(self):
        form = DeviceForm(self, self.controller)
        self.wait_window(form)
        if form.result:
            self.populate_inventory()
            self.controller.update_connection_menu()

    def open_edit_form(self):
        selected_iid = self.tree.focus()
        if not selected_iid:
            messagebox.showwarning("Nenhuma Seleção", "Por favor, selecione um dispositivo para editar.", parent=self)
            return

        device_to_edit = next((d for d in self.inventory_data if d['id'] == int(selected_iid)), None)
        if device_to_edit:
            form = DeviceForm(self, self.controller, device_to_edit)
            self.wait_window(form)
            if form.result:
                self.populate_inventory()
                self.controller.update_connection_menu()

    def delete_selected(self):
        selected_iid = self.tree.focus()
        if not selected_iid:
            messagebox.showwarning("Nenhuma Seleção", "Por favor, selecione um dispositivo para remover.", parent=self)
            return

        if messagebox.askyesno("Confirmar Remoção", "Tem a certeza que deseja remover o dispositivo selecionado?", parent=self):
            remove_device(int(selected_iid))
            self.populate_inventory()
            self.controller.update_connection_menu()