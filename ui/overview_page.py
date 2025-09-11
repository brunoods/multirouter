"""
Página de Visão Geral (Dashboard) da aplicação.
"""

from tkinter import ttk
from ttkbootstrap.scrolled import ScrolledText


class OverviewPage(ttk.Frame):
    """Frame que exibe o dashboard principal da aplicação."""

    def __init__(self, parent, app):
        """
        Inicializa a página de visão geral.

        Args:
            parent: O widget pai.
            app: A instância principal da aplicação.
        """
        super().__init__(parent)
        self.app = app

        self.create_widgets()

    def create_widgets(self):
        """Cria os widgets da página."""
        # Frame para o status
        status_frame = ttk.Labelframe(self, text="Status do Dispositivo", padding=10)
        status_frame.pack(fill="x", padx=10, pady=10)

        self.status_label = ttk.Label(
            status_frame, text="Nenhum dispositivo selecionado"
        )
        self.status_label.pack(side="left", padx=5)

        self.connection_status_label = ttk.Label(
            status_frame, text="Não conectado", bootstyle="danger"
        )
        self.connection_status_label.pack(side="left", padx=5)

        # Frame para a exibição da configuração
        config_frame = ttk.Labelframe(
            self, text="Visualizador de Configuração", padding=10
        )
        config_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.config_text = ScrolledText(
            config_frame, wrap="word", height=20, state="disabled"
        )
        self.config_text.pack(fill="both", expand=True)

        # Frame para o monitoramento
        monitoring_frame = ttk.Labelframe(self, text="Monitorização", padding=10)
        monitoring_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.monitoring_label = ttk.Label(
            monitoring_frame, text="A monitorização não está ativa."
        )
        self.monitoring_label.pack()

    def update_connection_status_label(self, status):
        """
        Atualiza a label de status da conexão.

        Args:
            status (str): O novo status da conexão (ex: "Conectado").
        """
        self.connection_status_label.config(text=status)
        if status == "Conectado":
            self.connection_status_label.config(bootstyle="success")
        else:
            self.connection_status_label.config(bootstyle="danger")

    def update_config_display(self, config):
        """
        Exibe a configuração do dispositivo no widget de texto.

        Args:
            config (str): A configuração a ser exibida.
        """
        self.config_text.config(state="normal")
        self.config_text.delete("1.0", "end")
        self.config_text.insert("1.0", config)
        self.config_text.config(state="disabled")

    def update_monitoring_status(self, status_list):
        """
        Atualiza a área de monitorização com o status dos dispositivos.

        Args:
            status_list (list): Uma lista de strings com o status de cada dispositivo.
        """
        status_text = "\n".join(status_list)
        self.monitoring_label.config(text=status_text)

    def refresh(self):
        """Atualiza a página quando ela é exibida."""
        device = self.app.get_selected_device()
        if device:
            self.status_label.config(text=f"Dispositivo: {device.get('ip')}")
            status = self.app.logic.connection.get_connection_status(device)
            self.update_connection_status_label(status)
        else:
            self.status_label.config(text="Nenhum dispositivo selecionado")
            self.update_connection_status_label("Não conectado")
