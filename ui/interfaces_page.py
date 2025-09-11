"""
Página da interface do utilizador para visualizar e gerir interfaces de rede.
"""
from tkinter import ttk, messagebox
from logic.interface_manager import get_device_interfaces


class InterfacesPage(ttk.Frame):
    """Frame que exibe a lista de interfaces do dispositivo selecionado."""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.create_widgets()

    def create_widgets(self):
        """Cria os widgets da página."""
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill="both", expand=True)

        # Botão de refresh
        refresh_btn = ttk.Button(
            main_frame, text="Atualizar Lista de Interfaces", command=self.refresh
        )
        refresh_btn.pack(pady=(0, 10))

        # Treeview para exibir as interfaces
        self.interfaces_tree = ttk.Treeview(
            main_frame,
            columns=("interface", "ip_address", "status", "protocol"),
            show="headings",
        )
        self.interfaces_tree.heading("interface", text="Interface")
        self.interfaces_tree.heading("ip_address", text="Endereço IP")
        self.interfaces_tree.heading("status", text="Status")
        self.interfaces_tree.heading("protocol", text="Protocolo")

        # Ajustar a largura das colunas
        self.interfaces_tree.column("interface", width=150)
        self.interfaces_tree.column("ip_address", width=150)
        self.interfaces_tree.column("status", width=100, anchor="center")
        self.interfaces_tree.column("protocol", width=100, anchor="center")

        self.interfaces_tree.pack(fill="both", expand=True)

    def refresh(self):
        """Busca e exibe as interfaces do dispositivo selecionado."""
        # Limpa a lista atual
        for item in self.interfaces_tree.get_children():
            self.interfaces_tree.delete(item)

        device = self.app.get_selected_device()
        if not device:
            messagebox.showinfo("Aviso", "Por favor, selecione um dispositivo na página de Inventário.")
            return

        interfaces = get_device_interfaces(device)

        if not interfaces:
            messagebox.showinfo("Informação", "Nenhuma interface encontrada ou ocorreu um erro.")
            return

        # Preenche a lista com as novas interfaces
        for interface_data in interfaces:
            self.interfaces_tree.insert(
                "",
                "end",
                values=(
                    interface_data.get("interface", "N/A"),
                    interface_data.get("ip_address", "N/A"),
                    interface_data.get("status", "N/A"),
                    interface_data.get("protocol", "N/A"),
                ),
            )