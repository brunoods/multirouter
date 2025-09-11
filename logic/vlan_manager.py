"""
Módulo para gerir as VLANs dos dispositivos de rede.
"""
import logging
import importlib
from tkinter import messagebox
from logic.connection import get_connection

def get_device_vlans(device):
    """
    Obtém a lista de VLANs de um dispositivo dinamicamente.

    Args:
        device (dict): O dicionário do dispositivo.

    Returns:
        list: Uma lista de dicionários, onde cada um representa uma VLAN.
              Retorna uma lista vazia em caso de erro.
    """
    connection = get_connection(device)
    if not connection:
        messagebox.showerror("Erro", "Dispositivo não conectado.")
        return []

    try:
        device_type = device.get("device_type")
        module_path = f"vendors.{device_type}"
        vendor_module = importlib.import_module(module_path)

        if hasattr(vendor_module, "get_vlans"):
            return vendor_module.get_vlans(connection)
        else:
            msg = f"Função 'get_vlans' não implementada para {device_type}"
            logging.warning(msg)
            messagebox.showwarning("Não Implementado", msg)
            return []
    except Exception as e:
        logging.error(f"Erro ao obter VLANs de {device.get('ip')}: {e}", exc_info=True)
        messagebox.showerror("Erro", f"Ocorreu um erro inesperado: {e}")
        return []

def create_vlan(device, vlan_id, vlan_name):
    """
    Cria uma nova VLAN num dispositivo.

    Args:
        device (dict): O dicionário do dispositivo.
        vlan_id (str): O ID da VLAN a ser criada (ex: '100').
        vlan_name (str): O nome da VLAN.
    """
    connection = get_connection(device)
    if not connection:
        messagebox.showerror("Erro", "Dispositivo não conectado.")
        return

    try:
        device_type = device.get("device_type")
        module_path = f"vendors.{device_type}"
        vendor_module = importlib.import_module(module_path)

        if hasattr(vendor_module, "create_vlan"):
            output = vendor_module.create_vlan(connection, vlan_id, vlan_name)
            messagebox.showinfo("Sucesso", f"Comandos para criar VLAN enviados:\n{output}")
        else:
            messagebox.showwarning("Não Implementado", f"Criar VLAN não implementado para {device_type}")

    except Exception as e:
        logging.error(f"Erro ao criar VLAN em {device.get('ip')}: {e}", exc_info=True)
        messagebox.showerror("Erro", f"Ocorreu um erro inesperado: {e}")