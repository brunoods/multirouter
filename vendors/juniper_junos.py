# vendors/juniper_junos.py
import re
import time

device_type = "juniper_junos"

def get_config_commands():
    return {"running": "show configuration", "vlans": "show vlans"}

def get_show_commands():
    """Retorna um dicionário de comandos 'show' de verificação."""
    return {
        'version': 'show version',
        'ip_brief': 'show interfaces terse',
        'neighbors': 'show lldp neighbors',
        'static_routes': 'show route protocol static',
        'acls': 'show configuration firewall'
    }

def check_compliance(config_text):
    """Verifica a configuração contra um conjunto de regras de conformidade."""
    results = []
    
    # Regra 1: Verificar se NTP está configurado
    if re.search(r"ntp {\s+server", config_text, re.MULTILINE):
        results.append({'rule': 'NTP Configurado', 'status': 'Conforme', 'details': 'Configuração de NTP encontrada.'})
    else:
        results.append({'rule': 'NTP Configurado', 'status': 'Não Conforme', 'details': 'Nenhuma configuração de NTP encontrada em [system ntp].'})
        
    return results

def get_static_route_config_commands(network, prefix, nexthop):
    return [f"set routing-options static route {network}/{prefix} next-hop {nexthop}"]

def get_interface_config_commands(interface_name, description, status, vlan_name=None):
    commands = []
    if status == "off": commands.append(f"set interfaces {interface_name} disable")
    else: commands.append(f"delete interfaces {interface_name} disable")
    if description: commands.append(f'set interfaces {interface_name} description "{description}"')
    else: commands.append(f'delete interfaces {interface_name} description')
    if vlan_name: commands.append(f"set interfaces {interface_name} unit 0 family ethernet-switching vlan members {vlan_name}")
    return commands

def get_vlan_config_commands(vlan_id, vlan_name):
    return [f"set vlans {vlan_name} vlan-id {vlan_id}"]

def get_acl_rule_config_commands(filter_name, rule_details):
    term_name = f"term-{int(time.time())}"
    base_command = f"set firewall family inet filter {filter_name} term {term_name}"
    commands = []
    if rule_details.get("source") and rule_details["source"] != 'any':
        commands.append(f"{base_command} from source-address {rule_details['source']}")
    if rule_details.get("destination") and rule_details["destination"] != 'any':
        commands.append(f"{base_command} from destination-address {rule_details['destination']}")
    if rule_details.get("protocol") and rule_details["protocol"] != 'ip':
        commands.append(f"{base_command} from protocol {rule_details['protocol']}")
    commands.append(f"{base_command} then {rule_details['action']}")
    return commands

def parse_version(text):
    """Analisa a saída do 'show version' para extrair modelo e versão do Junos."""
    version_match = re.search(r"Junos: ([\w\.\-]+)", text)
    model_match = re.search(r"Model: (\S+)", text)
    return {
        "version": version_match.group(1) if version_match else "N/A",
        "model": model_match.group(1) if model_match else "N/A"
    }

def parse_acl_rules(filter_name, filter_type, text):
    results = []
    try:
        filter_block_match = re.search(r'filter ' + re.escape(filter_name) + r' {(.*?)}', text, re.DOTALL)
        if not filter_block_match: return []
        filter_block = filter_block_match.group(1)
        term_blocks = re.finditer(r'term (\S+) {(.*?)}', filter_block, re.DOTALL)
        for term_match in term_blocks:
            term_name = term_match.group(1)
            term_content = term_match.group(2)
            from_match = re.search(r'from {(.*?)}', term_content, re.DOTALL)
            from_content = from_match.group(1).strip() if from_match else "any"
            then_match = re.search(r'then {(.*?)}', term_content, re.DOTALL)
            then_content = then_match.group(1).strip() if then_match else "N/A"
            results.append({
                'id_term': term_name, 'action': then_content, 'protocol': 'any',
                'source': from_content.replace('\n', ' '), 'destination': 'any', 'options': ''
            })
    except Exception:
        pass
    return results

def parse_acls(text):
    results = []
    pattern = re.compile(r"filter (\S+)")
    for line in text.strip().splitlines():
        match = pattern.search(line)
        if match:
            results.append({'type': 'Filter', 'name_id': match.group(1)})
    return results

def parse_static_routes(text):
    results = []
    pattern = re.compile(r"(\S+/\d+)\s+.*?to\s+([\d\.]+)\s+via")
    for match in pattern.finditer(text):
        results.append({'destination': match.group(1), 'next_hop': match.group(2)})
    return results

def parse_ip_brief(text):
    results = []
    lines = text.strip().splitlines()
    pattern = re.compile(r"^(\S+\.\d+)\s+(up|down)\s+(up|down)\s+\w+\s+(\S+)")
    for line in lines:
        match = pattern.match(line)
        if match:
            results.append({'interface': match.group(1), 'ip_address': match.group(4), 'status': match.group(2), 'protocol': match.group(3)})
    return results

def parse_config(config_text):
    parsed_data = {'hostname': 'N/A', 'version': 'N/A', 'interfaces': []}
    match = re.search(r"host-name (\S+);", config_text)
    if match: parsed_data['hostname'] = match.group(1)
    for block in re.finditer(r'(\S+-(\d+/\d+/\d+)) {', config_text):
        if_name = block.group(1)
        if_details_match = re.search(r'interface ' + re.escape(if_name) + r' {(.*?)}', config_text, re.DOTALL)
        if_details = if_details_match.group(1) if if_details_match else ""
        description_match = re.search(r'description "(.*?)";', if_details)
        description = description_match.group(1) if description_match else ""
        status = "shutdown" if "disable;" in if_details else "no shutdown"
        vlan_match = re.search(r'vlan members (\S+);', if_details)
        access_vlan = vlan_match.group(1).strip() if vlan_match else "N/A"
        parsed_data['interfaces'].append({'name': if_name, 'ip': 'N/A', 'status': status, 'description': description, 'access_vlan': access_vlan})
    return parsed_data

def parse_vlans(vlan_output):
    vlan_list = []
    pattern = re.compile(r"^([\w-]+)\s+(\d+)", re.MULTILINE)
    matches = pattern.findall(vlan_output)
    for match in matches:
        vlan_list.append({'name': match[0], 'id': match[1], 'status': 'active'})
    return vlan_list