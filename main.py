from user import User
from registry_client import RegistryClient
from rpc_server import RPCServer
from rpc_client import RPCClient
from mom_manager import MOMManager
import threading

def start_user_interface():
    registry = RegistryClient()

    # Coleta dados do usuário
    name = input("Digite seu nome: ").strip()
    latitude = float(input("Latitude: "))
    longitude = float(input("Longitude: "))
    status = input("Status (online/offline): ").strip().lower()
    radius = float(input("Raio de comunicação (km): "))
    port = int(input("Porta RPC para este usuário: "))

    # Cria instância local para RPC + MOM, mas registra remotamente
    user = User(name, latitude, longitude, status, radius)
    user.rpc_port = port
    user_id = registry.register_user(name, latitude, longitude, status, radius)
    user.id = user_id  # Sincroniza id com o remoto

    # Inicializa RPC Server e MOM (mesmo que status esteja offline)
    rpc_server = RPCServer(user, port=port)
    rpc_server.start()
    mom = MOMManager(name)

    def menu():
        while True:
            print("\n[Menu]")
            print("1. Atualizar localização")
            print("2. Atualizar status")
            print("3. Atualizar raio de comunicação")
            print("4. Mostrar contatos online no raio")
            print("5. Enviar mensagem")
            print("6. Ver mensagens offline")
            print("0. Sair")
            op = input("Opção: ")

            if op == "1":
                lat = float(input("Nova latitude: "))
                lon = float(input("Nova longitude: "))
                registry.update_location(user.id, lat, lon)
                print("Localização atualizada.")
            elif op == "2":
                new_status = input("Novo status (online/offline): ").strip().lower()
                user.status = new_status
                registry.update_status(user.id, new_status)
                print("Status atualizado.")
            elif op == "3":
                r = float(input("Novo raio (km): "))
                user.radius_km = r
                registry.update_radius(user.id, r)
                print("Raio atualizado.")
            elif op == "4":
                contatos = registry.get_online_contacts_within_radius(user.id)
                print("Contatos online dentro do raio:")
                for cid, cname in contatos:
                    print(f" - {cname} (id: {cid})")
            elif op == "5":
                dest_name = input("Nome do destinatário: ").strip()
                dest_info = registry.get_user_info_by_name(dest_name)
                if not dest_info:
                    print("Usuário não encontrado.")
                    continue

                _, status = dest_info
                msg = input("Mensagem: ")

                # Verifica se o destinatário está dentro do raio
                try:
                    within_radius = registry.is_within_radius(user.id, dest_name)
                except Exception as e:
                    print("Erro ao verificar distância:", e)
                    within_radius = False

                if status == "online" and within_radius:
                    try:
                        dest_port = int(input("Porta RPC do destinatário: "))
                        client = RPCClient(target_port=dest_port)
                        client.send_message(user.name, msg)
                        print("Mensagem enviada via RPC.")
                    except Exception as e:
                        print("Erro no envio RPC:", e)
                else:
                    mom.send_message(dest_name, msg)
                    print("Mensagem enviada via fila (usuário offline ou fora de cobertura).")

            elif op == "6":
                msgs = mom.read_buffer()
                if not msgs:
                    print("Nenhuma mensagem offline.")
                else:
                    print("Mensagens offline:")
                    for m in msgs:
                        print(" -", m)
            elif op == "0":
                try:
                    registry.update_status(user_id, "offline")
                    print(f"[INFO] Status do usuário '{user.name}' atualizado para offline.")
                except Exception as e:
                    print(f"[ERRO] Falha ao atualizar status para offline: {e}")
                mom.disconnect()
                print("Saindo...")
                break


    threading.Thread(target=menu).start()

# Executa CLI
if __name__ == "__main__":
    start_user_interface()
