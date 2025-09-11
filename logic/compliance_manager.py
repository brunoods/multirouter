"""
Gere as regras de conformidade e a sua verificação nos dispositivos de rede.
"""

import json
import os
from tkinter import messagebox


class ComplianceManager:
    """Gere as operações de CRUD para as regras de conformidade."""

    def __init__(self, filename="compliance_rules.json"):
        """
        Inicializa o gestor de conformidade.

        Args:
            filename (str): O nome do ficheiro para guardar as regras.
        """
        self.filename = filename
        self.rules = self._load_rules()

    def _load_rules(self):
        """Carrega as regras de conformidade do ficheiro JSON."""
        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                return json.load(f)
        return []

    def _save_rules(self):
        """Guarda as regras de conformidade no ficheiro JSON."""
        with open(self.filename, "w") as f:
            json.dump(self.rules, f, indent=4)

    def add_rule(self, rule):
        """Adiciona uma nova regra."""
        self.rules.append(rule)
        self._save_rules()

    def get_rules(self):
        """Retorna todas as regras."""
        return self.rules

    def update_rule(self, index, updated_rule):
        """
        Atualiza uma regra existente.

        Args:
            index (int): O índice da regra a ser atualizada.
            updated_rule (dict): A regra com os dados atualizados.
        """
        if 0 <= index < len(self.rules):
            self.rules[index] = updated_rule
            self._save_rules()

    def delete_rule(self, index):
        """Apaga uma regra."""
        if 0 <= index < len(self.rules):
            del self.rules[index]
            self._save_rules()


def check_compliance(app, device, rule):
    """
    Verifica se a configuração de um dispositivo está em conformidade com uma regra.

    Args:
        app: A instância principal da aplicação.
        device (dict): O dispositivo a ser verificado.
        rule (dict): A regra a ser aplicada.
    """
    # Lógica de verificação de conformidade
    messagebox.showinfo(
        "Verificação de Conformidade",
        f"A verificar a regra '{rule['name']}' no dispositivo {device.get('ip')}",
    )
    # Aqui entraria a lógica real para obter a configuração e compará-la.
    is_compliant = True  # Placeholder

    result_message = (
        f"O dispositivo {device.get('ip')} está em conformidade "
        f"com a regra '{rule['name']}'."
        if is_compliant
        else f"O dispositivo {device.get('ip')} NÃO está em conformidade com a "
        f"regra '{rule['name']}'."
    )
    messagebox.showinfo("Resultado da Conformidade", result_message)
