"""
Gere a criação, armazenamento e verificação de alertas de rede.
"""

import json
import os
from tkinter import messagebox


class AlertsManager:
    """Gere as operações de CRUD (Criar, Ler, Atualizar, Apagar) para os alertas."""

    def __init__(self, filename="alerts.json"):
        """
        Inicializa o gestor de alertas.

        Args:
            filename (str): O nome do ficheiro para guardar os alertas.
        """
        self.filename = filename
        self.alerts = self._load_alerts()

    def _load_alerts(self):
        """Carrega os alertas do ficheiro JSON."""
        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                return json.load(f)
        return []

    def _save_alerts(self):
        """Guarda os alertas no ficheiro JSON."""
        with open(self.filename, "w") as f:
            json.dump(self.alerts, f, indent=4)

    def add_alert(self, alert):
        """
        Adiciona um novo alerta à lista.

        Args:
            alert (dict): O dicionário do alerta a ser adicionado.
        """
        self.alerts.append(alert)
        self._save_alerts()

    def get_alerts(self):
        """Retorna todos os alertas."""
        return self.alerts

    def update_alert(self, index, updated_alert):
        """
        Atualiza um alerta existente.

        Args:
            index (int): O índice do alerta a ser atualizado.
            updated_alert (dict): O dicionário com os dados atualizados do alerta.
        """
        if 0 <= index < len(self.alerts):
            self.alerts[index] = updated_alert
            self._save_alerts()

    def delete_alert(self, index):
        """
        Apaga um alerta.

        Args:
            index (int): O índice do alerta a ser apagado.
        """
        if 0 <= index < len(self.alerts):
            del self.alerts[index]
            self._save_alerts()


def check_alerts(app):
    """
    Verifica todos os alertas definidos.

    Args:
        app: A instância principal da aplicação.
    """
    alerts_manager = app.alerts_manager
    inventory_manager = app.inventory_manager
    alerts = alerts_manager.get_alerts()
    devices = inventory_manager.get_devices()

    for alert in alerts:
        for device in devices:
            # Lógica de verificação de alertas (exemplo)
            if alert["type"] == "Status da Interface" and alert["device"] == device.get(
                "ip"
            ):
                messagebox.showinfo(
                    "Alerta",
                    f"A verificar o status da interface para o alerta:"
                    f"\n{alert['name']} no dispositivo {device.get('ip')}",
                )
