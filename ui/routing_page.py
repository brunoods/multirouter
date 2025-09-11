"""
Página da interface do utilizador para visualizar e gerir o roteamento.
"""
from tkinter import ttk, messagebox
from ttkbootstrap.scrolled import ScrolledText
from logic.routing_manager import get_device_routes, add_static_route

class RoutingPage(ttk.Frame):
    """Frame para a gestão de roteamento."""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.create_widgets()

    def create_widgets(self):
        """Cria os widgets da página."""
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill="both", expand=True)

        # Frame superior para ações
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill="x", pady=(0, 10))

        refresh_btn = ttk.Button(action_frame, text="Atualizar Tabela de Roteamento", command=self.refresh)
        refresh_btn.pack(side="left")

        # Frame para adicionar rota estática
        add_route_frame = ttk.Labelframe(main_frame, text="Adicionar Rota Estática", padding=10)
        add_route_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(add_route_frame, text="Rede (ex: 10.0.0.0/24):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.network_entry = ttk.Entry(add_route_frame, width=30)
        self.network_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(add_route_frame, text="Next-Hop (ex: 192.168.1.254):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.nexthop_entry = ttk.Entry(add_route_frame, width=30)
        self.nexthop_entry.grid(row=1, column=1, padx=5, pady=5)

        add_btn = ttk.Button(add_route_frame, text="Adicionar Rota", command=self.add_route_action)
        add_btn.grid(row=0, column=2, rowspan=2, padx=10)

        # Frame para exibir a tabela de roteamento
        routes_frame = ttk.Labelframe(main_frame, text="Tabela de Roteamento", padding=10)
        routes_frame.pack(fill="both", expand=True)

        self.routes_text = ScrolledText(routes_frame, wrap="none", state="disabled")
        self.routes_text.pack(fill="both", expand=True)

    def refresh(self):
        """Busca e exibe a tabela de roteamento do dispositivo."""
        device = self.app.get_selected_device()
        if not device:
            messagebox.showinfo("Aviso", "Por favor, selecione um dispositivo.")
            return

        self.routes_text.config(state="normal")
        self.routes_text.delete("1.0", "end")
        
        routes = get_device_routes(device)
        self.routes_text.insert("1.0", routes)
        self.routes_text.config(state="disabled")
    
    def add_route_action(self):
        """Pega os dados da UI e chama a função para adicionar a rota."""
        device = self.app.get_selected_device()
        if not device:
            messagebox.showerror("Erro", "Nenhum dispositivo selecionado.")
            return

        network = self.network_entry.get()
        next_hop = self.nexthop_entry.get()

        if not network or not next_hop:
            messagebox.showwarning("Dados em Falta", "Preencha os campos de rede e next-hop.")
            return
        
        add_static_route(device, network, next_hop)
        # Atualiza a tabela de rotas após adicionar
        self.after(2000, self.refresh) # Espera 2s para o dispositivo processar