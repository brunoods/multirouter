"""
Gere o inventário de dispositivos, lidando com o carregamento e
armazenamento de dados a partir de um ficheiro JSON.
"""
import json
import os
import logging

class InventoryManager:
    """Uma classe para gerir as operações CRUD de dispositivos de rede."""

    def __init__(self, filename="devices.json"):
        """
        Inicializa o gestor de inventário.

        Args:
            filename (str): O nome do ficheiro JSON para guardar os dispositivos.
        """
        self.filename = filename
        self.devices = self._load_devices()
        logging.info(f"{len(self.devices)} dispositivos carregados de {self.filename}.")

    def _load_devices(self):
        """Carrega a lista de dispositivos do ficheiro JSON."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logging.error(f"Erro ao ler o ficheiro JSON: {self.filename}. Ficheiro corrompido ou vazio.")
                return []
        return []

    def _save_devices(self):
        """Guarda a lista atual de dispositivos no ficheiro JSON."""
        try:
            with open(self.filename, "w") as f:
                json.dump(self.devices, f, indent=4)
            logging.info(f"Inventário guardado com sucesso em {self.filename}.")
        except Exception as e:
            logging.error(f"Não foi possível guardar o inventário em {self.filename}: {e}")

    def get_devices(self):
        """Retorna a lista completa de dispositivos."""
        return self.devices

    def add_device(self, device):
        """
        Adiciona um novo dispositivo ao inventário e guarda.

        Args:
            device (dict): O dicionário do dispositivo a ser adicionado.
        """
        self.devices.append(device)
        self._save_devices()
        logging.info(f"Dispositivo adicionado: {device.get('ip')}")

    def update_device(self, index, updated_device):
        """
        Atualiza um dispositivo existente no inventário e guarda.

        Args:
            index (int): O índice do dispositivo a ser atualizado.
            updated_device (dict): O dicionário com os dados atualizados.
        """
        if 0 <= index < len(self.devices):
            self.devices[index] = updated_device
            self._save_devices()
            logging.info(f"Dispositivo atualizado: {updated_device.get('ip')}")
        else:
            logging.warning(f"Tentativa de atualizar um dispositivo com índice inválido: {index}")

    def remove_device(self, index):
        """
        Remove um dispositivo do inventário e guarda.

        Args:
            index (int): O índice do dispositivo a ser removido.
        """
        if 0 <= index < len(self.devices):
            removed_device = self.devices.pop(index)
            self._save_devices()
            logging.info(f"Dispositivo removido: {removed_device.get('ip')}")
        else:
            logging.warning(f"Tentativa de remover um dispositivo com índice inválido: {index}")