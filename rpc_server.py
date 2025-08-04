from xmlrpc.server import SimpleXMLRPCServer
import threading

class RPCServer:
    def __init__(self, user, host='localhost', port=9000, on_message_callback=None):
        self.user = user
        self.on_message_callback = on_message_callback
        self.server = SimpleXMLRPCServer((host, port), allow_none=True, logRequests=False)
        self.server.register_function(self.receive_message, "receive_message")
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.daemon = True

    def start(self):
        print(f"[RPCServer] Servidor RPC de {self.user.name} rodando em porta {self.server.server_address[1]}")
        self.thread.start()

    def receive_message(self, sender_name, message):
        """Função exposta para receber mensagens síncronas."""
        texto = f"[{self.user.name}] Mensagem recebida de {sender_name}: {message}"
        print(texto)
        if self.on_message_callback:
            self.on_message_callback(texto)
        return True
