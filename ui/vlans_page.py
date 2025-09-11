"""
Página da interface do utilizador para visualizar e gerir VLANs.
"""
from tkinter import ttk, messagebox, simpledialog
from logic.vlan_manager import get_device_vlans, create_vlan


class VLANsPage(ttk.Frame):
    """Frame para a gestão de VLANs."""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.create_widgets()

    def create_widgets(self):
        """Cria os widgets da página."""
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill="both", expand=True)

        # Frame de ações
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill="x", pady=(0, 10))

        refresh_btn = ttk.Button(action_frame, text="Atualizar Lista de VLANs", command=self.refresh)
        refresh_btn.pack(side="left", padx=(0, 10))
        
        create_btn = ttk.Button(action_frame, text="Criar Nova VLAN", command=self.create_vlan_action, bootstyle="success")
        create_btn.pack(side="left")

        # Treeview para exibir as VLANs
        self.vlans_tree = ttk.Treeview(
            main_frame,
            columns=("id", "name", "status"),
            show="headings",
        )
        self.vlans_tree.heading("id", text="ID da VLAN")
        self.vlans_tree.heading("name", text="Nome")
        self.vlans_tree.heading("status", text="Status")
        self.vlans_tree.pack(fill="both", expand=True)

    def refresh(self):
        """Busca e exibe as VLANs do dispositivo selecionado."""
        for item in self.vlans_tree.get_children():
            self.vlans_tree.delete(item)

        device = self.app.get_selected_device()
        if not device:
            messagebox.showinfo("Aviso", "Por favor, selecione um dispositivo.")
            return

        vlans = get_device_vlans(device)
        if not vlans:
            return

        for vlan in vlans:
            self.vlans_tree.insert(
                "", "end", values=(vlan.get("id"), vlan.get("name"), vlan.get("status"))
            )

    def create_vlan_action(self):
        """Inicia o processo para criar uma nova VLAN."""
        device = self.app.get_selected_device()
        if not device:
            messagebox.showerror("Erro", "Nenhum dispositivo selecionado.")
            return

        vlan_id = simpledialog.askstring("Criar VLAN", "Insira o ID da nova VLAN:", parent=self)
        if not vlan_id or not vlan_id.isdigit():
            messagebox.showwarning("Inválido", "O ID da VLAN deve ser um número.")
            return

        vlan_name = simpledialog.askstring("Criar VLAN", f"Insira o nome para a VLAN {vlan_id}:", parent=self)
        if not vlan_name:
            # Se o utilizador cancelar o nome, não fazemos nada
            return

        create_vlan(device, vlan_id, vlan_name)
        # Atualiza a lista após a tentativa de criação
        self.after(2000, self.refresh)