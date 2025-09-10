# vendors/cisco_ios.py
import re

device_type = "cisco_ios"

def get_config_commands():
    return {"running": "show running-config", "vlans": "show vlan brief"}

def get_show_commands():
    """Retorna um dicionário de comandos 'show' de verificação."""
    return {
        'version': 'show version',
        'ip_brief': 'show ip interface brief',
        'neighbors': 'show cdp neighbor',
        'static_routes': 'show ip route static',
        'acls': 'show ip access-lists'
    }
    
def get_static_route_config_commands(network, mask, nexthop):
    return [f"ip route {network} {mask} {nexthop}"]

def get_interface_config_commands(interface_name, description, status, vlan_id=None):
    commands = [f"interface {interface_name}"]
    if description: commands.append(f"description {description}")
    else: commands.append("no description")
    if vlan_id: commands.append("switchport mode access"); commands.append(f"switchport access vlan {vlan_id}")
    commands.append("no shutdown" if status == "on" else "shutdown")
    return commands

def get_vlan_config_commands(vlan_id, vlan_name):
    return [f"vlan {vlan_id}", f"name {vlan_name}"]
    
def get_acl_rule_config_commands(acl_name, rule_details):
    command = (f"access-list {acl_name} {rule_details['action']} {rule_details['protocol']} "
               f"{rule_details['source']} {rule_details['destination']} {rule_details['options']}")
    return [command.strip()]

def check_compliance(config_text):
    """Verifica a configuração contra um conjunto de regras de conformidade."""
    results = []
    
    # Regra 1: Verificar se NTP está configurado
    if re.search(r"^ntp server ", config_text, re.MULTILINE):
        results.append({'rule': 'NTP Configurado', 'status': 'Conforme', 'details': 'Servidor NTP encontrado.'})
    else:
        results.append({'rule': 'NTP Configurado', 'status': 'Não Conforme', 'details': 'Nenhum comando "ntp server" encontrado.'})
        
    # Adicionar mais regras aqui no futuro
    return results

def parse_version(text):
    """Analisa a saída do 'show version' para extrair modelo e versão do IOS."""
    version_match = re.search(r"Cisco IOS Software,.*? Version ([\w\.\(\)SE]+),", text)
    model_match = re.search(r"cisco (\S+) .* memory.", text, re.IGNORECASE)
    
    return {
        "version": version_match.group(1) if version_match else "N/A",
        "model": model_match.group(1) if model_match else "N/A"
    }

def parse_acl_rules(acl_name, acl_type, text):
    """Analisa o texto e extrai as regras de uma ACL específica."""
    results = []
    in_acl_block = False
    pattern = re.compile(r"^\s*(\d+)\s+(permit|deny)\s+(\S+)\s+(any|host \S+|\S+\s\S+)\s+(any|host \S+|\S+\s\S+)(.*)")
    
    for line in text.strip().splitlines():
        if acl_type in line and acl_name in line:
            in_acl_block = True
            continue
        if in_acl_block and ("access list" in line or line.strip() == ""):
            in_acl_block = False
            break
        
        if in_acl_block:
            match = pattern.match(line)
            if match:
                results.append({
                    'id_term': match.group(1),
                    'action': match.group(2),
                    'protocol': match.group(3),
                    'source': match.group(4).strip(),
                    'destination': match.group(5).strip(),
                    'options': match.group(6).strip()
                })
    return results

def parse_acls(text):
    results = []
    pattern = re.compile(r"^(Standard|Extended) IP access list (\S+)")
    for line in text.strip().splitlines():
        match = pattern.match(line)
        if match:
            results.append({'type': match.group(1), 'name_id': match.group(2)})
    return results

def parse_static_routes(text):
    results = []
    pattern = re.compile(r"S\s+([\d\.]+/\d+|[\d\.]+\s+[\d\.]+)\s+.*?via\s+([\d\.]+)")
    for line in text.strip().splitlines():
        match = pattern.search(line)
        if match:
            destination = match.group(1).replace(" ", "/")
            results.append({'destination': destination, 'next_hop': match.group(2)})
    return results

def parse_ip_brief(text):
    results = []
    lines = text.strip().splitlines()
    pattern = re.compile(r"^(\S+)\s+([\d\.]+|unassigned)\s+\w+\s+\w+\s+(up|down|administratively down)\s+(up|down)")
    for line in lines:
        match = pattern.match(line)
        if match:
            status = "admin down" if "administratively down" in match.group(3) else match.group(3)
            results.append({'interface': match.group(1), 'ip_address': match.group(2), 'status': status, 'protocol': match.group(4)})
    return results

def parse_config(config_text):
    parsed_data = {'hostname': 'N/A', 'version': 'N/A', 'interfaces': []}
    match = re.search(r"hostname (\S+)", config_text)
    if match: parsed_data['hostname'] = match.group(1)
    match = re.search(r"version (\d+\.\d+)", config_text)
    if match: parsed_data['version'] = match.group(1)
    interface_blocks = re.findall(r"(interface \S+.*?)(?=!|$)", config_text, re.DOTALL)
    for block in interface_blocks:
        if_name_match = re.search(r"interface (\S+)", block)
        if if_name_match:
            if_name = if_name_match.group(1)
            ip_addr, status, description, access_vlan = "N/A", "shutdown", "", "N/A"
            ip_match = re.search(r"ip address (\S+) (\S+)", block)
            if ip_match: ip_addr = f"{ip_match.group(1)} / {ip_match.group(2)}"
            desc_match = re.search(r"description (.*)", block)
            if desc_match: description = desc_match.group(1).strip()
            vlan_match = re.search(r"switchport access vlan (\d+)", block)
            if vlan_match: access_vlan = vlan_match.group(1)
            if "no shutdown" in block: status = "no shutdown"
            parsed_data['interfaces'].append(
                {'name': if_name, 'ip': ip_addr, 'status': status, 'description': description, 'access_vlan': access_vlan})
    return parsed_data

def parse_vlans(vlan_output):
    vlan_list = []
    pattern = re.compile(r"^(\d+)\s+([\w-]+)\s+(active|suspend|act/unsup)", re.MULTILINE)
    matches = pattern.findall(vlan_output)
    for match in matches:
        vlan_list.append({'id': match[0], 'name': match[1], 'status': match[2]})
    return vlan_list