import threading
from logic.connection import get_connection

class MassCommands:
    """
    Encapsula a lógica para executar comandos em massa de forma assíncrona.
    """
    def execute(self, devices, commands, ui_update_callback, completion_callback):
        """
        Inicia a execução dos comandos numa thread separada para não bloquear a UI.

        Args:
            devices (list): A lista de dispositivos.
            commands (list): A lista de comandos.
            ui_update_callback (function): Função para ser chamada com a saída de cada dispositivo.
            completion_callback (function): Função a ser chamada quando tudo terminar.
        """
        thread = threading.Thread(
            target=self._thread_worker,
            args=(devices, commands, ui_update_callback, completion_callback),
        )
        thread.start()

    def _thread_worker(self, devices, commands, ui_update_callback, completion_callback):
        """
        O trabalho que é executado na thread. Conecta-se a cada dispositivo e executa os comandos.
        """
        for device in devices:
            ip = device.get("ip")
            device_name = device.get("name", ip)
            output = f"--- {device_name} ({ip}) ---\n"
            
            connection = get_connection(device)
            if connection:
                try:
                    for command in commands:
                        result = connection.send_command(command)
                        output += f"$ {command}\n{result}\n"
                except Exception as e:
                    output += f"Erro: {e}\n"
                finally:
                    connection.disconnect()
            else:
                output += "Falha ao conectar.\n"
            
            output += "\n"
            
            # Usa o callback para enviar a atualização para a UI de forma segura
            ui_update_callback(output)
        
        # Chama o callback de conclusão
        completion_callback()