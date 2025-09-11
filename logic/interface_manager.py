"""
Módulo para gerir as interfaces dos dispositivos de rede.

Este gestor atua como uma ponte entre a UI e os módulos de
lógica específicos de cada fabricante (vendor).
"""
import logging
import importlib
from tkinter import messagebox
from logic.connection import get_connection


def get_device_interfaces(device):
    """
    Obtém a lista de interfaces de um dispositivo dinamicamente.

    Ele importa o módulo do fabricante correto em tempo de execução
    e chama a função 'get_interfaces' desse módulo.

    Args:
        device (dict): O dicionário do dispositivo.

    Returns:
        list: Uma lista de dicionários, onde cada um representa uma interface.
              Retorna uma lista vazia em caso de erro.
    """
    connection = get_connection(device)
    if not connection:
        messagebox.showerror("Erro", "Dispositivo não conectado.")
        logging.warning(
            f"Tentativa de obter interfaces de um dispositivo não conectado: {device.get('ip')}"
        )
        return []

    try:
        device_type = device.get("device_type")
        # Constrói o caminho completo para o módulo do fabricante
        module_path = f"vendors.{device_type}"
        # Importa o módulo dinamicamente
        vendor_module = importlib.import_module(module_path)

        # Chama a função 'get_interfaces' do módulo importado
        return vendor_module.get_interfaces(connection)

    except ImportError:
        logging.error(f"Módulo do fabricante não encontrado para o tipo: {device_type}")
        messagebox.showerror(
            "Erro", f"O módulo para o tipo de dispositivo '{device_type}' não foi encontrado."
        )
        return []
    except AttributeError:
        logging.error(f"A função 'get_interfaces' não foi encontrada no módulo {module_path}")
        messagebox.showerror(
            "Erro", f"Funcionalidade de interfaces não implementada para '{device_type}'."
        )
        return []
    except Exception as e:
        logging.error(
            f"Erro ao obter interfaces de {device.get('ip')}: {e}", exc_info=True
        )
        messagebox.showerror("Erro", f"Ocorreu um erro inesperado: {e}")
        return []