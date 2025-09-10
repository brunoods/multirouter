# ui/security_page.py
import tkinter as tk
from tkinter import ttk
from logic.configuration import add_acl_rule

class SecurityPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # --- Frame Principal ---
        main_frame = ttk.LabelFrame(self, text="Construtor de Regras de Firewall / ACL")
        main_frame.pack(padx=20, pady=20, fill="x", anchor="n")

        # --- Seleção da ACL ---
        ttk.Label(main_frame, text="Adicionar regra para:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.selected_acl = tk.StringVar()
        self.acl_combobox = ttk.Combobox(main_frame, textvariable=self.selected_acl, width=30, state="readonly")
        self.acl_combobox.grid(row=0, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
        self.acl_combobox.set("Selecione uma ACL...")

        # --- Formulário da Regra ---
        rule_frame = ttk.Frame(main_frame)
        rule_frame.grid(row=1, column=0, columnspan=3, pady=10)
        
        ttk.Label(rule_frame, text="Ação:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.action_var = tk.StringVar()
        action_cb = ttk.Combobox(rule_frame, textvariable=self.action_var, values=["permit", "deny", "accept", "drop"], width=15)
        action_cb.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        action_cb.set("permit")

        ttk.Label(rule_frame, text="Protocolo:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.proto_var = tk.StringVar()
        proto_cb = ttk.Combobox(rule_frame, textvariable=self.proto_var, values=["ip", "tcp", "udp", "icmp"], width=15)
        proto_cb.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        proto_cb.set("ip")

        ttk.Label(rule_frame, text="Origem (IP/Rede):").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.source_entry = ttk.Entry(rule_frame, width=30)
        self.source_entry.grid(row=2, column=1, sticky="w", padx=5, pady=2)
        self.source_entry.insert(0, "any")

        ttk.Label(rule_frame, text="Destino (IP/Rede):").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.dest_entry = ttk.Entry(rule_frame, width=30)
        self.dest_entry.grid(row=3, column=1, sticky="w", padx=5, pady=2)
        self.dest_entry.insert(0, "any")

        ttk.Label(rule_frame, text="Opções (ex: eq 80):").grid(row=4, column=0, sticky="w", padx=5, pady=2)
        self.options_entry = ttk.Entry(rule_frame, width=30)
        self.options_entry.grid(row=4, column=1, sticky="w", padx=5, pady=2)
        
        # --- Botão de Ação ---
        ttk.Button(main_frame, text="Adicionar Regra", style="primary",  command=lambda: add_acl_rule(self.controller)).grid(row=2, column=0, columnspan=3, pady=20)