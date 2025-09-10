# ui/templates_page.py
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from logic.templates_manager import (load_templates, save_single_template, 
                                     delete_template, find_variables_in_template,
                                     render_template)
from logic.configuration import send_commands
from ui.template_form import TemplateForm

class TemplatesPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # --- Estrutura Principal ---
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        # --- Painel Esquerdo: Lista de Templates e Ações ---
        left_frame = ttk.Frame(self)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        left_frame.grid_rowconfigure(1, weight=1)

        ttk.Label(left_frame, text="Templates Salvos", font=('Segoe UI', 11, 'bold')).grid(row=0, column=0, sticky="w")
        
        self.template_list = tk.Listbox(left_frame, height=15)
        self.template_list.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=5)
        self.template_list.bind("<<ListboxSelect>>", self.on_template_select)

        ttk.Button(left_frame, text="Novo", style="primary",  command=self.new_template).grid(row=2, column=0, sticky="ew", pady=5, padx=(0,2))
        ttk.Button(left_frame, text="Remover", style="danger",  command=self.delete_selected_template).grid(row=2, column=1, sticky="ew", pady=5, padx=(2,0))

        # --- Painel Direito: Editor e Ações do Template ---
        right_frame = ttk.Frame(self)
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        editor_header = ttk.Frame(right_frame)
        editor_header.grid(row=0, column=0, columnspan=2, sticky="ew")
        ttk.Label(editor_header, text="Nome do Template:").pack(side="left")
        self.template_name_entry = ttk.Entry(editor_header, width=40)
        self.template_name_entry.pack(side="left", padx=5)

        self.editor_text = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, font=("Consolas", 10))
        self.editor_text.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=5)

        ttk.Button(right_frame, text="Salvar Template", style="primary",  command=self.save_current_template).grid(row=2, column=0, sticky="e", pady=10)
        ttk.Button(right_frame, text="Aplicar Template ao Dispositivo...", style="primary",  command=self.apply_template).grid(row=2, column=1, sticky="w", pady=10, padx=10)

        self.populate_template_list()

    def populate_template_list(self):
        self.templates = load_templates()
        self.template_list.delete(0, tk.END)
        for template in self.templates:
            self.template_list.insert(tk.END, template['name'])

    def on_template_select(self, event):
        selection_indices = self.template_list.curselection()
        if not selection_indices: return
        
        selected_index = selection_indices[0]
        selected_template = self.templates[selected_index]
        
        self.template_name_entry.delete(0, tk.END)
        self.template_name_entry.insert(0, selected_template['name'])
        
        self.editor_text.delete('1.0', tk.END)
        self.editor_text.insert('1.0', selected_template['content'])

    def new_template(self):
        self.template_list.selection_clear(0, tk.END)
        self.template_name_entry.delete(0, tk.END)
        self.editor_text.delete('1.0', tk.END)
        self.template_name_entry.focus()

    def save_current_template(self):
        name = self.template_name_entry.get().strip()
        content = self.editor_text.get('1.0', 'end-1c').strip()
        if not name or not content:
            messagebox.showwarning("Dados Incompletos", "O nome e o conteúdo do template não podem estar vazios.", parent=self)
            return
        
        save_single_template(name, content)
        self.populate_template_list()
        messagebox.showinfo("Sucesso", f"Template '{name}' salvo com sucesso.", parent=self)
        
    def delete_selected_template(self):
        selection_indices = self.template_list.curselection()
        if not selection_indices:
            messagebox.showwarning("Nenhuma Seleção", "Selecione um template para remover.", parent=self)
            return

        selected_template_name = self.template_list.get(selection_indices[0])
        if messagebox.askyesno("Confirmar Remoção", f"Tem a certeza que deseja remover o template '{selected_template_name}'?", parent=self):
            delete_template(selected_template_name)
            self.populate_template_list()
            self.new_template()

    def apply_template(self):
        content = self.editor_text.get('1.0', 'end-1c')
        variables = find_variables_in_template(content)

        if not variables:
            # Se não houver variáveis, aplica diretamente
            commands = [cmd for cmd in content.splitlines() if cmd.strip() and not cmd.strip().startswith('!')]
            send_commands(self.controller, commands, "Template sem variáveis aplicado com sucesso.")
            return

        # Abre o formulário dinâmico para preencher as variáveis
        form = TemplateForm(self, variables)
        self.wait_window(form)
        
        if form.result:
            rendered_content = render_template(content, form.result)
            commands = [cmd for cmd in rendered_content.splitlines() if cmd.strip() and not cmd.strip().startswith('!')]
            send_commands(self.controller, commands, "Template aplicado com sucesso.")