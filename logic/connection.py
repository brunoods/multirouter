"""
Este módulo gere as conexões SSH com os dispositivos de rede usando Netmiko.
Ele é responsável por estabelecer, encerrar e verificar o status das conexões.
"""
import logging
from netmiko import ConnectHandler
from netmiko.exceptions import (
    NetmikoTimeoutException,
    NetmikoAuthenticationException,
)

# Dicionário global para armazenar as conexões ativas.
# A chave é o endereço IP do dispositivo e o valor é o objeto de conexão.
connections = {}


def connect(device):
    """
    Estabelece uma conexão SSH com um dispositivo de rede.

    Args:
        device (dict): Um dicionário contendo os detalhes do dispositivo,
                       como 'ip', 'username', 'password', e 'device_type'.

    Returns:
        bool: True se a conexão for bem-sucedida, False caso contrário.
    """
    ip = device.get("ip")
    if ip in connections and connections[ip].is_alive():
        logging.info(f"Já existe uma conexão ativa com {ip}.")
        return True

    try:
        logging.info(f"A tentar conectar-se a {ip}...")
        # O '**device' desempacota o dicionário nos argumentos que o ConnectHandler espera
        net_connect = ConnectHandler(**device)
        connections[ip] = net_connect
        logging.info(f"Conexão com {ip} estabelecida com sucesso.")
        return True
    except NetmikoAuthenticationException:
        logging.error(f"Falha na autenticação para {ip}. Verifique as credenciais.")
        return False
    except NetmikoTimeoutException:
        logging.error(
            f"Timeout ao conectar-se a {ip}. Verifique a conectividade e a firewall."
        )
        return False
    except Exception as e:
        # Captura qualquer outra exceção inesperada e regista o erro completo
        logging.error(
            f"Ocorreu um erro inesperado ao conectar-se a {ip}: {e}", exc_info=True
        )
        return False


def disconnect(device):
    """
    Encerra a conexão SSH com um dispositivo específico.

    Args:
        device (dict): O dicionário do dispositivo a ser desconectado.
    """
    ip = device.get("ip")
    if ip in connections:
        try:
            connections[ip].disconnect()
            logging.info(f"Conexão com {ip} encerrada com sucesso.")
        except Exception as e:
            logging.error(f"Erro ao desconectar de {ip}: {e}", exc_info=True)
        finally:
            # Garante que a conexão é removida do dicionário, mesmo que falhe
            del connections[ip]


def get_connection(device):
    """
    Retorna o objeto de conexão ativo para um dispositivo.

    Args:
        device (dict): O dispositivo para o qual obter a conexão.

    Returns:
        netmiko.ConnectHandler or None: O objeto de conexão se estiver ativo,
                                        caso contrário, None.
    """
    if not device:
        return None
    connection = connections.get(device.get("ip"))
    if connection and connection.is_alive():
        return connection
    return None


def get_connection_status(device):
    """
    Verifica e retorna o status da conexão para um dispositivo.

    Args:
        device (dict): O dispositivo a ser verificado.

    Returns:
        str: Uma string descritiva do status ("Conectado", "Não conectado", etc.).
    """
    if not device:
        return "Nenhum dispositivo selecionado"

    if get_connection(device):
        return "Conectado"
    else:
        return "Não conectado"