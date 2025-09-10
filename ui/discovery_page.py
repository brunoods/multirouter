# ui/discovery_page.py
import tkinter as tk
from tkinter import ttk, scrolledtext
from logic.discovery_manager import start_discovery

class DiscoveryPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # --- Frame Principal ---
        main_frame = ttk.LabelFrame(self, text="Descoberta Automática de Rede")
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(2, weight=1) # Dá mais espaço ao log

        # --- Frame de Parâmetros ---
        params_frame = ttk.Frame(main_frame)
        params_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(params_frame, text="Gama de Rede (CIDR):").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.network_entry = ttk.Entry(params_frame, width=30)
        self.network_entry.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        self.network_entry.insert(0, "192.168.1.0/24")

        ttk.Label(params_frame, text="Utilizador Comum:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.user_entry = ttk.Entry(params_frame, width=30)
        self.user_entry.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        self.user_entry.insert(0, "admin")
        
        ttk.Label(params_frame, text="Senha Comum:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.pass_entry = ttk.Entry(params_frame, width=30, show="*")
        self.pass_entry.grid(row=2, column=1, sticky="w", padx=5, pady=2)

        # --- Frame de Ação e Progresso ---
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=1, column=0, pady=10)

        self.run_button = ttk.Button(action_frame, text="Iniciar Descoberta", style="primary",  command=lambda: start_discovery(self.controller))
        self.run_button.pack(side="left", padx=10)
        
        self.progress_bar = ttk.Progressbar(action_frame, mode='indeterminate', length=200)
        self.progress_bar.pack(side="left", padx=10)

        # --- Frame do Log de Resultados ---
        log_frame = ttk.LabelFrame(main_frame, text="Log de Descoberta")
        log_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, font=("Consolas", 9), state="disabled", background="#ffffff")
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)