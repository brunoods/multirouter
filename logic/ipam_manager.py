# logic/ipam_manager.py
"""
Módulo para gerir o inventário de sub-redes (IPAM).
"""
import json
import ipaddress
from tkinter import messagebox

IPAM_FILE = "ipam.json"

def load_subnets():
    """Carrega as sub-redes do ficheiro JSON."""
    try:
        with open(IPAM_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        messagebox.showerror("Erro de IPAM", f"O ficheiro {IPAM_FILE} está corrompido.")
        return []

def save_subnets(subnets):
    """Salva a lista de sub-redes no ficheiro JSON."""
    try:
        with open(IPAM_FILE, 'w', encoding='utf-8') as f:
            json.dump(subnets, f, indent=4)
    except Exception as e:
        messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar os dados de IPAM: {e}")

def add_subnet(subnet_cidr, description):
    """Adiciona uma nova sub-rede ao inventário."""
    try:
        # Valida se a entrada é uma rede válida
        ipaddress.ip_network(subnet_cidr)
    except ValueError:
        messagebox.showerror("Entrada Inválida", f"'{subnet_cidr}' não é uma sub-rede válida. Use o formato CIDR (ex: 192.168.1.0/24).")
        return

    subnets = load_subnets()
    # Verifica se a sub-rede já existe
    if any(s['cidr'] == subnet_cidr for s in subnets):
        messagebox.showwarning("Sub-rede Duplicada", "Esta sub-rede já está no inventário.")
        return
        
    subnets.append({'cidr': subnet_cidr, 'description': description, 'allocations': {}})
    save_subnets(subnets)

def remove_subnet(subnet_cidr):
    """Remove uma sub-rede do inventário."""
    subnets = load_subnets()
    subnets = [s for s in subnets if s['cidr'] != subnet_cidr]
    save_subnets(subnets)

def get_subnet_details(subnet_cidr):
    """Retorna uma lista de todos os IPs numa sub-rede com o seu estado."""
    if not subnet_cidr:
        return []

    try:
        network = ipaddress.ip_network(subnet_cidr)
        ip_list = []
        
        # Encontra as alocações guardadas para esta rede
        subnets_data = load_subnets()
        subnet_info = next((s for s in subnets_data if s['cidr'] == subnet_cidr), None)
        allocations = subnet_info.get('allocations', {}) if subnet_info else {}

        for ip in network.hosts():
            ip_str = str(ip)
            status = allocations.get(ip_str, "Disponível")
            ip_list.append({'ip': ip_str, 'status': status})
            
        # Adiciona o endereço de rede e broadcast para informação
        if network.prefixlen < 31:
             ip_list.insert(0, {'ip': str(network.network_address), 'status': 'Endereço de Rede'})
             ip_list.append({'ip': str(network.broadcast_address), 'status': 'Endereço de Broadcast'})

        return ip_list
    except ValueError:
        return []