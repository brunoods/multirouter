# logic/discovery_manager.py
"""
Módulo para a lógica de descoberta de dispositivos na rede.
"""
import nmap
import threading
from tkinter import messagebox
from netmiko import ConnectHandler
from logic.inventory_manager import add_device, load_inventory

def start_discovery(app):
    """Inicia o processo de descoberta de rede numa thread separada."""
    discovery_page = app.frames[app.pages["DiscoveryPage"]]
    
    network_range = discovery_page.network_entry.get().strip()
    username = discovery_page.user_entry.get().strip()
    password = discovery_page.pass_entry.get().strip()
    
    if not network_range or not username or not password:
        messagebox.showwarning("Dados Incompletos", "Rede, Utilizador e Senha são obrigatórios.")
        return

    discovery_page.run_button.config(state="disabled")
    discovery_page.progress_bar.start()
    app.status_label.config(text=f"A iniciar varredura na rede {network_range}...")
    
    # Executa a lógica de descoberta numa thread para não bloquear a GUI
    thread = threading.Thread(target=discover_in_background, args=(app, network_range, username, password))
    thread.start()

def discover_in_background(app, network_range, username, password):
    """Função que corre em segundo plano para descobrir e identificar dispositivos."""
    discovery_page = app.frames[app.pages["DiscoveryPage"]]
    
    # Atualiza a GUI a partir da thread principal
    def update_log(message):
        discovery_page.log_text.config(state="normal")
        discovery_page.log_text.insert("end", message + "\n")
        discovery_page.log_text.see("end")
        discovery_page.log_text.config(state="disabled")

    try:
        app.after(0, update_log, "Passo 1: A procurar por anfitriões ativos (Ping Scan)...")
        nm = nmap.PortScanner()
        # -sn: Ping Scan - desativa a descoberta de portas
        nm.scan(hosts=network_range, arguments='-sn')
        
        active_hosts = nm.all_hosts()
        if not active_hosts:
            app.after(0, update_log, "Nenhum anfitrião ativo encontrado na gama especificada.")
            app.after(0, stop_discovery_gui, app)
            return

        app.after(0, update_log, f"Passo 2: Encontrados {len(active_hosts)} anfitriões ativos. A tentar identificar...")
        
        inventory = load_inventory()
        existing_ips = [dev['host'] for dev in inventory]
        
        for host in active_hosts:
            if host in existing_ips:
                app.after(0, update_log, f"-> {host} já existe no inventário. A ignorar.")
                continue

            app.after(0, update_log, f"-> Tentando conectar a {host}...")
            
            # Tenta conectar com cada tipo de dispositivo conhecido
            device_identified = False
            for type_name, vendor_module in app.VENDOR_MODULES.items():
                if "Roteador" not in type_name and "Switch" not in type_name: continue # Evita duplicados
                
                conn_details = {
                    'device_type': vendor_module.device_type,
                    'host': host,
                    'username': username,
                    'password': password,
                    'conn_timeout': 5 # Timeout curto para a descoberta
                }
                
                try:
                    with ConnectHandler(**conn_details) as net_connect:
                        # Se a conexão for bem-sucedida, o dispositivo é compatível
                        app.after(0, update_log, f"   SUCESSO! Dispositivo {host} identificado como {type_name}.")
                        
                        # Coleta detalhes
                        hostname = net_connect.find_prompt().replace(">", "").replace("#", "")
                        
                        # Adiciona ao inventário
                        new_device = {
                            'name': hostname,
                            'host': host,
                            'type_name': type_name,
                            'username': username,
                            'password': password
                        }
                        add_device(new_device)
                        app.after(0, update_log, f"   Dispositivo '{hostname}' adicionado ao inventário.")
                        device_identified = True
                        break # Para de tentar outros tipos de dispositivo
                
                except Exception:
                    # Falha silenciosa, apenas tenta o próximo tipo
                    continue
            
            if not device_identified:
                app.after(0, update_log, f"   FALHA: Não foi possível conectar a {host} com as credenciais fornecidas ou não é um dispositivo suportado.")

    except Exception as e:
        app.after(0, update_log, f"ERRO CRÍTICO DURANTE A DESCOBERTA: {e}")

    app.after(0, stop_discovery_gui, app)

def stop_discovery_gui(app):
    """Para os elementos visuais de progresso na GUI."""
    discovery_page = app.frames[app.pages["DiscoveryPage"]]
    discovery_page.progress_bar.stop()
    discovery_page.run_button.config(state="normal")
    app.status_label.config(text="Descoberta de rede concluída.")
    app.update_connection_menu() # Atualiza o menu principal com os novos dispositivos