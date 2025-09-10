# vendors/mikrotik_routeros.py
import re
import time

device_type = "mikrotik_routeros"

def get_config_commands():
    return {"running": "/export", "interfaces": "/interface print detail", "vlans": "/interface vlan print detail"}

def get_show_commands():
    """Retorna um dicionário de comandos 'show' de verificação."""
    return {
        'version': '/system resource print',
        'ip_brief': '/ip address print',
        'neighbors': '/ip neighbor print',
        'static_routes': '/ip route print where static=yes',
        'acls': '/ip firewall filter print detail'
    }

def get_static_route_config_commands(network, prefix, nexthop):
    return [f"/ip route add dst-address={network}/{prefix} gateway={nexthop}"]

def get_interface_config_commands(interface_name, description, status, vlan_id=None):
    commands = []
    commands.append(f'/interface set [find name="{interface_name}"] comment="{description}"')
    if status == "off":
        commands.append(f'/interface disable [find name="{interface_name}"]')
    else:
        commands.append(f'/interface enable [find name="{interface_name}"]')
    return commands

def get_vlan_config_commands(vlan_id, vlan_name, interface_master="bridge"):
    return [f"/interface vlan add name={vlan_name} vlan-id={vlan_id} interface={interface_master}"]

def get_acl_rule_config_commands(chain_name, rule_details):
    command = (f"/ip firewall filter add chain={chain_name} action={rule_details['action']} "
               f"protocol={rule_details['protocol']} src-address={rule_details['source']} "
               f"dst-address={rule_details['destination']}")
    if rule_details.get('options'):
        command += f" {rule_details['options']}"
    return [command]

def parse_version(text):
    """Analisa a saída do '/system resource print' para extrair modelo e versão."""
    version_match = re.search(r"version: ([\d\.]+)", text)
    model_match = re.search(r"board-name: (.*)", text)
    return {
        "version": version_match.group(1) if version_match else "N/A",
        "model": model_match.group(1).strip() if model_match else "N/A"
    }

def check_compliance(config_text):
    """Verifica a configuração contra um conjunto de regras de conformidade."""
    results = []
    
    # Regra 1: Verificar se NTP está configurado e ativo
    if re.search(r"/system ntp client set enabled=yes servers=", config_text, re.MULTILINE):
        results.append({'rule': 'NTP Configurado', 'status': 'Conforme', 'details': 'Cliente NTP encontrado e ativo.'})
    else:
        results.append({'rule': 'NTP Configurado', 'status': 'Não Conforme', 'details': 'Cliente NTP não está configurado ou não está ativo.'})
        
    return results

def parse_acl_rules(chain_name, chain_type, text):
    results = []
    rule_blocks = re.split(r'^\s*\d+\s+[XID ]*\s*', text, flags=re.MULTILINE)[1:]
    for i, block in enumerate(rule_blocks):
        chain_match = re.search(r'chain=(\S+)', block)
        if chain_match and chain_match.group(1) == chain_name:
            action = (m.group(1) if (m := re.search(r'action=(\S+)', block)) else 'N/A')
            protocol = (m.group(1) if (m := re.search(r'protocol=(\S+)', block)) else 'any')
            src_addr = (m.group(1) if (m := re.search(r'src-address=(\S+)', block)) else 'any')
            dst_addr = (m.group(1) if (m := re.search(r'dst-address=(\S+)', block)) else 'any')
            comment = (m.group(1) if (m := re.search(r'comment=\'(.*?)\'', block)) else '')
            results.append({
                'id_term': str(i), 'action': action, 'protocol': protocol,
                'source': src_addr, 'destination': dst_addr, 'options': comment
            })
    return results

def parse_acls(text):
    results = []
    chains = set()
    pattern = re.compile(r"chain=(\S+)")
    for line in text.strip().splitlines():
        match = pattern.search(line)
        if match:
            chains.add(match.group(1))
    for chain_name in sorted(list(chains)):
         results.append({'type': 'Chain', 'name_id': chain_name})
    return results

def parse_static_routes(text):
    results = []
    pattern = re.compile(r"dst-address=(\S+)\s+gateway=(\S+)")
    for line in text.strip().splitlines():
        match = pattern.search(line)
        if match:
            results.append({'destination': match.group(1), 'next_hop': match.group(2)})
    return results

def parse_ip_brief(text):
    results = []
    lines = text.strip().splitlines()
    pattern = re.compile(r"^\s*\d+\s+D?\s*(\S+/\d+)\s+\S+\s+(\S+)")
    for line in lines:
        match = pattern.match(line)
        if match:
            results.append({'interface': match.group(2), 'ip_address': match.group(1), 'status': 'up', 'protocol': 'up'})
    return results

def parse_config(config_text):
    parsed_data = {'hostname': 'N/A', 'version': 'N/A', 'interfaces': []}
    match = re.search(r'/system identity set name=(.*)', config_text)
    if match:
        parsed_data['hostname'] = match.group(1).strip('"')
    return parsed_data

def parse_vlans(vlan_output):
    vlan_list = []
    matches = re.finditer(r'name="([^"]+)" .*?vlan-id=(\d+)', vlan_output, re.DOTALL)
    for match in matches:
        vlan_list.append({'name': match.group(1), 'id': match.group(2), 'status': 'active'})
    return vlan_list