import socket
import threading
import os
import sys
from getpass import getpass

#server settings
HOST= '127.0.0.1'#Lhost
PORT= 5555
server_pass = os.environ.get("CHAT_SERVER_PASS", "user0")  # server password (prefer env var)

#store connected clients
clients= []
clients_lock = threading.Lock()
client_info = {}


def _client_id_from_info(info):
    if not info:
        return "<unknown>"
    host, port = info
    return f"{host}:{port}"


def remove_client(client):
    """
    Removes client from tracking and returns its (host, port) info exactly once.
    This prevents double-disconnect notifications from multiple cleanup paths.
    """
    with clients_lock:
        info = client_info.pop(client, None)
        if client in clients:
            clients.remove(client)
        return info

#Broadcast message to all clients
def broadcast(message, exclude=None):
    dead_clients = []
    with clients_lock:
        snapshot = list(clients)

    for client in snapshot:
        if client is None:
            continue
        if exclude is not None and client in exclude:
            continue
        try:
            # sendall ensures the whole payload is sent (or raises).
            client.sendall(message)
        except OSError:
            dead_clients.append(client)

    if dead_clients:
        disconnected = []
        for client in dead_clients:
            info = remove_client(client)
            if info is not None:
                disconnected.append(_client_id_from_info(info))
            try:
                client.close()
            except OSError:
                pass

        for cid in disconnected:
            print(f"Client disconnected: {cid}")
            broadcast(f"[server] {cid} disconnected\n".encode("utf-8"))

#handle individual client
def handle_client(client):
    try:
        while True:
            message = client.recv(1024)
            # recv() returns b"" when the peer has closed the connection.
            if not message:
                break
            broadcast(message)
    except OSError:
        pass
    finally:
        info = remove_client(client)
        try:
            client.close()
        except OSError:
            pass

        if info is not None:
            cid = _client_id_from_info(info)
            print(f"Client disconnected: {cid}")
            broadcast(f"[server] {cid} disconnected\n".encode("utf-8"))

#main server function
def start_server():
    pas = getpass("Enter server password: ")
    if pas != server_pass:
        print("Wrong password")
        sys.exit(1)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # server being reusable
        server.bind((HOST, PORT))
        server.listen()
        print(f"Server is listening on {HOST}:{PORT}")

        while True:
            client, address = server.accept()
            print(f"New connection {address[0]}:{address[1]}")
            with clients_lock:
                clients.append(client)
                client_info[client] = address
            thread = threading.Thread(target=handle_client, args=(client,), daemon=True)
            thread.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        try:
            server.close()
        except OSError:
            pass
        with clients_lock:
            snapshot = list(clients)
            clients.clear()
        for client in snapshot:
            try:
                client.close()
            except OSError:
                pass

if __name__ == "__main__":
    start_server()
