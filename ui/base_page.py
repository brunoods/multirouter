import tkinter as tk
from tkinter import ttk

class BasePage(ttk.Frame):
    def __init__(self, parent, app, page_title=""):
        super().__init__(parent)
        self.app = app
        self.page_title = page_title
        
        self._create_header()
        self.create_content() # Este método será implementado nas classes filhas

    def _create_header(self):
        header_frame = ttk.Frame(self, style='secondary.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 10), ipady=5)
        
        header_label = ttk.Label(
            header_frame, 
            text=self.page_title, 
            font=("Helvetica", 16, "bold"),
            style='inverse-secondary.TLabel'
        )
        header_label.pack(pady=10)

    def create_content(self):
        # Este método deve ser sobrescrito pelas classes que herdam de BasePage
        # para adicionar o conteúdo específico de cada página.
        pass