# logic/templates_manager.py
"""
Módulo para gerir os templates de configuração.
"""
import json
import re
from tkinter import messagebox

TEMPLATES_FILE = "templates.json"

def load_templates():
    """Carrega os templates do ficheiro JSON."""
    try:
        with open(TEMPLATES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        messagebox.showerror("Erro de Templates", f"O ficheiro {TEMPLATES_FILE} está corrompido.")
        return []

def save_templates(templates):
    """Salva a lista de templates no ficheiro JSON."""
    try:
        with open(TEMPLATES_FILE, 'w', encoding='utf-8') as f:
            json.dump(templates, f, indent=4)
    except Exception as e:
        messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar os templates: {e}")

def save_single_template(template_name, template_content):
    """Adiciona ou atualiza um template específico."""
    templates = load_templates()
    # Verifica se o template já existe para atualização
    found = False
    for i, template in enumerate(templates):
        if template['name'] == template_name:
            templates[i]['content'] = template_content
            found = True
            break
    if not found:
        templates.append({'name': template_name, 'content': template_content})
    
    save_templates(templates)

def delete_template(template_name):
    """Remove um template pelo nome."""
    templates = load_templates()
    templates = [t for t in templates if t['name'] != template_name]
    save_templates(templates)

def find_variables_in_template(content):
    """Encontra todas as variáveis no formato {{variavel}} no texto."""
    # A regex r"\{\{ *(\w+) *\}\}" encontra {{variavel}} com ou sem espaços
    return sorted(list(set(re.findall(r"\{\{ *(\w+) *\}\}", content))))

def render_template(content, variables_map):
    """Substitui as variáveis no template pelos valores fornecidos."""
    rendered_content = content
    for var_name, var_value in variables_map.items():
        rendered_content = rendered_content.replace(f"{{{{ {var_name} }}}}", var_value)
        rendered_content = rendered_content.replace(f"{{{{{var_name}}}}}", var_value)
    return rendered_content