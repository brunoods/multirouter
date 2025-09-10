# ui/alerts_page.py
import tkinter as tk
from tkinter import ttk, messagebox
from logic.alerts_manager import load_alert_rules, add_alert_rule, remove_alert_rule

class AlertsPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        creation_frame = ttk.LabelFrame(main_frame, text="Nova Regra de Alerta: Interface Offline")
        creation_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")

        ttk.Label(creation_frame, text="Dispositivo:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.device_combobox = ttk.Combobox(creation_frame, state="readonly", width=25)
        self.device_combobox.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.device_combobox.bind("<<ComboboxSelected>>", self.on_device_select)

        ttk.Label(creation_frame, text="Interface:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.interface_combobox = ttk.Combobox(creation_frame, state="readonly", width=25)
        self.interface_combobox.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        ttk.Button(creation_frame, text="Adicionar Regra", style="primary", command=self.save_rule).grid(row=2, column=0, columnspan=2, pady=10)

        rules_frame = ttk.LabelFrame(main_frame, text="Regras de Alerta Ativas")
        rules_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="nsew")
        rules_frame.grid_rowconfigure(0, weight=1)
        rules_frame.grid_columnconfigure(0, weight=1)
        
        cols = ("Dispositivo", "Métrica", "Detalhes")
        self.tree = ttk.Treeview(rules_frame, columns=cols, show="headings", selectmode="browse")
        for col in cols: self.tree.heading(col, text=col)
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(rules_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        ttk.Button(main_frame, text="Remover Regra Selecionada", style="danger", command=self.delete_rule).grid(row=2, column=0, pady=10)

    def on_device_select(self, event=None):
        selected_device_name = self.device_combobox.get()
        if not selected_device_name: return
        
        # A lógica para obter as interfaces de um dispositivo específico precisaria
        # de uma conexão. Para simplificar, usaremos as últimas interfaces lidas.
        overview_page = self.controller.frames[self.controller.pages["OverviewPage"]]
        interfaces = [overview_page.interfaces_tree.item(i, "values")[0] for i in overview_page.interfaces_tree.get_children()]
        self.interface_combobox['values'] = interfaces
        if interfaces:
            self.interface_combobox.set(interfaces[0])

    def save_rule(self):
        selected_device_name = self.device_combobox.get()
        selected_interface = self.interface_combobox.get()
        
        if not selected_device_name or not selected_interface:
            messagebox.showwarning("Dados Incompletos", "Por favor, selecione um dispositivo e uma interface.", parent=self)
            return
            
        device = next((d for d in self.controller.inventory if d['name'] == selected_device_name), None)
        if not device: return

        rule = {
            "device_id": device['id'],
            "device_name": device['name'],
            "metric": "Interface Status",
            "interface_name": selected_interface,
            "condition": "not equals",
            "value": "up" # Queremos ser alertados se o estado NÃO for 'up'
        }
        add_alert_rule(rule)
        self.populate_rules()

    def delete_rule(self):
        selected_iid = self.tree.focus()
        if not selected_iid:
            messagebox.showwarning("Nenhuma Seleção", "Por favor, selecione uma regra para remover.", parent=self)
            return
        
        if messagebox.askyesno("Confirmar Remoção", "Tem a certeza que deseja remover esta regra de alerta?", parent=self):
            remove_alert_rule(int(selected_iid))
            self.populate_rules()

    def populate_rules(self):
        """Carrega e exibe as regras de alerta salvas."""
        for i in self.tree.get_children(): self.tree.delete(i)
        
        rules = load_alert_rules()
        for rule in rules:
            details = f"Interface: {rule['interface_name']}, Condição: Estado != '{rule['value']}'"
            self.tree.insert("", "end", iid=rule['id'], values=(rule['device_name'], rule['metric'], details))