import uuid
from utils import haversine

class User:
    def __init__(self, name, latitude, longitude, status='offline', radius_km=5):
        self.id = str(uuid.uuid4())  # Identificador único do usuário
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.status = status  # 'online' ou 'offline'
        self.radius_km = radius_km
        self.contacts = {}  # {user_id: User}
        self.message_buffer = []  # Mensagens recebidas enquanto offline

    def update_location(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    def update_status(self, status):
        if status in ['online', 'offline']:
            self.status = status

    def update_radius(self, new_radius_km):
        self.radius_km = new_radius_km

    def is_within_radius(self, other_user):
        """Verifica se outro usuário está dentro do raio de alcance."""
        distance = haversine(self.latitude, self.longitude, other_user.latitude, other_user.longitude)
        return distance <= self.radius_km

    def add_contact(self, other_user):
        """Adiciona um contato se estiver dentro do raio."""
        if other_user.id != self.id and self.is_within_radius(other_user):
            self.contacts[other_user.id] = other_user

    def receive_message(self, message):
        """Adiciona mensagem ao buffer de mensagens."""
        self.message_buffer.append(message)

    def read_messages(self):
        """Retorna e limpa as mensagens recebidas."""
        msgs = self.message_buffer.copy()
        self.message_buffer.clear()
        return msgs
