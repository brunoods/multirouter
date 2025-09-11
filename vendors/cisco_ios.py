"""
Módulo específico para interagir com dispositivos Cisco IOS.
Contém comandos e funções de parsing para obter informações específicas da Cisco.
"""
import re


def get_interfaces(connection):
    """
    Obtém e analisa a lista de interfaces de um dispositivo Cisco IOS.

    Args:
        connection: O objeto de conexão Netmiko ativo.

    Returns:
        list: Uma lista de dicionários, cada um representando uma interface.
    """
    output = connection.send_command("show ip interface brief")
    interfaces = []
    # Regex para capturar: Interface, IP, Status e Protocolo
    regex = r"^(\S+)\s+([\d\.]+|unassigned)\s+\w+\s+\w+\s+(up|down|administratively down)\s+(\w+)"
    for line in output.splitlines():
        match = re.search(regex, line)
        if match:
            interfaces.append(
                {
                    "interface": match.group(1),
                    "ip_address": match.group(2),
                    "status": match.group(3),
                    "protocol": match.group(4),
                }
            )
    return interfaces


def get_routes(connection):
    """
    Obtém a tabela de roteamento de um dispositivo Cisco IOS.

    Args:
        connection: O objeto de conexão Netmiko ativo.

    Returns:
        str: A saída do comando 'show ip route'.
    """
    return connection.send_command("show ip route")


def add_static_route(connection, network, next_hop):
    """
    Adiciona uma rota estática a um dispositivo Cisco IOS.

    Args:
        connection: O objeto de conexão Netmiko ativo.
        network (str): A rede de destino no formato CIDR (ex: '10.0.0.0/24').
        next_hop (str): O endereço IP do próximo salto.

    Returns:
        str: A saída da execução dos comandos de configuração.
    """
    # Lógica para converter CIDR em máscara de sub-rede.
    # Isto é uma simplificação. Uma biblioteca como 'ipaddress' seria ideal.
    try:
        ip_addr, cidr_mask = network.split("/")
        cidr = int(cidr_mask)
        mask_parts = []
        for i in range(4):
            if cidr >= 8:
                mask_parts.append("255")
                cidr -= 8
            elif cidr > 0:
                mask_parts.append(str(256 - (2 ** (8 - cidr))))
                cidr = 0
            else:
                mask_parts.append("0")
        subnet_mask = ".".join(mask_parts)
    except (ValueError, IndexError):
        raise ValueError("Formato de rede inválido. Use IP/máscara (ex: 10.0.0.0/24)")

    commands = [f"ip route {ip_addr} {subnet_mask} {next_hop}"]
    return connection.send_config_set(commands)