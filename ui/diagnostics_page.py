"""
Página da interface do utilizador para as ferramentas de diagnóstico.
"""
from tkinter import ttk, messagebox
from ttkbootstrap.scrolled import ScrolledText
from logic.diagnostics import run_ping, run_traceroute


class DiagnosticsPage(ttk.Frame):
    """Frame que contém os widgets para ping e traceroute."""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.create_widgets()

    def create_widgets(self):
        """Cria os widgets da página."""
        # Frame de input
        input_frame = ttk.Frame(self)
        input_frame.pack(fill="x", padx=10, pady=10)

        ip_label = ttk.Label(input_frame, text="Endereço IP:")
        ip_label.pack(side="left", padx=(0, 5))

        self.ip_entry = ttk.Entry(input_frame, width=30)
        self.ip_entry.pack(side="left", padx=5)

        ping_btn = ttk.Button(input_frame, text="Ping", command=self.do_ping)
        ping_btn.pack(side="left", padx=5)

        traceroute_btn = ttk.Button(
            input_frame, text="Traceroute", command=self.do_traceroute
        )
        traceroute_btn.pack(side="left", padx=5)

        # Frame para o resultado
        output_frame = ttk.Labelframe(self, text="Resultado", padding=10)
        output_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.output_text = ScrolledText(output_frame, wrap="word", state="disabled")
        self.output_text.pack(fill="both", expand=True)

    def do_ping(self):
        """Executa a função de ping."""
        ip = self.ip_entry.get()
        if not ip:
            messagebox.showwarning("IP em falta", "Por favor, insira um endereço IP.")
            return

        self.clear_output()
        self.update_output(f"A executar ping para {ip}...\n\n")
        run_ping(ip, self.update_output)

    def do_traceroute(self):
        """Executa a função de traceroute."""
        ip = self.ip_entry.get()
        if not ip:
            messagebox.showwarning("IP em falta", "Por favor, insira um endereço IP.")
            return

        self.clear_output()
        self.update_output(f"A executar traceroute para {ip}...\n\n")
        run_traceroute(ip, self.update_output)

    def update_output(self, data):
        """Atualiza a área de texto com o resultado."""
        self.output_text.config(state="normal")
        self.output_text.insert("end", data)
        self.output_text.config(state="disabled")
        self.output_text.see("end")

    def clear_output(self):
        """Limpa a área de texto do resultado."""
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.config(state="disabled")