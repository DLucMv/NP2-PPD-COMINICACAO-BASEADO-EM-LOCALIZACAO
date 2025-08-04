from xmlrpc.server import SimpleXMLRPCServer
from user import User
from user_registry import UserRegistry
import threading

registry = UserRegistry()

# Funções expostas remotamente
def register_user(name, latitude, longitude, status, radius):
    user = User(name, latitude, longitude, status, radius)
    registry.add_user(user)
    return user.id

def update_location(user_id, lat, lon):
    registry.update_location(user_id, lat, lon)
    registry.update_contacts(user_id)
    return True

def update_status(user_id, status):
    registry.update_status(user_id, status)
    registry.update_contacts(user_id)
    return True

def update_radius(user_id, radius):
    registry.update_radius(user_id, radius)
    registry.update_contacts(user_id)
    return True

def get_online_contacts_within_radius(user_id):
    contacts = registry.get_online_contacts_within_radius(user_id)
    return [(u.id, u.name) for u in contacts]

def get_user_port_by_name(name):
    # Para simular RPC de forma mais prática
    for u in registry.users.values():
        if u.name == name:
            return u.name, u.status  
    return None

def is_within_radius(sender_id, receiver_name):
    return registry.is_within_radius(sender_id, receiver_name)

def remove_user(user_id):
    return registry.remove_user(user_id)

# Cria e inicia servidor
server = SimpleXMLRPCServer(("localhost", 8000), allow_none=True, logRequests=False)
server.register_function(register_user, "register_user")
server.register_function(update_location, "update_location")
server.register_function(update_status, "update_status")
server.register_function(update_radius, "update_radius")
server.register_function(is_within_radius, "is_within_radius")
server.register_function(get_online_contacts_within_radius, "get_online_contacts_within_radius")
server.register_function(get_user_port_by_name, "get_user_port_by_name")
server.register_function(remove_user, "remove_user")

print("[RegistryServer] Servidor iniciado em porta 8000")
server.serve_forever()
