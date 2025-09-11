"""
Página da interface do utilizador para gerir o inventário de dispositivos.
"""

from tkinter import ttk, messagebox, Toplevel
from .device_form import DeviceForm


class InventoryPage(ttk.Frame):
    """Frame que contém os widgets para a gestão do inventário."""

    def __init__(self, parent, app):
        """
        Inicializa a página de inventário.

        Args:
            parent: O widget pai (normalmente, o content_frame).
            app: A instância principal da aplicação.
        """
        super().__init__(parent)
        self.app = app
        self.inventory_manager = app.inventory_manager

        self.create_widgets()
        self.update_device_list()

    def create_widgets(self):
        """Cria os widgets da página, como a lista e os botões."""
        # Frame para a lista de dispositivos
        list_frame = ttk.Frame(self)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Treeview para exibir dispositivos
        self.device_tree = ttk.Treeview(
            list_frame,
            columns=("hostname", "ip", "device_type"),
            show="headings",
            bootstyle="primary",
        )
        self.device_tree.heading("hostname", text="Hostname")
        self.device_tree.heading("ip", text="Endereço IP")
        self.device_tree.heading("device_type", text="Tipo de Dispositivo")
        self.device_tree.pack(fill="both", expand=True)

        # Frame para os botões
        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", padx=10, pady=(0, 10))

        # Botões de ação
        add_btn = ttk.Button(
            button_frame, text="Adicionar", command=self.add_device, bootstyle="success"
        )
        add_btn.pack(side="left", padx=5)

        edit_btn = ttk.Button(
            button_frame, text="Editar", command=self.edit_device, bootstyle="info"
        )
        edit_btn.pack(side="left", padx=5)

        remove_btn = ttk.Button(
            button_frame,
            text="Remover",
            command=self.remove_device,
            bootstyle="danger",
        )
        remove_btn.pack(side="left", padx=5)

    def update_device_list(self, devices=None):
        """
        Atualiza a lista de dispositivos na Treeview.

        Args:
            devices (list, optional): A lista de dispositivos a exibir.
                                      Se None, obtém do inventory_manager.
        """
        if devices is None:
            devices = self.inventory_manager.get_devices()

        # Limpa a lista atual
        for item in self.device_tree.get_children():
            self.device_tree.delete(item)

        # Adiciona os dispositivos
        for device in devices:
            self.device_tree.insert(
                "", "end", values=(device["host"], device["ip"], device["device_type"])
            )

    def add_device(self):
        """Abre o formulário para adicionar um novo dispositivo."""
        DeviceForm(self, self.app, title="Adicionar Dispositivo")

    def edit_device(self):
        """Abre o formulário para editar o dispositivo selecionado."""
        selected_item = self.device_tree.selection()
        if not selected_item:
            messagebox.showwarning(
                "Nenhum Dispositivo Selecionado",
                "Por favor, selecione um dispositivo para editar.",
            )
            return

        device_index = self.device_tree.index(selected_item[0])
        device_data = self.inventory_manager.get_devices()[device_index]
        DeviceForm(
            self,
            self.app,
            device=device_data,
            device_index=device_index,
            title="Editar Dispositivo",
        )

    def remove_device(self):
        """Remove o dispositivo selecionado da lista."""
        selected_item = self.device_tree.selection()
        if not selected_item:
            messagebox.showwarning(
                "Nenhum Dispositivo Selecionado",
                "Por favor, selecione um dispositivo para remover.",
            )
            return

        device_index = self.device_tree.index(selected_item[0])
        if messagebox.askyesno(
            "Confirmar Remoção", "Tem a certeza que deseja remover este dispositivo?"
        ):
            self.inventory_manager.remove_device(device_index)
            self.update_device_list()
            self.app.update_device_list()  # Atualiza outras páginas

    def get_selected_device(self):
        """
        Retorna os dados do dispositivo selecionado na Treeview.

        Returns:
            dict or None: O dicionário do dispositivo selecionado ou None.
        """
        selected_item = self.device_tree.selection()
        if not selected_item:
            return None
        device_index = self.device_tree.index(selected_item[0])
        return self.inventory_manager.get_devices()[device_index]
