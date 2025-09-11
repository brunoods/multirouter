import tkinter as tk
from tkinter import ttk, messagebox
from .base_page import BasePage
from logic.inventory_manager import InventoryManager
from logic.mass_commands import MassCommands

class MassCommandsPage(BasePage):
    def __init__(self, parent, app):
        super().__init__(parent, app, page_title="Comandos em Massa")

    def create_content(self):
        self.inventory_manager = InventoryManager()
        self.mass_commands = MassCommands()

        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        devices_frame = ttk.Labelframe(main_frame, text="Dispositivos", padding=10)
        devices_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.device_listbox = tk.Listbox(devices_frame, selectmode=tk.MULTIPLE)
        self.device_listbox.pack(fill=tk.BOTH, expand=True)
        
        commands_frame = ttk.Frame(main_frame)
        commands_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        command_input_frame = ttk.Labelframe(commands_frame, text="Comandos (um por linha)", padding=10)
        command_input_frame.pack(fill=tk.X)

        self.command_text = tk.Text(command_input_frame, height=5)
        self.command_text.pack(fill=tk.X, expand=True)

        self.execute_button = ttk.Button(command_input_frame, text="Executar", command=self.execute_commands, style='primary.TButton')
        self.execute_button.pack(pady=5)
        
        self.progress_bar = ttk.Progressbar(command_input_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=(5,0))

        results_frame = ttk.Labelframe(commands_frame, text="Resultados", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.results_text = tk.Text(results_frame, state=tk.DISABLED, wrap=tk.WORD)
        self.results_text.pack(fill=tk.BOTH, expand=True)

        self.refresh()

    def refresh(self):
        self.device_listbox.delete(0, tk.END)
        devices = self.inventory_manager.get_devices()
        for device in devices:
            self.device_listbox.insert(tk.END, f"{device['name']} ({device['ip']})")

    def execute_commands(self):
        selected_indices = self.device_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Aviso", "Selecione pelo menos um dispositivo.")
            return

        commands_str = self.command_text.get("1.0", tk.END).strip()
        if not commands_str:
            messagebox.showwarning("Aviso", "Insira pelo menos um comando.")
            return
        
        commands_list = commands_str.split('\n')

        all_devices = self.inventory_manager.get_devices()
        selected_devices = [all_devices[i] for i in selected_indices]
        
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)
        self.results_text.config(state=tk.DISABLED)
        
        self.execute_button.config(state=tk.DISABLED)
        self.progress_bar.start()

        self.mass_commands.execute(
            selected_devices,
            commands_list,
            ui_update_callback=self.update_results,
            completion_callback=self.on_complete
        )

    def update_results(self, output):
        self.after(0, self._append_to_results, output)

    def _append_to_results(self, output):
        self.results_text.config(state=tk.NORMAL)
        self.results_text.insert(tk.END, output)
        self.results_text.see(tk.END)
        self.results_text.config(state=tk.DISABLED)

    def on_complete(self):
        self.after(0, self._finalize_execution)
        
    def _finalize_execution(self):
        self.progress_bar.stop()
        self.execute_button.config(state=tk.NORMAL)
        self._append_to_results("\n--- Execução Concluída ---")