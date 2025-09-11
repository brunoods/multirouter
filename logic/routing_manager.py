"""
Módulo para gerir as tabelas de roteamento dos dispositivos de rede.
"""
import logging
import importlib
from tkinter import messagebox
from logic.connection import get_connection

def get_device_routes(device):
    """
    Obtém a tabela de roteamento de um dispositivo dinamicamente.

    Args:
        device (dict): O dicionário do dispositivo.

    Returns:
        str: A tabela de roteamento como texto ou uma mensagem de erro.
    """
    connection = get_connection(device)
    if not connection:
        return "Dispositivo não conectado."

    try:
        device_type = device.get("device_type")
        module_path = f"vendors.{device_type}"
        vendor_module = importlib.import_module(module_path)
        
        if hasattr(vendor_module, "get_routes"):
            return vendor_module.get_routes(connection)
        else:
            msg = f"Função 'get_routes' não implementada para {device_type}"
            logging.warning(msg)
            return msg
    except Exception as e:
        logging.error(f"Erro ao obter rotas de {device.get('ip')}: {e}", exc_info=True)
        return f"Ocorreu um erro inesperado: {e}"

def add_static_route(device, network, next_hop):
    """
    Adiciona uma rota estática a um dispositivo.

    Args:
        device (dict): O dicionário do dispositivo.
        network (str): A rede de destino (ex: '10.0.0.0/24').
        next_hop (str): O IP do próximo salto.
    """
    connection = get_connection(device)
    if not connection:
        messagebox.showerror("Erro", "Dispositivo não conectado.")
        return

    try:
        device_type = device.get("device_type")
        module_path = f"vendors.{device_type}"
        vendor_module = importlib.import_module(module_path)

        if hasattr(vendor_module, "add_static_route"):
            output = vendor_module.add_static_route(connection, network, next_hop)
            messagebox.showinfo("Sucesso", f"Comandos enviados:\n{output}")
        else:
            messagebox.showwarning("Não Implementado", f"Adicionar rota não implementado para {device_type}")

    except Exception as e:
        logging.error(f"Erro ao adicionar rota em {device.get('ip')}: {e}", exc_info=True)
        messagebox.showerror("Erro", f"Ocorreu um erro inesperado: {e}")