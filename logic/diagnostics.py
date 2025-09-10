# logic/diagnostics.py
"""
Módulo para a lógica de execução de comandos de diagnóstico como ping e traceroute.
"""
import time
import threading
from tkinter import messagebox
from netmiko import ConnectHandler
from .connection import get_connection_details

def run_diagnostic_command(app, command_type):
    """
    Prepara e inicia a execução de um comando de diagnóstico numa thread separada.
    """
    diagnostics_page = app.frames[app.pages["DiagnosticsPage"]]
    
    target_ip = diagnostics_page.target_ip_entry.get().strip()
    if not target_ip:
        messagebox.showwarning("Destino Vazio", "Por favor, insira um endereço IP de destino.")
        return
        
    device_details = get_connection_details(app)
    if not device_details:
        # get_connection_details já mostra um aviso, então não precisamos de outro.
        return

    vendor_module = app.get_selected_vendor_module()
    if not vendor_module or not hasattr(vendor_module, 'get_diagnostic_commands'):
        messagebox.showerror("Erro", "Módulo do fabricante não suporta comandos de diagnóstico.")
        return

    diag_commands = vendor_module.get_diagnostic_commands(target_ip)
    command_to_run = diag_commands.get(command_type)

    if not command_to_run:
        messagebox.showwarning("Não Suportado", f"O comando '{command_type}' não é suportado por este dispositivo.")
        return

    # Limpa a área de resultados e desativa botões
    diagnostics_page.results_text.config(state="normal")
    diagnostics_page.results_text.delete('1.0', 'end')
    diagnostics_page.ping_button.config(state="disabled")
    diagnostics_page.trace_button.config(state="disabled")
    app.status_label.config(text=f"A executar '{command_to_run}' em {device_details['name']}...")

    # Executa a lógica de conexão numa thread para não bloquear a GUI
    thread = threading.Thread(target=execute_diag_in_background, args=(app, device_details, command_to_run))
    thread.start()

def execute_diag_in_background(app, device_details, command_to_run):
    """
    Função que corre em segundo plano para se conectar e executar o comando de diagnóstico.
    """
    result = ""
    try:
        if not app.sim_mode.get():
            with ConnectHandler(**device_details) as net_connect:
                # Usamos send_command_timing para comandos que demoram a responder
                output = net_connect.send_command(command_to_run, read_timeout=120)
                result = output
        else: # Modo Simulação
            time.sleep(3) # Simula um ping/traceroute demorado
            result = f"--- SAÍDA SIMULADA PARA: {command_to_run} ---\n"
            result += "Enviando 5 pacotes de 100 bytes para 8.8.8.8, timeout de 2 segundos:\n"
            result += "!!!!!\n"
            result += "Taxa de sucesso é 100 por cento (5/5)\n"

    except Exception as e:
        result = f"ERRO AO EXECUTAR COMANDO: {e}"

    # Agenda a atualização da GUI a partir da thread principal
    app.after(0, update_diag_gui_with_results, app, result)

def update_diag_gui_with_results(app, result):
    """Atualiza a interface gráfica com os resultados."""
    diagnostics_page = app.frames[app.pages["DiagnosticsPage"]]
    diagnostics_page.results_text.delete('1.0', 'end')
    diagnostics_page.results_text.insert('1.0', result)
    diagnostics_page.results_text.config(state="disabled")
    diagnostics_page.ping_button.config(state="normal")
    diagnostics_page.trace_button.config(state="normal")
    app.status_label.config(text="Comando de diagnóstico concluído.")