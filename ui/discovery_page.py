"""
Página da interface do utilizador para a descoberta de dispositivos na rede.
"""
from tkinter import ttk, messagebox
from ttkbootstrap.scrolled import ScrolledText
from logic.discovery_manager import start_discovery

class DiscoveryPage(ttk.Frame):
    """Frame para a funcionalidade de descoberta de rede."""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.create_widgets()

    def create_widgets(self):
        """Cria os widgets da página."""
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill="both", expand=True)

        # Frame de input
        input_frame = ttk.Labelframe(main_frame, text="Parâmetros de Descoberta", padding=10)
        input_frame.pack(fill="x")

        ttk.Label(input_frame, text="Gama de Rede (ex: 192.168.1.0/24):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.range_entry = ttk.Entry(input_frame, width=30)
        self.range_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Utilizador SSH:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.user_entry = ttk.Entry(input_frame, width=30)
        self.user_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Palavra-passe SSH:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.pass_entry = ttk.Entry(input_frame, show="*", width=30)
        self.pass_entry.grid(row=2, column=1, padx=5, pady=5)

        start_btn = ttk.Button(input_frame, text="Iniciar Descoberta", command=self.run_discovery, bootstyle="primary")
        start_btn.grid(row=1, column=2, rowspan=2, padx=20)

        # Barra de progresso
        self.progress = ttk.Progressbar(main_frame, orient="horizontal", mode="determinate", length=400)
        self.progress.pack(pady=20)

        # Resultado
        output_frame = ttk.Labelframe(main_frame, text="Dispositivos Encontrados (serão adicionados ao inventário)", padding=10)
        output_frame.pack(fill="both", expand=True)
        self.output_text = ScrolledText(output_frame, wrap="word", state="disabled")
        self.output_text.pack(fill="both", expand=True)

    def run_discovery(self):
        """Inicia o processo de descoberta."""
        network_range = self.range_entry.get()
        username = self.user_entry.get()
        password = self.pass_entry.get()

        if not all([network_range, username, password]):
            messagebox.showwarning("Dados em Falta", "Por favor, preencha todos os campos.")
            return

        credentials = {"username": username, "password": password}
        self.progress["value"] = 0
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", f"A iniciar a descoberta na gama {network_range}...\n")
        self.output_text.config(state="disabled")

        # Chama a função de descoberta, passando o gestor de inventário da app
        start_discovery(network_range, credentials, self.app.inventory_manager, self.update_progress, self.on_discovery_complete)

    def update_progress(self, value):
        """Atualiza a barra de progresso."""
        self.progress["value"] = value

    def on_discovery_complete(self):
        """Ações a serem executadas quando a descoberta termina."""
        messagebox.showinfo("Concluído", "Descoberta de rede terminada.")
        self.progress["value"] = 100
        # Atualiza a lista de dispositivos em toda a aplicação
        self.app.update_device_list()