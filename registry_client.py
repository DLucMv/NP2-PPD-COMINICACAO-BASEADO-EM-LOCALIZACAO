import xmlrpc.client

class RegistryClient:
    def __init__(self, host='localhost', port=8000):
        self.proxy = xmlrpc.client.ServerProxy(f"http://{host}:{port}", allow_none=True)

    def register_user(self, name, lat, lon, status, radius):
        return self.proxy.register_user(name, lat, lon, status, radius)

    def update_location(self, user_id, lat, lon):
        return self.proxy.update_location(user_id, lat, lon)

    def update_status(self, user_id, status):
        return self.proxy.update_status(user_id, status)

    def update_radius(self, user_id, radius):
        return self.proxy.update_radius(user_id, radius)

    def get_online_contacts_within_radius(self, user_id):
        return self.proxy.get_online_contacts_within_radius(user_id)

    def get_user_info_by_name(self, name):
        return self.proxy.get_user_port_by_name(name)
    
    def remove_user(self, user_id):
        return self.proxy.remove_user(user_id)
    
    def is_within_radius(self, sender_id, receiver_name):
        return self.proxy.is_within_radius(sender_id, receiver_name)


