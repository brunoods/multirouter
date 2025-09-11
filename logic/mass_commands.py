"""
Este módulo gere a execução de comandos em múltiplos dispositivos em simultâneo.
"""

import threading
from logic.connection import get_connection

# Nota: As importações de NetmikoTimeoutException e
# NetmikoAuthenticationException foram removidas porque não eram usadas aqui.


def run_mass_commands(
    devices, commands, mass_commands_page, progress_callback, completion_callback
):
    """
    Executa comandos em múltiplos dispositivos de forma assíncrona.

    Args:
        devices (list): Lista de dispositivos onde os comandos serão executados.
        commands (str): String com os comandos a serem executados, um por linha.
        mass_commands_page: A página da UI para atualizar com os resultados.
        progress_callback (function): Função para ser chamada com o progresso.
        completion_callback (function): Função a ser chamada quando tudo terminar.
    """
    command_list = commands.splitlines()
    thread = threading.Thread(
        target=_execute_commands_thread,
        args=(
            devices,
            command_list,
            mass_commands_page,
            progress_callback,
            completion_callback,
        ),
    )
    thread.start()


def _execute_commands_thread(
    devices, command_list, mass_commands_page, progress_callback, completion_callback
):
    """
    Função executada numa thread para enviar comandos para os dispositivos.
    """
    total_devices = len(devices)
    for i, device in enumerate(devices):
        ip = device.get("ip")
        output = f"--- A executar comandos em {ip} ---\n"
        connection = get_connection(device)
        if connection:
            for command in command_list:
                try:
                    result = connection.send_command(command)
                    output += f"$ {command}\n{result}\n"
                except Exception as e:
                    output += f"Erro ao executar o comando '{command}' em {ip}: {e}\n"
            output += f"--- Fim da execução em {ip} ---\n\n"
        else:
            output = f"--- Dispositivo {ip} não conectado ---\n\n"

        # Atualiza a UI a partir da thread principal
        mass_commands_page.after(0, mass_commands_page.update_output, output)

        # Atualiza o progresso
        progress = int(((i + 1) / total_devices) * 100)
        progress_callback(progress)

    completion_callback()
