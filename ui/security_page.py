"""
Página da interface do utilizador para gerir regras de segurança (ACLs).
"""
from tkinter import ttk, messagebox
from logic.security_manager import get_acls, add_acl_rule

class SecurityPage(ttk.Frame):
    """Frame para a gestão de ACLs."""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.create_widgets()

    def create_widgets(self):
        """Cria os widgets da página."""
        main_frame = ttk.Labelframe(self, text="Construtor de Regras de Firewall / ACL", padding=10)
        main_frame.pack(padx=10, pady=10, fill="x")

        # Seleção da ACL
        ttk.Label(main_frame, text="Adicionar regra para:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.acl_combobox = ttk.Combobox(main_frame, width=30, state="readonly")
        self.acl_combobox.grid(row=0, column=1, columnspan=2, sticky="ew", padx=5, pady=5)

        # Formulário da Regra
        ttk.Label(main_frame, text="Ação:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.action_var = ttk.Combobox(main_frame, values=["permit", "deny", "accept", "drop", "reject"], width=15)
        self.action_var.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        self.action_var.set("permit")

        ttk.Label(main_frame, text="Protocolo:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.proto_var = ttk.Combobox(main_frame, values=["ip", "tcp", "udp", "icmp"], width=15)
        self.proto_var.grid(row=2, column=1, sticky="w", padx=5, pady=2)
        self.proto_var.set("ip")

        ttk.Label(main_frame, text="Origem:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.source_entry = ttk.Entry(main_frame, width=30)
        self.source_entry.grid(row=3, column=1, sticky="w", padx=5, pady=2)
        self.source_entry.insert(0, "any")

        ttk.Label(main_frame, text="Destino:").grid(row=4, column=0, sticky="w", padx=5, pady=2)
        self.dest_entry = ttk.Entry(main_frame, width=30)
        self.dest_entry.grid(row=4, column=1, sticky="w", padx=5, pady=2)
        self.dest_entry.insert(0, "any")
        
        ttk.Label(main_frame, text="Opções:").grid(row=5, column=0, sticky="w", padx=5, pady=2)
        self.options_entry = ttk.Entry(main_frame, width=30)
        self.options_entry.grid(row=5, column=1, sticky="w", padx=5, pady=2)

        # Botão
        add_btn = ttk.Button(main_frame, text="Adicionar Regra", command=self.add_rule_action, bootstyle="primary")
        add_btn.grid(row=6, column=0, columnspan=2, pady=20)

    def refresh(self):
        """Atualiza a lista de ACLs disponíveis."""
        device = self.app.get_selected_device()
        if not device:
            self.acl_combobox['values'] = []
            self.acl_combobox.set("Selecione um dispositivo primeiro")
            return

        acls = get_acls(device)
        self.acl_combobox['values'] = [acl['name'] for acl in acls]
        if acls:
            self.acl_combobox.set(acls[0]['name'])
        else:
            self.acl_combobox.set("Nenhuma ACL encontrada")

    def add_rule_action(self):
        """Chama a lógica para adicionar a regra de ACL."""
        device = self.app.get_selected_device()
        acl_name = self.acl_combobox.get()
        
        if not device or not acl_name or "Nenhuma" in acl_name:
            messagebox.showerror("Erro", "Selecione um dispositivo e uma ACL válida.")
            return

        rule_details = {
            "action": self.action_var.get(), "protocol": self.proto_var.get(),
            "source": self.source_entry.get(), "destination": self.dest_entry.get(),
            "options": self.options_entry.get()
        }
        
        add_acl_rule(device, acl_name, rule_details)