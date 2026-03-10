import socket
import threading

#server settings
HOST= '127.0.0.1'#Lhost
PORT= 5555
server_pass = 'user0' #server password

#store connected clients
clients= []
nicknames= []

#Broadcast message to all clients
def broadcast(message):
    for client in clients:
        if client is not None:
            try:
                client.send(message)
            except:
                print(f"cliennt disconected {client}: {client.PORT}")
                client.remove(client)
                client.close()

#handle individual client
def handle_client(client):
    while True:
        try:
            message= client.recv(1024)
            broadcast(message)
        except:
            client.close()
            break

#main server function
def start_server():
    print("Enter server password\n")
    pas = input()
    if pas == server_pass: 
    
        server= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)# server being reusable 
        server.bind((HOST, PORT))
        server.listen()
        print(f"Server is listening on {HOST}:{PORT}")

        while True:
            client, address= server.accept()
            print(f"New connection {address[0]}:{address[1]}")
            clients.append(client)
            thread = threading.Thread(target=handle_client, args=(client,))
            thread.start()
    else:
        print("Wrong password")
        exit()

if __name__ == "__main__":
    start_server()