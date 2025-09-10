# logic/configuration.py
"""
Módulo para a lógica de envio de configurações e ações.
"""
from tkinter import messagebox, filedialog
from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException
from .connection import get_connection_details # Importa a função auxiliar

def send_commands(app, commands, success_message):
    """Função genérica para conectar e enviar uma lista de comandos."""
    if app.sim_mode.get():
        messagebox.showinfo("Simulação de Comandos", "Os seguintes comandos seriam enviados:\n\n" + "\n".join(commands))
        app.status_label.config(text=f"Modo Simulação: {success_message}")
        return True # Indica sucesso na simulação

    device = get_connection_details(app)
    if not device: return False

    app.status_label.config(text=f"Enviando comandos para {device['host']}..."); app.update_idletasks()
    try:
        with ConnectHandler(**device) as net_connect:
            output = net_connect.send_config_set(commands)
            messagebox.showinfo("Sucesso", f"{success_message}\n\nSaída:\n{output}")
        app.status_label.config(text="Comandos enviados com sucesso.")
        return True
    except (NetmikoAuthenticationException, NetmikoTimeoutException, Exception) as e:
        messagebox.showerror("Erro ao Enviar Comandos", f"Ocorreu um erro: {e}")
        app.status_label.config(text="Erro ao enviar comandos.")
        return False

def save_configuration(app):
    """Salva a configuração ativa na configuração de inicialização."""
    if app.sim_mode.get():
        messagebox.showinfo("Simulação", "Configuração seria salva agora (write memory / commit).")
        app.status_label.config(text="Modo Simulação: Configuração salva.")
        return

    device = get_connection_details(app)
    if not device: return
    
    if not messagebox.askyesno("Confirmação", "Tem certeza que deseja salvar a configuração atual no dispositivo? Esta ação é permanente."):
        return

    app.status_label.config(text=f"Salvando configuração em {device['host']}..."); app.update_idletasks()
    try:
        with ConnectHandler(**device) as net_connect:
            output = net_connect.save_config()
            messagebox.showinfo("Sucesso", f"Configuração salva com sucesso!\n\n{output}")
        app.status_label.config(text="Configuração salva com sucesso.")
    except (NetmikoAuthenticationException, NetmikoTimeoutException, Exception) as e:
        messagebox.showerror("Erro ao Salvar", f"Ocorreu um erro: {e}")
        app.status_label.config(text="Erro ao salvar.")

def export_configuration(app):
    """Busca a configuração atual e a salva em um arquivo de texto."""
    config_text = app.raw_command_outputs.get("running", "").strip()
    if not config_text:
        messagebox.showwarning("Aviso", "Não há configuração para exportar. Conecte a um dispositivo primeiro.")
        return
    hostname = app.frames[app.pages["OverviewPage"]].hostname_value.cget("text")
    if hostname == "N/A" or not hostname: hostname = "backup"
    from datetime import datetime
    suggested_filename = f"{hostname}_{datetime.now().strftime('%Y-%m-%d')}.txt"
    filepath = filedialog.asksaveasfilename(initialfile=suggested_filename, defaultextension=".txt", filetypes=[("Arquivos de Texto", "*.txt"), ("Todos os Arquivos", "*.*")])
    if not filepath: return
    try:
        with open(filepath, 'w', encoding='utf-8') as f: f.write(config_text)
        messagebox.showinfo("Sucesso", f"Configuração exportada com sucesso para:\n{filepath}")
    except Exception as e:
        messagebox.showerror("Erro ao Salvar Arquivo", f"Não foi possível salvar o arquivo.\nErro: {e}")

def restore_configuration(app):
    """Abre um ficheiro de configuração e aplica-o ao dispositivo selecionado."""
    device_details = get_connection_details(app)
    if not device_details: return

    filepath = filedialog.askopenfilename(
        title="Selecionar ficheiro de backup para restaurar",
        filetypes=[("Arquivos de Texto", "*.txt"), ("Todos os Arquivos", "*.*")]
    )
    if not filepath:
        return

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            commands_to_send = f.read().splitlines()
            commands_to_send = [cmd for cmd in commands_to_send if cmd.strip() and not cmd.strip().startswith('!')]
    except Exception as e:
        messagebox.showerror("Erro ao Ler Ficheiro", f"Não foi possível ler o ficheiro de configuração:\n{e}")
        return

    if not commands_to_send:
        messagebox.showwarning("Ficheiro Vazio", "O ficheiro de configuração selecionado está vazio ou não contém comandos válidos.")
        return

    confirmation_message = (f"Você está prestes a aplicar {len(commands_to_send)} comandos ao dispositivo "
                            f"'{device_details['name']}' ({device_details['host']}).\n\n"
                            "ESTA AÇÃO PODE SOBRESCREVER A CONFIGURAÇÃO EXISTENTE.\n\n"
                            "Deseja continuar?")

    if messagebox.askyesno("CONFIRMAÇÃO CRÍTICA", confirmation_message, icon='warning'):
        send_commands(app, commands_to_send, "Configuração restaurada com sucesso a partir do ficheiro.")


def configure_interface(app):
    vendor_module = app.get_selected_vendor_module()
    if not vendor_module: return
    interface_page = app.frames[app.pages["InterfacesPage"]]
    if not interface_page.selected_interface_name:
        messagebox.showwarning("Aviso", "Nenhuma interface selecionada."); return
    
    vlan_id_or_name = None
    device_details = get_connection_details(app)
    if device_details and "Switch" in device_details.get('type_name', ''):
        selected_vlan = interface_page.vlan_combobox.get()
        if selected_vlan and selected_vlan != "Nenhuma": vlan_id_or_name = selected_vlan.split(' ')[0]

    commands = vendor_module.get_interface_config_commands(
        interface_name=interface_page.selected_interface_name,
        description=interface_page.entry_if_desc.get(),
        status=interface_page.if_status_var.get(),
        vlan_id=vlan_id_or_name
    )
    send_commands(app, commands, f"Interface {interface_page.selected_interface_name} configurada.")

def create_vlan(app):
    vendor_module = app.get_selected_vendor_module();
    if not vendor_module: return
    vlan_page = app.frames[app.pages["VlansPage"]]
    vlan_id_str = vlan_page.entry_vlan_id.get(); vlan_name = vlan_page.entry_vlan_name.get()
    if not vlan_id_str or not vlan_name: messagebox.showerror("Erro", "ID e Nome são obrigatórios."); return
    try:
        vlan_id = int(vlan_id_str);
        if not 2 <= vlan_id <= 4094: raise ValueError
    except ValueError:
        messagebox.showerror("Erro de Validação", "O ID da VLAN deve ser um número entre 2 e 4094."); return
    
    commands = vendor_module.get_vlan_config_commands(vlan_id, vlan_name)
    send_commands(app, commands, f"VLAN {vlan_id} criada/atualizada.")

def add_static_route(app):
    vendor_module = app.get_selected_vendor_module();
    if not vendor_module: return
    routing_page = app.frames[app.pages["RoutingPage"]]
    network = routing_page.entry_route_net.get(); mask_prefix = routing_page.entry_route_mask.get(); nexthop = routing_page.entry_route_nexthop.get()
    if not all([network, mask_prefix, nexthop]): messagebox.showerror("Erro", "Todos os campos da rota são obrigatórios."); return
    
    commands = vendor_module.get_static_route_config_commands(network, mask_prefix, nexthop)
    send_commands(app, commands, "Rota estática adicionada.")

def add_acl_rule(app):
    vendor_module = app.get_selected_vendor_module()
    if not vendor_module:
        messagebox.showerror("Erro", "Tipo de dispositivo inválido.")
        return

    security_page = app.frames[app.pages["SecurityPage"]]
    
    acl_name = security_page.selected_acl.get()
    if not acl_name or acl_name == "Selecione uma ACL...":
        messagebox.showerror("Erro", "Você precisa selecionar uma ACL/Filtro para adicionar a regra.")
        return

    acl_name_id = acl_name.split('(')[0].strip()
        
    rule_details = {
        "action": security_page.action_var.get(),
        "protocol": security_page.proto_var.get(),
        "source": security_page.source_entry.get(),
        "destination": security_page.dest_entry.get(),
        "options": security_page.options_entry.get(),
    }
    
    if not all([rule_details['action'], rule_details['protocol'], rule_details['source'], rule_details['destination']]):
        messagebox.showerror("Erro", "Ação, Protocolo, Origem e Destino são obrigatórios.")
        return

    commands = vendor_module.get_acl_rule_config_commands(acl_name_id, rule_details)
    send_commands(app, commands, f"Regra adicionada à ACL {acl_name_id}.")