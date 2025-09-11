"""
Formulário Toplevel para adicionar ou editar um dispositivo.
"""
from tkinter import Toplevel, ttk, messagebox

class DeviceForm(Toplevel):
    """Janela de formulário para os detalhes de um dispositivo."""

    def __init__(self, parent, app, device=None, device_index=None, title="Formulário de Dispositivo"):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()

        self.title(title)
        self.app = app
        self.parent = parent
        self.device_data = device
        self.device_index = device_index
        
        self.inventory_manager = app.inventory_manager

        self.create_form()
        if self.device_data:
            self.fill_form()

    def create_form(self):
        """Cria os campos do formulário."""
        form_frame = ttk.Frame(self, padding=20)
        form_frame.pack(fill="both", expand=True)

        # Campos
        ttk.Label(form_frame, text="Hostname:").grid(row=0, column=0, sticky="w", pady=5)
        self.host_entry = ttk.Entry(form_frame, width=40)
        self.host_entry.grid(row=0, column=1, pady=5)

        ttk.Label(form_frame, text="Endereço IP:").grid(row=1, column=0, sticky="w", pady=5)
        self.ip_entry = ttk.Entry(form_frame, width=40)
        self.ip_entry.grid(row=1, column=1, pady=5)

        ttk.Label(form_frame, text="Utilizador:").grid(row=2, column=0, sticky="w", pady=5)
        self.user_entry = ttk.Entry(form_frame, width=40)
        self.user_entry.grid(row=2, column=1, pady=5)

        ttk.Label(form_frame, text="Palavra-passe:").grid(row=3, column=0, sticky="w", pady=5)
        self.pass_entry = ttk.Entry(form_frame, show="*", width=40)
        self.pass_entry.grid(row=3, column=1, pady=5)

        ttk.Label(form_frame, text="Tipo de Dispositivo:").grid(row=4, column=0, sticky="w", pady=5)
        self.type_combo = ttk.Combobox(form_frame, values=["cisco_ios", "juniper_junos", "mikrotik_routeros"], state="readonly")
        self.type_combo.grid(row=4, column=1, pady=5)
        self.type_combo.set("cisco_ios")

        # Botões
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        save_btn = ttk.Button(btn_frame, text="Guardar", command=self.save_device, bootstyle="success")
        save_btn.pack(side="left", padx=10)

        cancel_btn = ttk.Button(btn_frame, text="Cancelar", command=self.destroy)
        cancel_btn.pack(side="left", padx=10)

    def fill_form(self):
        """Preenche o formulário com os dados de um dispositivo existente."""
        self.host_entry.insert(0, self.device_data.get("host", ""))
        self.ip_entry.insert(0, self.device_data.get("ip", ""))
        self.user_entry.insert(0, self.device_data.get("username", ""))
        self.pass_entry.insert(0, self.device_data.get("password", ""))
        self.type_combo.set(self.device_data.get("device_type", "cisco_ios"))

    def save_device(self):
        """Guarda os dados do dispositivo, seja novo ou editado."""
        device_details = {
            "host": self.host_entry.get(),
            "ip": self.ip_entry.get(),
            "username": self.user_entry.get(),
            "password": self.pass_entry.get(),
            "device_type": self.type_combo.get()
        }

        if not all(device_details.values()):
            messagebox.showerror("Erro", "Todos os campos são obrigatórios.", parent=self)
            return
        
        if self.device_index is not None:
            # Atualizar dispositivo existente
            self.inventory_manager.update_device(self.device_index, device_details)
        else:
            # Adicionar novo dispositivo
            self.inventory_manager.add_device(device_details)

        # Atualiza a lista na página de inventário e em toda a app
        self.parent.update_device_list()
        self.app.update_device_list()
        self.destroy()