import xmlrpc.client

class RPCClient:
    def __init__(self, target_host='localhost', target_port=9000):
        self.target = f"http://{target_host}:{target_port}"
        self.proxy = xmlrpc.client.ServerProxy(self.target, allow_none=True)

    def send_message(self, sender_name, message):
        try:
            print(f"[RPCClient] Enviando para {self.target} -> {message}")
            return self.proxy.receive_message(sender_name, message)
        except Exception as e:
            print(f"[RPCClient] Falha ao enviar mensagem RPC: {e}")
            return False
