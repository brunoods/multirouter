# logic/connection.py
"""
Módulo para a lógica de conexão e leitura de dados dos dispositivos.
"""
import time
from tkinter import messagebox
from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException
from logic.inventory_manager import update_device

def get_connection_details(app):
    """Coleta os detalhes de conexão da GUI e retorna um dicionário."""
    selected_name = app.device_combobox.get()
    if not selected_name or "Nenhum dispositivo" in selected_name:
        if not getattr(app, 'is_monitoring', False):
            messagebox.showwarning("Nenhum Dispositivo", "Por favor, adicione um dispositivo no Inventário e selecione-o.")
        return None
        
    device_details = next((d for d in app.inventory if d['name'] == selected_name), None)
    if not device_details:
        if not getattr(app, 'is_monitoring', False):
            messagebox.showerror("Erro", "Dispositivo selecionado não encontrado no inventário.")
        return None

    vendor_module = app.get_selected_vendor_module()
    if not vendor_module:
        return None

    conn_details = device_details.copy()
    conn_details['device_type'] = vendor_module.device_type
    return conn_details


def connect_and_read_config(app, is_monitoring_thread=False, alert_callback=None):
    """Função de lógica para conectar e ler dados do dispositivo."""
    app.is_monitoring = is_monitoring_thread

    if not is_monitoring_thread:
        app.raw_command_outputs.clear()
    
    vendor_module = app.get_selected_vendor_module()
    if not vendor_module: 
        if not is_monitoring_thread: messagebox.showerror("Erro", "Tipo de dispositivo inválido.")
        return

    device_details_for_connect = get_connection_details(app)
    if not device_details_for_connect: return
    
    raw_config, vlan_output, static_routes_output, acls_output, version_info_raw, ip_brief_output = (None,) * 6

    # Lógica de Conexão Real
    if not app.sim_mode.get():
        try:
            if not is_monitoring_thread:
                app.status_label.config(text=f"Conectando a {device_details_for_connect['host']}..."); app.update_idletasks()
            
            with ConnectHandler(**device_details_for_connect) as net_connect:
                if not is_monitoring_thread:
                    app.status_label.config(text="Conectado! Lendo dados..."); app.update_idletasks()
                
                read_commands = vendor_module.get_config_commands()
                show_commands = vendor_module.get_show_commands()

                raw_config = net_connect.send_command(read_commands.get("running", ""))
                version_info_raw = net_connect.send_command(show_commands.get("version", ""))
                ip_brief_output = net_connect.send_command(show_commands.get("ip_brief", ""))
                
                app.raw_command_outputs['running'] = raw_config
                app.raw_command_outputs['acls'] = net_connect.send_command(show_commands.get("acls", "")) if "acls" in show_commands else None

                if version_info_raw and hasattr(vendor_module, 'parse_version'):
                    version_details = vendor_module.parse_version(version_info_raw)
                    device_to_update = {
                        'id': device_details_for_connect['id'],
                        'os_version': version_details.get('version', 'N/A'),
                        'model': version_details.get('model', 'N/A')
                    }
                    update_device(device_to_update)
                    app.after(0, app.update_connection_menu)
        
        except Exception as e:
            if is_monitoring_thread:
                app.after(0, app.status_label.config, {'text': f"Erro de monitorização: {e}"})
            else:
                messagebox.showerror("Erro de Conexão", f"Ocorreu um erro: {e}")
                app.status_label.config(text="Erro de conexão.")
            return
            
    # Lógica de Simulação
    else:
        if not is_monitoring_thread:
            app.status_label.config(text="Simulando Conexão..."); app.update_idletasks(); time.sleep(1)
        
        device_name = device_details_for_connect.get('type_name', '')
        if "Cisco" in device_name:
            raw_config = "hostname Cisco-Simulado\ninterface GigabitEthernet0/1\n shutdown"
            ip_brief_output = "Interface IP-Address OK? Method Status Protocol\nGi0/0 192.168.1.1 YES manual up up\nGi0/1 unassigned YES manual administratively down down\n"
        
        app.raw_command_outputs['running'] = raw_config
        app.raw_command_outputs['acls'] = "Extended IP access list 101\n 10 permit ip any any"

    # --- Processamento e Callback de Alerta ---
    parsed_data_for_alerts = {}
    if ip_brief_output and hasattr(vendor_module, 'parse_ip_brief'):
        parsed_data_for_alerts['interfaces'] = vendor_module.parse_ip_brief(ip_brief_output)
    
    if is_monitoring_thread and alert_callback:
        alert_callback(app, device_details_for_connect['id'], parsed_data_for_alerts)

    # --- Atualização da GUI ---
    def update_gui():
        # A atualização completa da GUI só é necessária em cliques manuais
        if not is_monitoring_thread:
            device_name = device_details_for_connect.get('type_name', '')
            is_switch = "Switch" in device_name
            
            parsed_config = vendor_module.parse_config(raw_config) if raw_config is not None else {}
            parsed_vlans = vendor_module.parse_vlans(vlan_output) if is_switch and vlan_output is not None else []
            parsed_routes = vendor_module.parse_static_routes(static_routes_output) if static_routes_output is not None and hasattr(vendor_module, 'parse_static_routes') else []
            parsed_acls = vendor_module.parse_acls(app.raw_command_outputs['acls']) if app.raw_command_outputs.get('acls') and hasattr(vendor_module, 'parse_acls') else []
            
            app.update_overview_page(parsed_config, parsed_vlans, parsed_routes, parsed_acls)
        
        app.status_label.config(text=f"Dados atualizados às {time.strftime('%H:%M:%S')}.")
    
    app.after(0, update_gui)
    app.is_monitoring = False