"""
Módulo para gerir as configurações dos dispositivos de rede.
Inclui funções para obter, guardar, exportar e restaurar configurações.
"""

import os
from tkinter import filedialog, messagebox


def get_config(device, connection):
    """
    Obtém a configuração 'running-config' de um dispositivo.

    Args:
        device (dict): O dispositivo do qual obter a configuração.
        connection: O objeto de conexão Netmiko.

    Returns:
        str: A configuração do dispositivo ou uma mensagem de erro.
    """
    if not connection or not connection.is_alive():
        return "Erro: Dispositivo não conectado."
    try:
        # O comando pode variar dependendo do 'device_type'
        command = "show running-config"
        if device.get("device_type") == "juniper_junos":
            command = "show configuration"
        elif device.get("device_type") == "mikrotik_routeros":
            command = "export"

        output = connection.send_command(command)
        return output
    except Exception as e:
        return f"Erro ao obter a configuração: {e}"


def save_config(device, connection):
    """
    Salva a configuração 'running-config' na 'startup-config' do dispositivo.

    Args:
        device (dict): O dispositivo onde a configuração será guardada.
        connection: O objeto de conexão Netmiko.
    """
    if not connection or not connection.is_alive():
        messagebox.showerror("Erro", "Dispositivo não conectado.")
        return

    try:
        command = "write memory"
        if device.get("device_type") == "juniper_junos":
            command = "commit"
        # Mikrotik não tem um comando análogo direto via CLI para "salvar"

        output = (
            connection.save_config()
            if command == "write memory"
            else connection.commit()
        )

        messagebox.showinfo("Sucesso", f"Configuração guardada com sucesso!\n{output}")
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao guardar a configuração: {e}")


def export_config(device, connection):
    """
    Exporta a configuração de um dispositivo para um ficheiro de texto.

    Args:
        device (dict): O dispositivo cuja configuração será exportada.
        connection: O objeto de conexão Netmiko.
    """
    config = get_config(device, connection)
    if "Erro" in config:
        messagebox.showerror("Erro", config)
        return

    # Sugere um nome de ficheiro
    filename = f"{device.get('ip')}_config.txt"
    filepath = filedialog.asksaveasfilename(
        initialfile=filename,
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
    )

    if filepath:
        try:
            with open(filepath, "w") as f:
                f.write(config)
            messagebox.showinfo("Sucesso", f"Configuração exportada para {filepath}")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao exportar a configuração: {e}")


def restore_config(device, connection):
    """
    Restaura uma configuração para um dispositivo a partir de um ficheiro.

    Args:
        device (dict): O dispositivo onde a configuração será restaurada.
        connection: O objeto de conexão Netmiko.
    """
    if not connection or not connection.is_alive():
        messagebox.showerror("Erro", "Dispositivo não conectado.")
        return

    filepath = filedialog.askopenfilename(
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )

    if not filepath:
        return

    try:
        output = connection.send_config_from_file(filepath)
        messagebox.showinfo(
            "Sucesso", f"Configuração restaurada com sucesso!\n{output}"
        )
        # Opcional: guardar a configuração após restaurar
        save_config(device, connection)
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao restaurar a configuração: {e}")
