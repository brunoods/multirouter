# logic/compliance_manager.py
"""
Módulo para a lógica de execução de auditorias de conformidade.
"""
import threading
from tkinter import messagebox
from netmiko import ConnectHandler
from logic.inventory_manager import load_inventory

def run_compliance_audit(app):
    """
    Inicia a auditoria de conformidade em todos os dispositivos do inventário.
    Usa threading para não bloquear a interface gráfica.
    """
    compliance_page = app.frames[app.pages["CompliancePage"]]
    
    inventory = load_inventory()
    if not inventory:
        messagebox.showwarning("Inventário Vazio", "Não há dispositivos no inventário para auditar.")
        return

    # Limpa resultados antigos e desativa o botão
    compliance_page.tree.delete(*compliance_page.tree.get_children())
    compliance_page.run_button.config(state="disabled")
    app.status_label.config(text=f"A executar auditoria em {len(inventory)} dispositivo(s)...")

    # Executa a lógica de conexão numa thread separada
    thread = threading.Thread(target=execute_audit_in_background, args=(app, inventory))
    thread.start()

def execute_audit_in_background(app, inventory):
    """
    Função que corre em segundo plano para se conectar a cada dispositivo e verificar a conformidade.
    """
    all_results = []

    for device in inventory:
        vendor_module = app.VENDOR_MODULES.get(device['type_name'])
        if not vendor_module:
            all_results.append({'device': device['name'], 'rule': 'Conexão', 'status': 'Falhou', 'details': 'Tipo de dispositivo não suportado.'})
            continue
        
        # Monta os detalhes da conexão
        conn_details = device.copy()
        conn_details['device_type'] = vendor_module.device_type
        
        try:
            raw_config = ""
            if not app.sim_mode.get():
                with ConnectHandler(**conn_details) as net_connect:
                    # Usa o comando de 'running config' definido no módulo do fabricante
                    config_command = vendor_module.get_config_commands().get("running")
                    if config_command:
                        raw_config = net_connect.send_command(config_command)
            else: # Modo Simulação
                if "Cisco" in device['type_name']:
                    raw_config = "hostname Cisco-Simulado\n!\nntp server 1.1.1.1"
                elif "Juniper" in device['type_name']:
                    raw_config = "system { host-name Juniper-Simulado; ntp { server 2.2.2.2; } }"
                elif "Mikrotik" in device['type_name']:
                    raw_config = "/system ntp client set enabled=yes servers=3.3.3.3"

            # Executa a verificação de conformidade
            if hasattr(vendor_module, 'check_compliance'):
                compliance_results = vendor_module.check_compliance(raw_config)
                for result in compliance_results:
                    result['device'] = device['name']
                    all_results.append(result)

        except Exception as e:
            all_results.append({'device': device['name'], 'rule': 'Conexão', 'status': 'Falhou', 'details': f"Erro ao conectar: {e}"})

    # Após terminar o loop, atualiza a GUI a partir da thread principal
    app.after(0, update_gui_with_audit_results, app, all_results)


def update_gui_with_audit_results(app, all_results):
    """Atualiza a interface gráfica com os resultados da auditoria."""
    compliance_page = app.frames[app.pages["CompliancePage"]]
    
    # Limpa a tabela antes de inserir novos resultados
    compliance_page.tree.delete(*compliance_page.tree.get_children())
    
    # Prepara as tags de cor
    compliance_page.tree.tag_configure('Pass', background='#c8e6c9') # Verde
    compliance_page.tree.tag_configure('Fail', background='#ffcdd2') # Vermelho

    for result in all_results:
        status = result.get('status', 'N/A')
        tag = 'Pass' if status == 'Conforme' else 'Fail'
        compliance_page.tree.insert("", "end", values=(
            result.get('device', 'N/A'),
            result.get('rule', 'N/A'),
            status,
            result.get('details', '')
        ), tags=(tag,))
        
    compliance_page.run_button.config(state="normal")
    app.status_label.config(text="Auditoria de conformidade concluída.")