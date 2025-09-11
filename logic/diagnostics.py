"""
Módulo para executar diagnósticos de rede como Ping e Traceroute.
"""

import subprocess
import threading


def run_ping(ip, output_callback):
    """
    Executa o comando ping para um determinado IP numa thread separada.

    Args:
        ip (str): O endereço IP para o qual executar o ping.
        output_callback (function): Função para atualizar a UI com o resultado.
    """

    def ping_thread():
        """Função que executa o ping em segundo plano."""
        try:
            # Comando de ping pode variar entre SOs (aqui para Windows/Linux)
            param = "-n" if subprocess.os.name == "nt" else "-c"
            command = ["ping", param, "4", ip]
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            output = result.stdout
        except subprocess.CalledProcessError as e:
            output = f"Erro ao executar o ping:\n{e.stderr}"
        except FileNotFoundError:
            output = "Erro: O comando 'ping' não foi encontrado."
        except Exception as e:
            output = f"Ocorreu um erro inesperado: {e}"

        output_callback(output)

    threading.Thread(target=ping_thread, daemon=True).start()


def run_traceroute(ip, output_callback):
    """
    Executa o comando traceroute para um determinado IP numa thread separada.

    Args:
        ip (str): O endereço IP para o qual executar o traceroute.
        output_callback (function): Função para atualizar a UI com o resultado.
    """

    def traceroute_thread():
        """Função que executa o traceroute em segundo plano."""
        try:
            command = "tracert" if subprocess.os.name == "nt" else "traceroute"
            result = subprocess.run(
                [command, ip], capture_output=True, text=True, check=True
            )
            output = result.stdout
        except subprocess.CalledProcessError as e:
            output = f"Erro ao executar o traceroute:\n{e.stderr}"
        except FileNotFoundError:
            output = f"Erro: O comando '{command}' não foi encontrado."
        except Exception as e:
            output = f"Ocorreu um erro inesperado: {e}"

        output_callback(output)

    threading.Thread(target=traceroute_thread, daemon=True).start()
