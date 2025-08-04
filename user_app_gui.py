import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
import threading
from registry_client import RegistryClient
from rpc_server import RPCServer
from rpc_client import RPCClient
from mom_manager import MOMManager
from user import User

class UserAppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Comunicação por Localização")
        self.registry = RegistryClient()
        self.user = None
        self.rpc_server = None
        self.mom = None

        self.build_login_screen()

    def build_login_screen(self):
        self.clear_screen()

        tk.Label(self.root, text="Nome:").pack()
        self.name_entry = tk.Entry(self.root)
        self.name_entry.pack()

        tk.Label(self.root, text="Latitude:").pack()
        self.lat_entry = tk.Entry(self.root)
        self.lat_entry.pack()

        tk.Label(self.root, text="Longitude:").pack()
        self.lon_entry = tk.Entry(self.root)
        self.lon_entry.pack()

        tk.Label(self.root, text="Status (online/offline):").pack()
        self.status_entry = tk.Entry(self.root)
        self.status_entry.pack()

        tk.Label(self.root, text="Raio (km):").pack()
        self.radius_entry = tk.Entry(self.root)
        self.radius_entry.pack()

        tk.Label(self.root, text="Porta RPC:").pack()
        self.port_entry = tk.Entry(self.root)
        self.port_entry.pack()

        tk.Button(self.root, text="Entrar", command=self.register_user).pack(pady=10)

    def build_main_screen(self):
        self.clear_screen()

        tk.Label(self.root, text=f"Bem-vindo, {self.user.name}").pack()

        tk.Button(self.root, text="Atualizar Localização", command=self.update_location).pack(fill='x')
        tk.Button(self.root, text="Atualizar Status", command=self.update_status).pack(fill='x')
        tk.Button(self.root, text="Atualizar Raio", command=self.update_radius).pack(fill='x')
        tk.Button(self.root, text="Mostrar Contatos Online", command=self.show_contacts).pack(fill='x')
        tk.Button(self.root, text="Enviar Mensagem", command=self.send_message).pack(fill='x')
        tk.Button(self.root, text="Ver Mensagens Offline", command=self.show_offline_msgs).pack(fill='x')
        tk.Button(self.root, text="Sair", command=self.quit_app).pack(fill='x', pady=10)

        self.output = scrolledtext.ScrolledText(self.root, height=10)
        self.output.pack(padx=10, pady=5)

    def register_user(self):
        name = self.name_entry.get()
        lat = float(self.lat_entry.get())
        lon = float(self.lon_entry.get())
        status = self.status_entry.get().strip().lower()
        radius = float(self.radius_entry.get())
        port = int(self.port_entry.get())

        # Registrar usuário ou atualizar informações
        user_id = self.registry.register_user(name, lat, lon, status, radius)
        self.user = User(name, lat, lon, status, radius)
        self.user.id = user_id
        self.user.rpc_port = port

        # Iniciar ou reiniciar servidor RPC
        if self.rpc_server:
            self.rpc_server.stop()
        self.rpc_server = RPCServer(self.user, port=port, on_message_callback=self.append_output)
        self.rpc_server.start()

        # Inicializar ou reconectar MOM
        if self.mom is None:
            self.mom = MOMManager(self.user, name)
        else:
            try:
                self.mom.conn.connect(wait=True)
                self.mom.conn.subscribe(destination=self.mom.queue_name, id=1, ack='auto')
                self.append_output("Reconectado à fila MOM.")
            except Exception as e:
                self.append_output(f"[ERRO] Reconexão MOM falhou: {e}")

        # Atualizar status no registry para garantir que o usuário está online
        self.registry.update_status(user_id, "online")
        self.user.status = "online"

        self.build_main_screen()
        #self.check_mom_messages() 

    def update_location(self):
        lat = float(simpledialog.askstring("Latitude", "Nova latitude:"))
        lon = float(simpledialog.askstring("Longitude", "Nova longitude:"))
        self.registry.update_location(self.user.id, lat, lon)
        self.append_output("Localização atualizada.")
        
    def update_status(self):
        status = simpledialog.askstring("Status", "Novo status (online/offline):").strip().lower()
        self.user.status = status
        self.registry.update_status(self.user.id, status)
        self.append_output("Status atualizado.")
        
    def update_radius(self):
        r = float(simpledialog.askstring("Raio", "Novo raio (km):"))
        self.user.radius_km = r
        self.registry.update_radius(self.user.id, r)
        self.append_output("Raio atualizado.")

    def show_contacts(self):
        contatos = self.registry.get_online_contacts_within_radius(self.user.id)
        if not contatos:
            self.append_output("Nenhum contato online no raio.")
        else:
            self.append_output("Contatos online no raio:")
            for cid, cname in contatos:
                self.append_output(f" - {cname} (id: {cid})")

    def send_message(self):
        dest_name = simpledialog.askstring("Destinatário", "Nome do destinatário:")
        msg = simpledialog.askstring("Mensagem", "Digite a mensagem:")
        dest_info = self.registry.get_user_info_by_name(dest_name)

        if not dest_info:
            messagebox.showerror("Erro", "Usuário não encontrado.")
            return

        _, status = dest_info

        try:
            within_radius = self.registry.is_within_radius(self.user.id, dest_name)
        except Exception as e:
            print("Erro ao verificar distância:", e)
            within_radius = False

        if status == "online" and within_radius:
            try:
                dest_port = int(simpledialog.askstring("Porta", "Porta RPC do destinatário:"))
                client = RPCClient(target_port=dest_port)
                client.send_message(self.user.name, msg)
                self.append_output("Mensagem enviada via RPC.")
            except Exception as e:
                self.append_output(f"Erro no envio RPC: {e}")
        else:
            self.mom.send_message(dest_name, msg)
            self.append_output("Mensagem enviada via fila.")

    def show_offline_msgs(self):
        try:
            contacts = self.registry.get_online_contacts_within_radius(self.user.id)
        except Exception as e:
            print("Erro ao verificar distância:", e)
            contacts = False

        if self.user.status == "online" and contacts:
            msgs = self.mom.read_buffer()
            if not msgs:
                self.append_output("Nenhuma mensagem offline.")
            else:
                self.append_output("Mensagens offline:")
                for m in msgs:
                    self.append_output(m)
        else:
            self.append_output("Sem conexão")

    def check_mom_messages(self):
        if self.mom:
            msgs = self.mom.read_buffer()
            # Filtrar mensagens só se estiver online e dentro do raio
            if self.user.status == "online":
                for m in msgs:
                    self.append_output(f"[OFFLINE] {m}")
            else:
                # Ignorar mensagens MOM pois o usuário está offline ou fora do raio
                pass
        self.root.after(2000, self.check_mom_messages)

    def quit_app(self):
        if self.user:
            try:
                self.registry.update_status(self.user.id, "offline")
                self.append_output(f"Status do usuário '{self.user.name}' atualizado para offline.")
            except Exception as e:
                self.append_output(f"[ERRO] Falha ao atualizar status: {e}")
            self.mom.disconnect()
        self.root.destroy()

    def append_output(self, text):
        def task():
            self.output.insert(tk.END, text + "\n")
            self.output.see(tk.END)
        self.root.after(0, task)

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = UserAppGUI(root)
    root.mainloop()
