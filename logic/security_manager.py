"""
Módulo para gerir as funcionalidades de segurança, como ACLs.
"""
import logging
import importlib
from tkinter import messagebox
from logic.connection import get_connection

def get_acls(device):
    """Obtém a lista de ACLs de um dispositivo."""
    connection = get_connection(device)
    if not connection:
        messagebox.showerror("Erro", "Dispositivo não conectado.")
        return []

    try:
        device_type = device.get("device_type")
        module_path = f"vendors.{device_type}"
        vendor_module = importlib.import_module(module_path)

        if hasattr(vendor_module, "get_acls"):
            return vendor_module.get_acls(connection)
        else:
            messagebox.showwarning("Não Implementado", f"Função 'get_acls' não implementada para {device_type}")
            return []
    except Exception as e:
        logging.error(f"Erro ao obter ACLs de {device.get('ip')}: {e}", exc_info=True)
        return []


def add_acl_rule(device, acl_name, rule_details):
    """Adiciona uma regra a uma ACL existente."""
    connection = get_connection(device)
    if not connection:
        messagebox.showerror("Erro", "Dispositivo não conectado.")
        return

    try:
        device_type = device.get("device_type")
        module_path = f"vendors.{device_type}"
        vendor_module = importlib.import_module(module_path)

        if hasattr(vendor_module, "add_acl_rule"):
            output = vendor_module.add_acl_rule(connection, acl_name, rule_details)
            messagebox.showinfo("Sucesso", f"Comandos para adicionar regra enviados:\n{output}")
        else:
            messagebox.showwarning("Não Implementado", f"Função 'add_acl_rule' não implementada para {device_type}")
    except Exception as e:
        logging.error(f"Erro ao adicionar regra de ACL em {device.get('ip')}: {e}", exc_info=True)
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}")