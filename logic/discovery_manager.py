import threading
import socket
import logging
from ipaddress import ip_network
from logic.connection import connect

class DiscoveryManager:
    """
    Encapsula a lógica para descobrir dispositivos na rede de forma assíncrona.
    """
    def start(self, network_range, credentials, inventory_manager, progress_callback, completion_callback):
        """
        Inicia a descoberta de dispositivos numa thread separada.
        """
        thread = threading.Thread(
            target=self._discover_thread,
            args=(network_range, credentials, inventory_manager, progress_callback, completion_callback),
            daemon=True
        )
        thread.start()

    def _discover_thread(self, network_range, credentials, inventory_manager, progress_callback, completion_callback):
        """A lógica de descoberta que corre em segundo plano."""
        try:
            # Usa a biblioteca ipaddress para uma gestão de rede mais robusta e flexível
            network = ip_network(network_range, strict=False)
            ips_to_scan = [str(ip) for ip in network.hosts()]
        except ValueError as e:
            logging.error(f"Gama de rede inválida: {network_range}. Erro: {e}")
            completion_callback(f"Erro: Gama de rede inválida - {e}")
            return

        total_ips = len(ips_to_scan)
        if total_ips == 0:
            completion_callback("Nenhum IP para verificar na gama fornecida.")
            return

        existing_ips = {dev['ip'] for dev in inventory_manager.get_devices()}
        discovered_devices = []

        for i, ip in enumerate(ips_to_scan):
            # Verifica se a porta 22 (SSH) está aberta
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.1)  # Timeout rápido para não bloquear
                if s.connect_ex((ip, 22)) == 0:
                    logging.info(f"Porta 22 aberta encontrada em {ip}. A tentar conectar...")
                    for device_type in ["cisco_ios", "juniper_junos", "mikrotik_routeros"]:
                        device_details = {
                            "name": ip,
                            "ip": ip,
                            "type": device_type,
                            "username": credentials["username"],
                            "password": credentials["password"],
                        }
                        conn = connect(device_details)
                        if conn:
                            logging.info(f"Dispositivo {ip} ({device_type}) descoberto.")
                            if ip not in existing_ips:
                                inventory_manager.add_device(device_details)
                                existing_ips.add(ip)
                                discovered_devices.append(device_details)
                            conn.disconnect()
                            break
            
            progress_callback(int(((i + 1) / total_ips) * 100))

        completion_callback(discovered_devices)