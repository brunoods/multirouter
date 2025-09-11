"""
Página da interface do utilizador para a gestão de alertas.
"""
from tkinter import ttk, messagebox
from logic.alerts_manager import AlertsManager
# Removi a importação não utilizada de 'tkinter as tk'

class AlertsPage(ttk.Frame):
    """Frame para a gestão e visualização de alertas."""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.alerts_manager = AlertsManager()
        self.create_widgets()
        self.load_alerts()

    def create_widgets(self):
        """Cria os widgets da página de alertas."""
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill="both", expand=True)

        # Frame da lista de alertas
        list_frame = ttk.Labelframe(main_frame, text="Alertas Configurados")
        list_frame.pack(fill="both", expand=True)

        self.alerts_tree = ttk.Treeview(
            list_frame,
            columns=("name", "type", "device"),
            show="headings"
        )
        self.alerts_tree.heading("name", text="Nome do Alerta")
        self.alerts_tree.heading("type", text="Tipo")
        self.alerts_tree.heading("device", text="Dispositivo")
        self.alerts_tree.pack(fill="both", expand=True, pady=5)

        # Botões
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill="x")

        # No futuro, podemos adicionar aqui formulários para
        # criar e editar alertas de forma mais detalhada.
        add_btn = ttk.Button(
            btn_frame, text="Adicionar (Exemplo)",
            command=self.add_alert, bootstyle="success"
        )
        add_btn.pack(side="left", padx=5)

        remove_btn = ttk.Button(
            btn_frame, text="Remover",
            command=self.remove_alert, bootstyle="danger"
        )
        remove_btn.pack(side="left", padx=5)

    def load_alerts(self):
        """Carrega os alertas do gestor e exibe-os na lista."""
        self.alerts_tree.delete(*self.alerts_tree.get_children())
        for alert in self.alerts_manager.get_alerts():
            self.alerts_tree.insert(
                "", "end",
                values=(alert["name"], alert["type"], alert["device"])
            )

    def add_alert(self):
        """Adiciona um novo alerta de exemplo."""
        # Esta é uma implementação simplificada.
        # O ideal seria abrir um formulário como na página de inventário.
        new_alert = {
            "name": "Alerta de Interface Down",
            "type": "Status da Interface",
            "device": "192.168.1.1",
            "condition": "status != up"
        }
        self.alerts_manager.add_alert(new_alert)
        self.load_alerts()
        messagebox.showinfo("Sucesso", "Alerta de exemplo adicionado.")

    def remove_alert(self):
        """Remove o alerta selecionado."""
        selected_item = self.alerts_tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um alerta para remover.")
            return

        if messagebox.askyesno("Confirmar", "Tem a certeza que deseja remover este alerta?"):
            index = self.alerts_tree.index(selected_item[0])
            self.alerts_manager.delete_alert(index)
            self.load_alerts()

    def refresh(self):
        """Atualiza a lista de alertas quando a página é mostrada."""
        self.load_alerts()