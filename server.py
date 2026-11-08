from socket import *
import threading


clients = []


def handle_client(client_socket):
    while True:
        try:
            message = client_socket.recv(4096)
            if not message:
                break

            for client in clients:
                try:
                    client.send(message)
                except:
                    pass
        except:
            break

    if client_socket in clients:
        clients.remove(client_socket)
    client_socket.close()


def start_server():
    server = socket(AF_INET, SOCK_STREAM)
    server.bind(('localhost', 8080))
    server.listen(5)
    print("Сервер запущено і чекає на підключення...")

    while True:
        client_socket, addr = server.accept()
        print(f"З'єднано з {addr}")
        clients.append(client_socket)


        threading.Thread(target=handle_client, args=(client_socket,), daemon=True).start()


start_server()