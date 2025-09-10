# logic/alerts_manager.py
"""
Módulo para gerir a definição e verificação de regras de alerta.
"""
import json
import time
from tkinter import messagebox

ALERTS_FILE = "alerts.json"

def load_alert_rules():
    """Carrega as regras de alerta do ficheiro JSON."""
    try:
        with open(ALERTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        messagebox.showerror("Erro de Alertas", f"O ficheiro {ALERTS_FILE} está corrompido.")
        return []

def save_alert_rules(rules):
    """Salva la lista de regras de alerta no ficheiro JSON."""
    try:
        with open(ALERTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(rules, f, indent=4)
    except Exception as e:
        messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar as regras de alerta: {e}")

def add_alert_rule(rule_details):
    """Adiciona uma nova regra de alerta."""
    rules = load_alert_rules()
    rule_details['id'] = int(time.time() * 1000)
    rules.append(rule_details)
    save_alert_rules(rules)

def remove_alert_rule(rule_id):
    """Remove uma regra de alerta pelo seu ID."""
    rules = load_alert_rules()
    rules = [rule for rule in rules if rule.get('id') != rule_id]
    save_alert_rules(rules)

def check_alerts(app, device_id, parsed_data):
    """Verifica os dados recolhidos contra as regras de alerta definidas."""
    rules = load_alert_rules()
    triggered_alerts = []

    for rule in rules:
        if rule.get('device_id') == device_id:
            # Lógica para a regra "Interface Status"
            if rule['metric'] == 'Interface Status':
                interfaces = parsed_data.get('interfaces', [])
                for interface in interfaces:
                    if interface['name'] == rule['interface_name']:
                        actual_status = interface['status']
                        expected_status = rule['value']
                        condition = rule['condition']
                        
                        if condition == 'not equals' and actual_status != expected_status:
                            alert_message = (f"ALERTA: Interface '{interface['name']}' no dispositivo "
                                             f"'{rule['device_name']}' está com o estado '{actual_status}', "
                                             f"mas o esperado era '{expected_status}'.")
                            triggered_alerts.append(alert_message)
    
    if triggered_alerts:
        app.after(0, show_alert_popup, "\n\n".join(triggered_alerts))

def show_alert_popup(message):
    messagebox.showwarning("Alerta de Monitorização", message)