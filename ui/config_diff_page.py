# ui/config_diff_page.py
import tkinter as tk
from tkinter import ttk, scrolledtext
from logic.diff_manager import load_file_into_text_widget, compare_configs

class ConfigDiffPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # --- Frame Principal com 3 colunas ---
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Painel A (Esquerda) ---
        frame_a = ttk.LabelFrame(self, text="Configuração A")
        frame_a.grid(row=0, column=0, padx=10, pady=10, sticky="nsew", rowspan=2)
        frame_a.grid_rowconfigure(1, weight=1)
        frame_a.grid_columnconfigure(0, weight=1)
        
        ttk.Button(frame_a, text="Carregar Ficheiro A...", command=lambda: load_file_into_text_widget(self.text_a)).grid(row=0, column=0, pady=5)
        self.text_a = scrolledtext.ScrolledText(frame_a, wrap=tk.WORD, font=("Consolas", 9))
        self.text_a.grid(row=1, column=0, sticky="nsew")

        # --- Painel B (Direita) ---
        frame_b = ttk.LabelFrame(self, text="Configuração B")
        frame_b.grid(row=0, column=1, padx=10, pady=10, sticky="nsew", rowspan=2)
        frame_b.grid_rowconfigure(1, weight=1)
        frame_b.grid_columnconfigure(0, weight=1)

        ttk.Button(frame_b, text="Carregar Ficheiro B...", command=lambda: load_file_into_text_widget(self.text_b)).grid(row=0, column=0, pady=5)
        self.text_b = scrolledtext.ScrolledText(frame_b, wrap=tk.WORD, font=("Consolas", 9))
        self.text_b.grid(row=1, column=0, sticky="nsew")
        
        # --- Painel de Ação e Resultados (Centro) ---
        center_frame = ttk.Frame(self)
        center_frame.grid(row=0, column=2, rowspan=2, padx=10, pady=10, sticky="nsew")
        center_frame.grid_rowconfigure(1, weight=1)
        center_frame.grid_columnconfigure(0, weight=1)

        ttk.Button(center_frame, text="---> Comparar <---", command=lambda: compare_configs(self.controller)).pack(pady=20)
        
        results_frame = ttk.LabelFrame(center_frame, text="Diferenças")
        results_frame.pack(fill="both", expand=True)
        self.results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, font=("Consolas", 9), state="disabled")
        self.results_text.pack(fill="both", expand=True)