"""
Página da interface do utilizador para a gestão de regras de conformidade.
"""
from tkinter import ttk, messagebox
from logic.compliance_manager import ComplianceManager, check_compliance
# Removi 'tkinter as tk' porque não era usado


class CompliancePage(ttk.Frame):
    """Frame para a gestão e verificação de conformidade."""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.compliance_manager = ComplianceManager()
        self.create_widgets()
        self.load_rules()

    def create_widgets(self):
        """Cria os widgets da página."""
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill="both", expand=True)

        # Frame da lista de regras
        list_frame = ttk.Labelframe(main_frame, text="Regras de Conformidade")
        list_frame.pack(fill="both", expand=True)

        self.rules_tree = ttk.Treeview(
            list_frame, columns=("name", "description"), show="headings"
        )
        self.rules_tree.heading("name", text="Nome da Regra")
        self.rules_tree.heading("description", text="Descrição")
        self.rules_tree.pack(fill="both", expand=True, pady=5)

        # Botões
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill="x")

        check_btn = ttk.Button(
            btn_frame,
            text="Verificar Conformidade",
            command=self.run_check,
            bootstyle="primary",
        )
        check_btn.pack(side="left", padx=5)
        # Futuramente, adicionar botões para Adicionar/Editar/Remover regras

    def load_rules(self):
        """Carrega as regras de conformidade na lista."""
        self.rules_tree.delete(*self.rules_tree.get_children())
        for rule in self.compliance_manager.get_rules():
            self.rules_tree.insert(
                "", "end", values=(rule["name"], rule["description"])
            )

    def run_check(self):
        """
        Executa a verificação de conformidade para a regra e dispositivo selecionados.
        """
        device = self.app.get_selected_device()
        if not device:
            messagebox.showerror("Erro", "Nenhum dispositivo selecionado.")
            return

        selected_item = self.rules_tree.selection()
        if not selected_item:
            messagebox.showerror("Erro", "Nenhuma regra selecionada.")
            return

        rule_index = self.rules_tree.index(selected_item[0])
        rule = self.compliance_manager.get_rules()[rule_index]

        # Chama a função correta
        check_compliance(self.app, device, rule)

    def refresh(self):
        """Atualiza a lista de regras quando a página é exibida."""
        self.load_rules()