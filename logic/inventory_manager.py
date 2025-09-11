# logic/inventory_manager.py
"""
Módulo para gerir o inventário de dispositivos (carregar, salvar, etc.).
"""
import json
import time
from tkinter import messagebox

DEVICES_FILE = "devices.json"


def load_inventory():
    """Carrega o inventário de dispositivos do ficheiro JSON."""
    try:
        with open(DEVICES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        messagebox.showerror(
            "Erro de Inventário", f"O ficheiro {DEVICES_FILE} está corrompido."
        )
        return []


def save_inventory(devices):
    """Salva a lista de dispositivos no ficheiro JSON."""
    try:
        with open(DEVICES_FILE, "w", encoding="utf-8") as f:
            json.dump(devices, f, indent=4)
    except Exception as e:
        messagebox.showerror(
            "Erro ao Salvar", f"Não foi possível salvar o inventário: {e}"
        )


def add_device(device_details):
    """Adiciona um novo dispositivo ao inventário."""
    inventory = load_inventory()
    device_details["id"] = int(time.time() * 1000)
    inventory.append(device_details)
    save_inventory(inventory)


def update_device(updated_device):
    """Atualiza um dispositivo existente no inventário."""
    inventory = load_inventory()
    for i, device in enumerate(inventory):
        if device.get("id") == updated_device.get("id"):
            # Atualiza apenas as chaves presentes no dicionário 'updated_device'
            inventory[i].update(updated_device)
            break
    save_inventory(inventory)


def remove_device(device_id):
    """Remove um dispositivo do inventário pelo seu ID."""
    inventory = load_inventory()
    inventory = [device for device in inventory if device.get("id") != device_id]
    save_inventory(inventory)
