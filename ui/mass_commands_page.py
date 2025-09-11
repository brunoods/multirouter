"""
Página da interface para execução de comandos em massa.
"""

from tkinter import ttk
from ttkbootstrap.scrolled import ScrolledText
from logic.mass_commands import run_mass_commands


class MassCommandsPage(ttk.Frame):
    """Frame para a funcionalidade de comandos em massa."""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.create_widgets()

    def create_widgets(self):
        """Cria os widgets da página."""
        # Frame para a lista de dispositivos e comandos
        input_frame = ttk.Frame(self)
        input_frame.pack(fill="x", padx=10, pady=10)

        # Treeview para selecionar dispositivos
        self.device_tree = ttk.Treeview(
            input_frame, columns=("ip",), show="headings", height=5
        )
        self.device_tree.heading("ip", text="Selecionar Dispositivos")
        self.device_tree.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Área de texto para os comandos
        self.command_text = ScrolledText(input_frame, wrap="word", height=5)
        self.command_text.pack(side="left", fill="both", expand=True)

        # Botão para executar
        run_btn = ttk.Button(
            self, text="Executar Comandos", command=self.execute, bootstyle="primary"
        )
        run_btn.pack(pady=5)

        # Barra de progresso
        self.progress = ttk.Progressbar(
            self, orient="horizontal", mode="determinate", length=300
        )
        self.progress.pack(pady=5)

        # Área de texto para o resultado
        output_frame = ttk.Labelframe(self, text="Resultado", padding=10)
        output_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.output_text = ScrolledText(output_frame, wrap="word")
        self.output_text.pack(fill="both", expand=True)

    def update_device_list(self, devices):
        """Atualiza a lista de dispositivos na Treeview."""
        self.device_tree.delete(*self.device_tree.get_children())
        for device in devices:
            self.device_tree.insert("", "end", values=(device["ip"],))

    def execute(self):
        """Inicia a execução dos comandos em massa."""
        selected_items = self.device_tree.selection()
        if not selected_items:
            self.update_output("Nenhum dispositivo selecionado.\n")
            return

        all_devices = self.app.inventory_manager.get_devices()
        selected_ips = {
            self.device_tree.item(item)["values"][0] for item in selected_items
        }

        selected_devices = [dev for dev in all_devices if dev["ip"] in selected_ips]

        commands = self.command_text.get("1.0", "end-1c")

        self.output_text.delete("1.0", "end")
        self.progress["value"] = 0

        run_mass_commands(
            selected_devices, commands, self, self.update_progress, self.on_complete
        )

    def update_output(self, data):
        """Adiciona texto à área de resultado."""
        self.output_text.insert("end", data)
        self.output_text.see("end")

    def update_progress(self, value):
        """Atualiza a barra de progresso."""
        self.progress["value"] = value

    def on_complete(self):
        """Chamado quando a execução termina."""
        self.update_output("\n--- Execução Concluída ---\n")
        self.progress["value"] = 100
