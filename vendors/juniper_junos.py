"""
Módulo específico para interagir com dispositivos Juniper Junos.
Contém comandos e funções de parsing para Junos.
"""
import re


def get_interfaces(connection):
    """
    Obtém e analisa a lista de interfaces de um dispositivo Juniper Junos.

    Args:
        connection: O objeto de conexão Netmiko ativo.

    Returns:
        list: Uma lista de dicionários, cada um representando uma interface.
    """
    output = connection.send_command("show interfaces terse")
    interfaces = []
    for line in output.splitlines():
        # Procura por linhas que contêm endereços IPv4
        if "inet" in line:
            parts = line.split()
            if len(parts) >= 2:
                # A lógica de status "up/down" é mais complexa em Junos
                # e exigiria outro comando. Isto é uma simplificação.
                interfaces.append(
                    {
                        "interface": parts[0],
                        "ip_address": parts[1],
                        "status": "up",  # Placeholder
                        "protocol": "up",  # Placeholder
                    }
                )
    return interfaces


def get_routes(connection):
    """
    Obtém a tabela de roteamento de um dispositivo Juniper Junos.

    Args:
        connection: O objeto de conexão Netmiko ativo.

    Returns:
        str: A saída do comando 'show route'.
    """
    return connection.send_command("show route")


def add_static_route(connection, network, next_hop):
    """
    Adiciona uma rota estática a um dispositivo Juniper Junos.

    Args:
        connection: O objeto de conexão Netmiko ativo.
        network (str): A rede de destino no formato CIDR (ex: '10.0.0.0/24').
        next_hop (str): O endereço IP do próximo salto.

    Returns:
        str: A saída da execução dos comandos e do commit.
    """
    commands = [f"set routing-options static route {network} next-hop {next_hop}"]
    # Em Junos, é necessário fazer 'commit' para aplicar as alterações
    output = connection.send_config_set(commands)
    output += "\n--- Commit Result ---\n"
    output += connection.commit()
    return output