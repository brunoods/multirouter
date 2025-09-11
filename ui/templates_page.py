"""
Página da interface do utilizador para gerir e aplicar templates de configuração.
"""
from tkinter import ttk, messagebox, simpledialog
from ttkbootstrap.scrolled import ScrolledText
from logic.templates_manager import TemplatesManager, apply_template_to_device
from .template_form import TemplateForm
import re


class TemplatesPage(ttk.Frame):
    """Frame para a gestão de templates."""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.templates_manager = TemplatesManager()
        self.create_widgets()
        self.load_templates()

    def create_widgets(self):
        """Cria os widgets da página."""
        # Frame principal
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill="both", expand=True)

        # Frame da lista de templates
        list_frame = ttk.Labelframe(main_frame, text="Templates Guardados")
        list_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.template_listbox = ttk.Treeview(
            list_frame, columns=("name",), show="headings"
        )
        self.template_listbox.heading("name", text="Nome do Template")
        self.template_listbox.pack(fill="both", expand=True)
        self.template_listbox.bind("<<TreeviewSelect>>", self.on_template_select)

        # Frame de botões para a lista
        list_btn_frame = ttk.Frame(list_frame)
        list_btn_frame.pack(fill="x", pady=5)
        
        add_btn = ttk.Button(list_btn_frame, text="Adicionar", command=self.add_template, bootstyle="success")
        add_btn.pack(side="left", padx=5)

        edit_btn = ttk.Button(list_btn_frame, text="Editar", command=self.edit_template, bootstyle="info")
        edit_btn.pack(side="left", padx=5)

        delete_btn = ttk.Button(list_btn_frame, text="Apagar", command=self.delete_template, bootstyle="danger")
        delete_btn.pack(side="left", padx=5)
        
        # Frame do editor de template
        editor_frame = ttk.Labelframe(main_frame, text="Conteúdo do Template")
        editor_frame.pack(side="left", fill="both", expand=True)
        
        self.template_content = ScrolledText(editor_frame, wrap="word", height=15)
        self.template_content.pack(fill="both", expand=True)
        
        # Botão para aplicar o template
        apply_btn = ttk.Button(main_frame, text="Aplicar Template ao Dispositivo", command=self.apply_template)
        apply_btn.pack(pady=10, fill="x")

    def load_templates(self):
        """Carrega os templates para a lista."""
        self.template_listbox.delete(*self.template_listbox.get_children())
        for template in self.templates_manager.get_templates():
            self.template_listbox.insert("", "end", values=(template["name"],))

    def on_template_select(self, event):
        """Exibe o conteúdo do template selecionado."""
        selected_item = self.template_listbox.selection()
        if not selected_item:
            return
            
        index = self.template_listbox.index(selected_item[0])
        template = self.templates_manager.get_templates()[index]
        self.template_content.delete("1.0", "end")
        self.template_content.insert("1.0", template["content"])

    def add_template(self):
        """Abre o formulário para adicionar um novo template."""
        TemplateForm(self, self.app, title="Adicionar Template")

    def edit_template(self):
        """Abre o formulário para editar o template selecionado."""
        selected_item = self.template_listbox.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um template para editar.")
            return

        index = self.template_listbox.index(selected_item[0])
        template = self.templates_manager.get_templates()[index]
        TemplateForm(self, self.app, template=template, template_index=index, title="Editar Template")

    def delete_template(self):
        """Apaga o template selecionado."""
        selected_item = self.template_listbox.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um template para apagar.")
            return
        
        if messagebox.askyesno("Confirmar", "Tem a certeza que deseja apagar este template?"):
            index = self.template_listbox.index(selected_item[0])
            self.templates_manager.delete_template(index)
            self.load_templates()
            self.template_content.delete("1.0", "end")

    def apply_template(self):
        """Aplica o template selecionado ao dispositivo selecionado."""
        device = self.app.get_selected_device()
        if not device:
            messagebox.showerror("Erro", "Nenhum dispositivo selecionado.")
            return

        content = self.template_content.get("1.0", "end-1c")
        if not content:
            messagebox.showerror("Erro", "O conteúdo do template está vazio.")
            return

        # Encontra todas as variáveis no formato {{variavel}}
        variables_needed = set(re.findall(r"\{\{(.*?)\}\}", content))
        
        variables_values = {}
        for var in variables_needed:
            value = simpledialog.askstring("Input", f"Insira o valor para a variável '{var}':", parent=self)
            if value is None: # O utilizador cancelou
                return
            variables_values[var] = value
        
        # Chama a função correta do gestor de templates
        apply_template_to_device(device, content, variables_values)