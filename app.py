# 1. Importar as bibliotecas necessárias
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledText
from tkinter import messagebox, Toplevel
import paramiko
# AGORA VAMOS USAR A BIBLIOTECA DA API
import routeros_api

# ----------------------------------------------------------------------------------
# NOVA FUNÇÃO DE CONEXÃO VIA API
# ----------------------------------------------------------------------------------
def conectar_api(ip, usuario, senha):
    """Tenta conectar ao roteador via API e retorna o objeto de conexão."""
    try:
        connection = routeros_api.RouterOsApiPool(
            ip,
            username=usuario,
            password=senha,
            plaintext_login=True
        )
        # Retorna o objeto de API para podermos enviar comandos
        return connection.get_api()
    except Exception as e:
        messagebox.showerror("Erro de Conexão API", f"Não foi possível conectar à API do roteador.\nVerifique IP, utilizador e senha.\n\nErro: {e}")
        return None

# ----------------------------------------------------------------------------------
# FUNÇÃO DO WIZARD ATUALIZADA COM A LÓGICA REAL
# ----------------------------------------------------------------------------------
def aplicar_configuracao_inicial(wizard_window, entries):
    """Recolhe os dados, conecta via API e aplica a configuração inicial."""
    # 1. Recolher os dados do Wizard
    wan_if = entries["interface_wan"].get()
    lan_if = entries["interface_lan"].get()
    lan_ip = entries["ip_da_rede_lan_ex"].get()
    dhcp_pool = entries["pool_dhcp_ex"].get()
    admin_user = entries["novo_utilizador_admin"].get()
    admin_pass = entries["nova_senha_admin"].get()

    if not all([wan_if, lan_if, lan_ip, dhcp_pool, admin_user, admin_pass]):
        messagebox.showwarning("Campos em Falta", "Por favor, preencha todos os campos.", parent=wizard_window)
        return

    # 2. Conectar via API usando os dados da janela principal
    main_ip = entry_ip.get()
    main_user = entry_usuario.get()
    main_pass = entry_senha.get()

    api = conectar_api(main_ip, main_user, main_pass)
    
    # Se a conexão falhar, a função conectar_api já mostra um erro e retorna None
    if not api:
        return
    
    # Exibe na tela de resultado que o processo iniciou
    texto_resultado.delete("1.0", ttk.END)
    texto_resultado.insert(ttk.END, "Conectado com sucesso via API. A aplicar configurações...\n\n")
    texto_resultado.update_idletasks()

    # 3. Executar Comandos Estruturados
    try:
        # Configurar DHCP Client na WAN
        api.get_resource('/ip/dhcp-client').add(interface=wan_if, disabled='no')
        texto_resultado.insert(ttk.END, "1. DHCP Client na WAN... [OK]\n")
        texto_resultado.update_idletasks()

        # Configurar IP da LAN
        api.get_resource('/ip/address').add(address=lan_ip, interface=lan_if)
        texto_resultado.insert(ttk.END, "2. Endereço IP da LAN... [OK]\n")
        texto_resultado.update_idletasks()
        
        # Configurar Pool DHCP
        api.get_resource('/ip/pool').add(name='dhcp_pool_lan', ranges=dhcp_pool)
        texto_resultado.insert(ttk.END, "3. Pool de IPs DHCP... [OK]\n")
        texto_resultado.update_idletasks()
        
        # Configurar DHCP Server
        dhcp_server_resource = api.get_resource('/ip/dhcp-server')
        dhcp_server_resource.add(name='dhcp_lan', interface=lan_if, address_pool='dhcp_pool_lan', disabled='no')
        # Adicionar a Rede DHCP
        dhcp_network_resource = api.get_resource('/ip/dhcp-server/network')
        # Extrai o endereço de rede do IP/máscara (ex: 192.168.88.1/24 -> 192.168.88.0)
        gateway_address = lan_ip.split('/')[0]
        network_address = '.'.join(lan_ip.split('.')[:3]) + '.0'
        dhcp_network_resource.add(address=f"{network_address}/{lan_ip.split('/')[1]}", gateway=gateway_address)
        texto_resultado.insert(ttk.END, "4. Servidor DHCP na LAN... [OK]\n")
        texto_resultado.update_idletasks()

        # Configurar NAT
        api.get_resource('/ip/firewall/nat').add(chain='srcnat', action='masquerade', out_interface=wan_if)
        texto_resultado.insert(ttk.END, "5. Regra de NAT (Masquerade)... [OK]\n")
        texto_resultado.update_idletasks()
        
        # Criar novo utilizador admin e dar-lhe plenos poderes
        user_resource = api.get_resource('/user')
        user_resource.add(name=admin_user, password=admin_pass, group='full')
        texto_resultado.insert(ttk.END, f"6. Utilizador '{admin_user}' criado... [OK]\n")
        texto_resultado.update_idletasks()

        # Feedback Final
        messagebox.showinfo("Sucesso!", "O roteador foi configurado com sucesso!\nÉ recomendado reiniciar o roteador.", parent=wizard_window)
        texto_resultado.insert(ttk.END, "\n--- CONFIGURAÇÃO CONCLUÍDA ---")
        
    except Exception as e:
        messagebox.showerror("Erro de Configuração", f"Ocorreu um erro durante a aplicação das configurações:\n{e}", parent=wizard_window)
        texto_resultado.insert(ttk.END, f"\n--- ERRO ---\n{e}")

    # Fecha a janela do wizard no final
    wizard_window.destroy()


# O resto do código (a interface gráfica, as funções de SSH, etc.) permanece exatamente o mesmo.
# Vou colar o código completo abaixo para garantir que nada falte.

# ----------------------------------------------------------------------------------
# Funções de SSH (sem alteração)
def executar_comando_ssh(comando):
    """
    Pega as credenciais da interface, conecta, executa UM comando e retorna o resultado.
    Esta função será a base para todas as nossas ações.
    """
    ip = entry_ip.get()
    usuario = entry_usuario.get()
    senha = entry_senha.get()

    if not ip or not usuario or not senha:
        messagebox.showerror("Erro de Conexão", "Os campos de IP, Utilizador e Senha devem ser preenchidos.")
        return None # Retorna None em caso de falha

    try:
        cliente_ssh = paramiko.SSHClient()
        cliente_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        cliente_ssh.connect(hostname=ip, username=usuario, password=senha, port=22, timeout=5)
        stdin, stdout, stderr = cliente_ssh.exec_command(comando)
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        cliente_ssh.close()

        resultado_final = ""
        if output:
            resultado_final += output
        if error:
            resultado_final += f"\n--- ERROS ---\n{error}"
        return resultado_final

    except Exception as e:
        messagebox.showerror("Erro de Execução", f"Falha na conexão ou execução do comando:\n{e}")
        return None

def ver_status_interfaces():
    """Função para o botão 'Ver Status das Interfaces'."""
    comando = "/interface print" 
    texto_resultado.delete("1.0", ttk.END)
    texto_resultado.insert(ttk.END, f"Executando o comando: '{comando}'...\n\n")
    texto_resultado.update_idletasks()

    resultado = executar_comando_ssh(comando)
    if resultado is not None:
        texto_resultado.insert(ttk.END, resultado)

def enviar_comando_manual():
    """Função para a caixa de texto de comando manual."""
    comando = entry_comando.get("1.0", ttk.END).strip()
    if not comando:
        messagebox.showwarning("Aviso", "Por favor, digite um comando na caixa de texto.")
        return

    texto_resultado.delete("1.0", ttk.END)
    texto_resultado.insert(ttk.END, f"Executando o comando manual: '{comando}'...\n\n")
    texto_resultado.update_idletasks()

    resultado = executar_comando_ssh(comando)
    if resultado is not None:
        texto_resultado.insert(ttk.END, resultado)

# ----------------------------------------------------------------------------------
# Função para criar a Janela do Wizard (sem alteração)
# ----------------------------------------------------------------------------------
def criar_janela_wizard():
    wizard = Toplevel(janela)
    wizard.title("Wizard de Configuração Inicial MikroTik")
    wizard.geometry("500x300")
    
    frame = ttk.Frame(wizard, padding=15)
    frame.pack(fill="both", expand=True)

    labels = ["Interface WAN:", "Interface LAN:", "IP da Rede LAN (ex: 192.168.88.1/24):", 
              "Pool DHCP (ex: 192.168.88.10-192.168.88.254):", "Novo Utilizador Admin:", "Nova Senha Admin:"]
    
    defaults = ["ether1", "ether2", "192.168.88.1/24", "192.168.88.10-192.168.88.254", "admin_novo", ""]

    entries = {}
    for i, text in enumerate(labels):
        ttk.Label(frame, text=text).grid(row=i, column=0, sticky="w", pady=2)
        entry = ttk.Entry(frame)
        entry.insert(0, defaults[i])
        entry.grid(row=i, column=1, sticky="ew", padx=5)
        # Chave para o dicionário 'entries'
        key_name = text.lower().replace(" ", "_").replace(":", "").split("(")[0].strip()
        entries[key_name] = entry

    frame.grid_columnconfigure(1, weight=1)

    apply_button = ttk.Button(frame, text="Aplicar Configuração", 
                              command=lambda: aplicar_configuracao_inicial(wizard, entries), 
                              bootstyle="success")
    apply_button.grid(row=len(labels), column=0, columnspan=2, pady=15)

# ----------------------------------------------------------------------------------
# Configuração da Janela Principal e Widgets (sem alteração)
# ----------------------------------------------------------------------------------
janela = ttk.Window(themename="litera")
janela.title("Ferramenta de Configuração de Rede v4.1")
janela.state('zoomed')

main_frame = ttk.Frame(janela)
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

frame_botoes = ttk.LabelFrame(main_frame, text="Funções Rápidas", padding=10)
frame_botoes.pack(side="left", fill="y", padx=(0, 10))

frame_principal = ttk.Frame(main_frame)
frame_principal.pack(side="right", fill="both", expand=True)

botao_wizard = ttk.Button(frame_botoes, text="Configurar Roteador do Zero", command=criar_janela_wizard, bootstyle="danger")
botao_wizard.pack(fill="x", pady=5)
ttk.Separator(frame_botoes, orient='horizontal').pack(fill='x', pady=10)
botao_ver_interfaces = ttk.Button(frame_botoes, text="Ver Interfaces (MikroTik)", command=ver_status_interfaces)
botao_ver_interfaces.pack(fill="x", pady=5)

frame_conexao = ttk.LabelFrame(frame_principal, text="Dados de Conexão", padding=10)
frame_conexao.pack(fill="x")
ttk.Label(frame_conexao, text="IP do Equipamento:").grid(row=0, column=0, padx=5, pady=5)
entry_ip = ttk.Entry(frame_conexao)
entry_ip.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
ttk.Label(frame_conexao, text="Utilizador:").grid(row=1, column=0, padx=5, pady=5)
entry_usuario = ttk.Entry(frame_conexao)
entry_usuario.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
ttk.Label(frame_conexao, text="Senha:").grid(row=2, column=0, padx=5, pady=5)
entry_senha = ttk.Entry(frame_conexao, show="*")
entry_senha.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
frame_conexao.grid_columnconfigure(1, weight=1)

frame_manual = ttk.LabelFrame(frame_principal, text="Comando Manual", padding=10)
frame_manual.pack(fill="x", pady=10)
entry_comando = ScrolledText(frame_manual, height=4)
entry_comando.pack(fill="x", expand=True)
botao_enviar = ttk.Button(frame_manual, text="Enviar Comando", command=enviar_comando_manual, bootstyle="info")
botao_enviar.pack(pady=(10,0))

frame_resultado = ttk.LabelFrame(frame_principal, text="Resultado", padding=10)
frame_resultado.pack(fill="both", expand=True)
texto_resultado = ScrolledText(frame_resultado, height=15)
texto_resultado.pack(fill="both", expand=True)

janela.mainloop()