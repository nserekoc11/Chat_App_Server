import socket 
import threading
from server import start_server


#client settings
HOST = '127.0.0.1'
PORT = 5555



#reciever messages from server
def reciever_messages(client):
    while True:
        try:
            message= client.recv(1024).decode()
            print(message)
        except:
            print ("Disconected from server")
            client.close()
            break



#send messages to server
def send_message(client):
    while True:
        message = input()
        client.send(message.encode())
        if message == f"exit({PORT})":
            client.close()
            break

#main client function 
def start_client(start_server):
    client= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client, address = start_server.accept()
    print(f"ID {address[0]}:{address[1]}")
    print(f"Connected to server {HOST}:{PORT}")
    

    #start threads
    recieve_thread = threading.Thread(target=reciever_messages, args=(client,))
    recieve_thread.start()

    send_thread = threading.Thread(target=send_message, args=(client,))
    send_thread.start()
    
    #show recently joined user



if __name__ == "__main__":
    start_client(start_server)