"""
Gere os templates de configuração, incluindo criação, gestão e aplicação.
"""
import json
import os
import logging
from tkinter import messagebox
from logic.connection import get_connection


class TemplatesManager:
    """Gere as operações de CRUD para os templates."""

    def __init__(self, filename="templates.json"):
        self.filename = filename
        self.templates = self._load_templates()

    def _load_templates(self):
        """Carrega os templates do ficheiro JSON."""
        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                return json.load(f)
        return []

    def _save_templates(self):
        """Guarda os templates no ficheiro JSON."""
        with open(self.filename, "w") as f:
            json.dump(self.templates, f, indent=4)

    def add_template(self, template):
        """Adiciona um novo template."""
        self.templates.append(template)
        self._save_templates()

    def get_templates(self):
        """Retorna todos os templates."""
        return self.templates

    def update_template(self, index, updated_template):
        """Atualiza um template existente."""
        if 0 <= index < len(self.templates):
            self.templates[index] = updated_template
            self._save_templates()

    def delete_template(self, index):
        """Apaga um template."""
        if 0 <= index < len(self.templates):
            del self.templates[index]
            self._save_templates()


def apply_template_to_device(device, template_content, variables):
    """
    Aplica um template de configuração a um dispositivo.

    Args:
        device (dict): O dispositivo ao qual aplicar o template.
        template_content (str): O conteúdo do template com placeholders.
        variables (dict): Um dicionário com as variáveis para substituir.
    """
    connection = get_connection(device)
    if not connection:
        messagebox.showerror("Erro de Conexão", f"Não foi possível conectar-se a {device.get('ip')}.")
        logging.error(f"Tentativa de aplicar template sem conexão a {device.get('ip')}.")
        return

    # Substitui as variáveis no template
    rendered_config = template_content
    for key, value in variables.items():
        placeholder = "{{" + key + "}}"
        rendered_config = rendered_config.replace(placeholder, value)

    config_commands = rendered_config.splitlines()

    try:
        logging.info(f"A aplicar o template ao dispositivo {device.get('ip')}...")
        output = connection.send_config_set(config_commands)
        logging.info(f"Template aplicado com sucesso a {device.get('ip')}.")
        messagebox.showinfo("Sucesso", f"Template aplicado com sucesso!\n\n{output}")
    except Exception as e:
        logging.error(f"Erro ao aplicar o template em {device.get('ip')}: {e}", exc_info=True)
        messagebox.showerror("Erro", f"Ocorreu um erro ao aplicar o template: {e}")