# ui/device_form.py
import tkinter as tk
from tkinter import ttk, messagebox
from logic.inventory_manager import add_device, update_device

class DeviceForm(tk.Toplevel):
    """Janela de formulário para adicionar ou editar um dispositivo."""
    def __init__(self, parent, controller, device_to_edit=None):
        super().__init__(parent)
        self.transient(parent)
        self.controller = controller
        self.device_to_edit = device_to_edit

        self.title("Adicionar Novo Dispositivo" if not device_to_edit else "Editar Dispositivo")
        self.geometry("400x250")

        self.result = None

        form_frame = ttk.Frame(self)
        form_frame.pack(padx=20, pady=20, fill="both", expand=True)

        ttk.Label(form_frame, text="Nome Apelido:").grid(row=0, column=0, sticky="w", pady=5)
        self.name_entry = ttk.Entry(form_frame, width=30)
        self.name_entry.grid(row=0, column=1, pady=5)

        ttk.Label(form_frame, text="Endereço IP:").grid(row=1, column=0, sticky="w", pady=5)
        self.ip_entry = ttk.Entry(form_frame, width=30)
        self.ip_entry.grid(row=1, column=1, pady=5)

        ttk.Label(form_frame, text="Tipo de Dispositivo:").grid(row=2, column=0, sticky="w", pady=5)
        self.type_combobox = ttk.Combobox(form_frame, values=list(self.controller.VENDOR_MODULES.keys()), state="readonly", width=27)
        self.type_combobox.grid(row=2, column=1, pady=5)
        
        ttk.Label(form_frame, text="Usuário:").grid(row=3, column=0, sticky="w", pady=5)
        self.user_entry = ttk.Entry(form_frame, width=30)
        self.user_entry.grid(row=3, column=1, pady=5)

        ttk.Label(form_frame, text="Senha:").grid(row=4, column=0, sticky="w", pady=5)
        self.pass_entry = ttk.Entry(form_frame, width=30, show="*")
        self.pass_entry.grid(row=4, column=1, pady=5)
        
        if device_to_edit:
            self.name_entry.insert(0, device_to_edit.get('name', ''))
            self.ip_entry.insert(0, device_to_edit.get('host', ''))
            self.type_combobox.set(device_to_edit.get('type_name', ''))
            self.user_entry.insert(0, device_to_edit.get('username', ''))
            self.pass_entry.insert(0, device_to_edit.get('password', ''))

        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        save_button = ttk.Button(button_frame, text="Salvar", command=self.on_save)
        save_button.pack(side="left", padx=10)
        
        cancel_button = ttk.Button(button_frame, text="Cancelar", command=self.destroy)
        cancel_button.pack(side="left", padx=10)

    def on_save(self):
        details = {
            'name': self.name_entry.get(),
            'host': self.ip_entry.get(),
            'type_name': self.type_combobox.get(),
            'username': self.user_entry.get(),
            'password': self.pass_entry.get()
        }
        
        if not all([details['name'], details['host'], details['type_name'], details['username']]):
            messagebox.showerror("Campos Vazios", "Todos os campos, exceto a senha, são obrigatórios.", parent=self)
            return

        if self.device_to_edit:
            details['id'] = self.device_to_edit.get('id')
            update_device(details)
        else:
            add_device(details)
        
        self.result = True
        self.destroy()