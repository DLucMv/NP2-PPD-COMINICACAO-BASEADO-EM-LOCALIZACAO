from user import User

class UserRegistry:
    def __init__(self):
        self.users = {}  # {user_id: User}

    def add_user(self, user: User):
        self.users[user.id] = user

    def remove_user(self, user_id: str):
        if user_id in self.users:
            del self.users[user_id]

    def update_location(self, user_id: str, latitude: float, longitude: float):
        if user_id in self.users:
            self.users[user_id].update_location(latitude, longitude)

    def update_status(self, user_id: str, status: str):
        if user_id in self.users:
            self.users[user_id].update_status(status)

    def update_radius(self, user_id: str, radius_km: float):
        if user_id in self.users:
            self.users[user_id].update_radius(radius_km)

    def get_user(self, user_id: str) -> User:
        return self.users.get(user_id)

    def get_online_contacts_within_radius(self, user_id: str):
        """Retorna lista de usuários online e dentro do raio de comunicação do usuário."""
        if user_id not in self.users:
            return []

        user = self.users[user_id]
        contacts = []
        for other_id, other_user in self.users.items():
            if other_id != user_id and other_user.status == 'online':
                if user.is_within_radius(other_user):
                    contacts.append(other_user)
        return contacts

    def update_contacts(self, user_id: str):
        """Atualiza lista de contatos de um usuário com base na distância."""
        if user_id not in self.users:
            return

        user = self.users[user_id]
        user.contacts.clear()
        for other_id, other_user in self.users.items():
            if other_id != user_id and user.is_within_radius(other_user):
                user.add_contact(other_user)

    def is_within_radius(self, sender_id, receiver_name):
        sender = self.users.get(sender_id)
        receiver = next((u for u in self.users.values() if u.name == receiver_name), None)
        if not sender or not receiver:
            return False
        return sender.is_within_radius(receiver)
