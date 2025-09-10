# logic/mass_commands.py
"""
Módulo para a lógica de execução de comandos em massa.
"""
from tkinter import messagebox
from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException
import threading

def run_mass_commands(app):
    """
    Executa um comando em todos os dispositivos selecionados na página de Comandos em Massa.
    Usa threading para não bloquear a interface gráfica durante a execução.
    """
    mass_commands_page = app.frames[app.pages["MassCommandsPage"]]
    
    # Obtém os dispositivos selecionados
    selected_devices = []
    for device_id, var in mass_commands_page.device_vars.items():
        if var.get(): # Se a checkbox estiver marcada
            device_details = next((d for d in app.inventory if d['id'] == device_id), None)
            if device_details:
                selected_devices.append(device_details)

    command_to_run = mass_commands_page.command_entry.get("1.0", "end-1c").strip()

    if not selected_devices:
        messagebox.showwarning("Nenhuma Seleção", "Por favor, selecione pelo menos um dispositivo.")
        return
        
    if not command_to_run:
        messagebox.showwarning("Comando Vazio", "Por favor, insira um comando para executar.")
        return

    # Limpa a área de resultados e desativa o botão para evitar cliques duplos
    mass_commands_page.results_text.delete('1.0', 'end')
    mass_commands_page.run_button.config(state="disabled")
    app.status_label.config(text=f"A executar em {len(selected_devices)} dispositivo(s)...")

    # Executa a lógica de conexão numa thread separada
    thread = threading.Thread(target=execute_in_background, args=(app, selected_devices, command_to_run))
    thread.start()


def execute_in_background(app, selected_devices, command_to_run):
    """
    Função que corre em segundo plano para se conectar aos dispositivos e executar os comandos.
    """
    mass_commands_page = app.frames[app.pages["MassCommandsPage"]]
    final_results = ""

    for device in selected_devices:
        header = f"--- RESULTADOS PARA: {device['name']} ({device['host']}) ---\n"
        final_results += header
        
        vendor_module = app.VENDOR_MODULES.get(device['type_name'])
        if not vendor_module:
            final_results += "ERRO: Tipo de dispositivo não suportado.\n\n"
            continue

        # Monta os detalhes da conexão
        conn_details = device.copy()
        conn_details['device_type'] = vendor_module.device_type
        
        try:
            if not app.sim_mode.get():
                with ConnectHandler(**conn_details) as net_connect:
                    output = net_connect.send_command(command_to_run)
                    final_results += output + "\n\n"
            else: # Modo Simulação
                time.sleep(1) # Simula o atraso da rede
                output = f"Saída simulada para o comando '{command_to_run}' em {device['name']}."
                final_results += output + "\n\n"

        except Exception as e:
            final_results += f"ERRO AO CONECTAR: {e}\n\n"

    # Após terminar o loop, atualiza a GUI a partir da thread principal
    app.after(0, update_gui_with_results, app, final_results)

def update_gui_with_results(app, results):
    """Atualiza a interface gráfica com os resultados. Deve ser chamado pela thread principal."""
    mass_commands_page = app.frames[app.pages["MassCommandsPage"]]
    mass_commands_page.results_text.delete('1.0', 'end')
    mass_commands_page.results_text.insert('1.0', results)
    mass_commands_page.run_button.config(state="normal")
    app.status_label.config(text="Execução de comandos em massa concluída.")

# Import 'time' para a simulação
import time