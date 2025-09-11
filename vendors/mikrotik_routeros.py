"""
Módulo específico para interagir com dispositivos Mikrotik RouterOS.
Contém comandos e funções de parsing para RouterOS.
"""
import re


def get_interfaces(connection):
    """
    Obtém e analisa a lista de interfaces de um dispositivo Mikrotik.

    Args:
        connection: O objeto de conexão Netmiko ativo.

    Returns:
        list: Uma lista de dicionários, cada um representando uma interface.
    """
    ip_output = connection.send_command("/ip address print")
    interface_output = connection.send_command("/interface print")

    interfaces = {}

    # Primeiro, obtém todas as interfaces e o seu status
    for line in interface_output.splitlines()[3:-1]:  # Ignora cabeçalho/rodapé
        parts = line.split()
        if len(parts) > 2 and parts[0].isdigit(): # Garante que é uma linha de dados
            name = parts[1]
            # Extrai o status a partir das flags (R=running)
            status = "up" if "R" in parts[2] else "down"
            interfaces[name] = {
                "interface": name,
                "ip_address": "unassigned",
                "status": status,
                "protocol": status,  # Em Mikrotik, status e protocol são similares
            }

    # Depois, associa os endereços IP às interfaces
    for line in ip_output.splitlines()[2:-1]: # Formato ligeiramente diferente
        match = re.search(r"\s(\d+\.\d+\.\d+\.\d+/\d+)\s+(\S+)", line)
        if match:
            ip = match.group(1)
            interface_name = match.group(2)
            if interface_name in interfaces:
                interfaces[interface_name]["ip_address"] = ip

    return list(interfaces.values())


def get_routes(connection):
    """
    Obtém a tabela de roteamento de um dispositivo Mikrotik RouterOS.

    Args:
        connection: O objeto de conexão Netmiko ativo.

    Returns:
        str: A saída do comando '/ip route print'.
    """
    return connection.send_command("/ip route print")


def add_static_route(connection, network, next_hop):
    """
    Adiciona uma rota estática a um dispositivo Mikrotik RouterOS.

    Args:
        connection: O objeto de conexão Netmiko ativo.
        network (str): A rede de destino no formato CIDR (ex: '10.0.0.0/24').
        next_hop (str): O endereço IP do próximo salto.

    Returns:
        str: A saída da execução do comando.
    """
    command = f"/ip route add dst-address={network} gateway={next_hop}"
    return connection.send_command(command)