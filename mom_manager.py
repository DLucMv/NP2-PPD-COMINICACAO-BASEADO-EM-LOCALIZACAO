import stomp
import time
import threading

class MOMManager(stomp.ConnectionListener):
    def __init__(self, user_name, queue_name=None, host='localhost', port=61613):
        self.user_name = user_name
        self.queue_name = queue_name or f"/queue/user.{user_name}"
        self.conn = stomp.Connection([(host, port)])
        self.conn.set_listener('', self)
        self.conn.connect(wait=True)
        self.conn.subscribe(destination=self.queue_name, id=1, ack='auto')
        self.message_buffer = []
        print(f"[MOM] Subscrito na fila: {self.queue_name}")

    def send_message(self, target_user, message):
        destination = f"/queue/user.{target_user}"
        body = f"Mensagem offline de {self.user_name}: {message}"
        self.conn.send(destination=destination, body=body)
        print(f"[MOM] Mensagem enviada para {destination}")

    def on_message(self, frame):
        message = frame.body
        print(f"[MOM] {self.user_name} recebeu: {message}")
        self.message_buffer.append(message)

    def read_buffer(self):
        msgs = self.message_buffer.copy()
        self.message_buffer.clear()
        return msgs

    def disconnect(self):
        self.conn.disconnect()
