import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from .base_page import BasePage
from logic.ipam_manager import (
    load_subnets,
    add_subnet,
    remove_subnet,
    get_subnet_details,
)

class IPAMPage(BasePage):
    def __init__(self, parent, app):
        super().__init__(parent, app, page_title="Gestão de Endereços IP (IPAM)")

    def create_content(self):
        # --- Estrutura Principal ---
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        main_frame.grid_columnconfigure(1, weight=3)
        main_frame.grid_rowconfigure(0, weight=1)

        # --- Painel Esquerdo: Lista de Sub-redes ---
        left_frame = ttk.LabelFrame(main_frame, text="Sub-redes Geridas")
        left_frame.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="nsew")
        left_frame.grid_rowconfigure(0, weight=1)

        self.subnet_list = tk.Listbox(left_frame, selectmode="browse")
        self.subnet_list.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=5)
        self.subnet_list.bind("<<ListboxSelect>>", self.on_subnet_select)

        add_btn = ttk.Button(left_frame, text="Adicionar", style="success.TButton", command=self.open_add_subnet_form)
        add_btn.grid(row=1, column=0, sticky="ew", padx=(0, 2), pady=5)
        
        remove_btn = ttk.Button(left_frame, text="Remover", style="danger.TButton", command=self.delete_selected_subnet)
        remove_btn.grid(row=1, column=1, sticky="ew", padx=(2, 0), pady=5)

        # --- Painel Direito: Detalhes dos IPs ---
        right_frame = ttk.LabelFrame(main_frame, text="Detalhes da Sub-rede")
        right_frame.grid(row=0, column=1, padx=(5, 0), pady=5, sticky="nsew")
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        cols = ("Endereço IP", "Estado")
        self.ip_tree = ttk.Treeview(right_frame, columns=cols, show="headings")
        self.ip_tree.heading("Endereço IP", text="Endereço IP")
        self.ip_tree.heading("Estado", text="Estado")
        self.ip_tree.column("Endereço IP", width=150)
        self.ip_tree.pack(fill="both", expand=True)
        
        self.populate_subnet_list()

    def populate_subnet_list(self):
        self.subnet_list.delete(0, tk.END)
        self.subnets = load_subnets()
        for subnet in self.subnets:
            self.subnet_list.insert(tk.END, f"{subnet['cidr']} - {subnet.get('description', 'N/A')}")

    def on_subnet_select(self, event):
        selection_indices = self.subnet_list.curselection()
        if not selection_indices:
            return

        selected_subnet_cidr = self.subnets[selection_indices[0]]["cidr"]
        ip_details = get_subnet_details(selected_subnet_cidr)

        for i in self.ip_tree.get_children():
            self.ip_tree.delete(i)

        for ip_info in ip_details:
            self.ip_tree.insert("", "end", values=(ip_info["ip"], ip_info["status"]))

    def open_add_subnet_form(self):
        form = AddSubnetForm(self)
        self.wait_window(form)
        if form.result:
            add_subnet(form.result["cidr"], form.result["description"])
            self.populate_subnet_list()

    def delete_selected_subnet(self):
        selection_indices = self.subnet_list.curselection()
        if not selection_indices:
            messagebox.showwarning("Nenhuma Seleção", "Selecione uma sub-rede para remover.", parent=self)
            return

        selected_subnet_cidr = self.subnets[selection_indices[0]]["cidr"]
        if messagebox.askyesno("Confirmar Remoção", f"Tem a certeza que deseja remover a sub-rede {selected_subnet_cidr}?", parent=self):
            remove_subnet(selected_subnet_cidr)
            self.populate_subnet_list()
            for i in self.ip_tree.get_children():
                self.ip_tree.delete(i)

class AddSubnetForm(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.transient(parent)
        self.title("Adicionar Nova Sub-rede")
        self.result = None

        ttk.Label(self, text="Sub-rede (formato CIDR):").pack(padx=10, pady=(10, 0))
        self.cidr_entry = ttk.Entry(self, width=30)
        self.cidr_entry.pack(padx=10, pady=5)
        self.cidr_entry.insert(0, "192.168.1.0/24")

        ttk.Label(self, text="Descrição:").pack(padx=10, pady=5)
        self.desc_entry = ttk.Entry(self, width=30)
        self.desc_entry.pack(padx=10, pady=5)

        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Adicionar", style="success.TButton", command=self.on_add).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancelar", command=self.destroy).pack(side="left", padx=5)
        
        self.grab_set() # Foca nesta janela

    def on_add(self):
        cidr = self.cidr_entry.get()
        desc = self.desc_entry.get()
        if not cidr or not desc:
            messagebox.showwarning("Campos Vazios", "Por favor, preencha todos os campos.", parent=self)
            return
            
        self.result = {"cidr": cidr, "description": desc}
        self.destroy()