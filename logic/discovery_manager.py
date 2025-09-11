"""
Módulo para a descoberta de dispositivos na rede.
"""
import threading
import socket
import logging
from logic.connection import connect, get_connection

def start_discovery(network_range, credentials, inventory_manager, progress_callback, completion_callback):
    """
    Inicia a descoberta de dispositivos numa thread separada.

    Args:
        network_range (str): A gama de IPs a verificar (ex: 192.168.1.0/24).
        credentials (dict): Credenciais para tentar a ligação ({'username': ..., 'password': ...}).
        inventory_manager: A instância do InventoryManager para adicionar dispositivos.
        progress_callback (function): Função para atualizar a barra de progresso.
        completion_callback (function): Função a ser chamada no final.
    """
    thread = threading.Thread(
        target=_discover_thread,
        args=(network_range, credentials, inventory_manager, progress_callback, completion_callback),
        daemon=True
    )
    thread.start()

def _discover_thread(network_range, credentials, inventory_manager, progress_callback, completion_callback):
    """A lógica de descoberta que corre em segundo plano."""
    try:
        # Lógica simples para gerar IPs a partir de uma gama /24
        base_ip = ".".join(network_range.split('.')[:3])
        ips_to_scan = [f"{base_ip}.{i}" for i in range(1, 255)]
    except Exception as e:
        logging.error(f"Gama de rede inválida: {network_range}. Erro: {e}")
        completion_callback()
        return

    total_ips = len(ips_to_scan)
    for i, ip in enumerate(ips_to_scan):
        progress_callback(int(((i + 1) / total_ips) * 100))
        # Verifica se a porta 22 (SSH) está aberta
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.1)  # Timeout rápido
            if s.connect_ex((ip, 22)) == 0:
                logging.info(f"Porta 22 aberta encontrada em {ip}. A tentar conectar...")
                # Tenta conectar com as credenciais fornecidas
                for device_type in ["cisco_ios", "juniper_junos", "mikrotik_routeros"]:
                    device_details = {
                        "ip": ip,
                        "host": ip,  # Usa o IP como hostname por defeito
                        "device_type": device_type,
                        "username": credentials["username"],
                        "password": credentials["password"],
                    }
                    conn = connect(device_details)
                    if conn:
                        logging.info(f"Dispositivo {ip} ({device_type}) descoberto e adicionado.")
                        # Verifica se o dispositivo já existe antes de adicionar
                        existing_ips = [dev['ip'] for dev in inventory_manager.get_devices()]
                        if ip not in existing_ips:
                            inventory_manager.add_device(device_details)
                        # Fecha a conexão de teste
                        get_connection(device_details).disconnect()
                        break # Pára de tentar outros tipos de dispositivo

    completion_callback()