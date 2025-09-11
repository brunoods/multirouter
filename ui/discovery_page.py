import tkinter as tk
from tkinter import ttk, messagebox
from .base_page import BasePage
from logic.inventory_manager import InventoryManager
from logic.discovery_manager import DiscoveryManager

class DiscoveryPage(BasePage):
    def __init__(self, parent, app):
        super().__init__(parent, app, page_title="Descoberta de Rede")

    def create_content(self):
        self.inventory_manager = InventoryManager()
        self.discovery_manager = DiscoveryManager()

        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        input_frame = ttk.Labelframe(main_frame, text="Parâmetros de Descoberta", padding=10)
        input_frame.pack(fill="x")
        input_frame.columnconfigure(1, weight=1)

        ttk.Label(input_frame, text="Gama de Rede (ex: 192.168.1.0/24):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.range_entry = ttk.Entry(input_frame)
        self.range_entry.grid(row=0, column=1, columnspan=2, sticky="ew", padx=5, pady=5)

        ttk.Label(input_frame, text="Utilizador SSH:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.user_entry = ttk.Entry(input_frame)
        self.user_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(input_frame, text="Palavra-passe SSH:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.pass_entry = ttk.Entry(input_frame, show="*")
        self.pass_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        self.start_btn = ttk.Button(input_frame, text="Iniciar Descoberta", command=self.run_discovery, style="primary.TButton")
        self.start_btn.grid(row=1, column=2, rowspan=2, padx=(20, 5), pady=5, sticky="ns")

        self.progress = ttk.Progressbar(main_frame, orient="horizontal", mode="determinate")
        self.progress.pack(fill='x', pady=20, padx=10)

        output_frame = ttk.Labelframe(main_frame, text="Resultados da Descoberta", padding=10)
        output_frame.pack(fill="both", expand=True, padx=10, pady=(0,10))
        self.output_text = tk.Text(output_frame, wrap="word", state="disabled", height=10)
        self.output_text.pack(fill="both", expand=True)

    def run_discovery(self):
        network_range = self.range_entry.get()
        username = self.user_entry.get()
        password = self.pass_entry.get()

        if not all([network_range, username, password]):
            messagebox.showwarning("Dados em Falta", "Por favor, preencha todos os campos.")
            return

        credentials = {"username": username, "password": password}
        
        self.start_btn.config(state="disabled")
        self.progress["value"] = 0
        self.update_output(f"A iniciar a descoberta na gama {network_range}...\n", clear=True)

        self.discovery_manager.start(
            network_range, 
            credentials, 
            self.inventory_manager,
            self.update_progress, 
            self.on_discovery_complete
        )

    def update_progress(self, value):
        self.after(0, lambda: self.progress.config(value=value))

    def on_discovery_complete(self, result):
        self.after(0, self._finalize_discovery, result)

    def _finalize_discovery(self, discovered_devices):
        self.progress["value"] = 100
        self.start_btn.config(state="normal")
        
        if isinstance(discovered_devices, str):
            messagebox.showerror("Erro na Descoberta", discovered_devices)
            self.update_output(f"\n{discovered_devices}")
        elif discovered_devices:
            self.update_output("\n--- Dispositivos Descobertos e Adicionados ---\n")
            for dev in discovered_devices:
                self.update_output(f"- {dev['name']} ({dev['ip']}) do tipo {dev['type']}\n")
            messagebox.showinfo("Concluído", f"{len(discovered_devices)} novo(s) dispositivo(s) encontrado(s) e adicionado(s) ao inventário.")
        else:
            self.update_output("\nNenhum novo dispositivo foi encontrado.")
            messagebox.showinfo("Concluído", "A descoberta terminou, mas nenhum novo dispositivo foi encontrado.")
            
        if "Inventário" in self.app.pages:
            self.app.pages["Inventário"].refresh()

    def update_output(self, text, clear=False):
        self.output_text.config(state="normal")
        if clear:
            self.output_text.delete("1.0", "end")
        self.output_text.insert("end", text)
        self.output_text.see("end")
        self.output_text.config(state="disabled")