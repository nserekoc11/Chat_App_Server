import socket
import threading


HOST = "127.0.0.1"
PORT = 5555


def receiver_messages(client: socket.socket) -> None:
    while True:
        try:
            data = client.recv(1024)
            if not data:
                print("Disconnected from server")
                return
            print(data.decode("utf-8", errors="replace"))
        except OSError:
            print("Disconnected from server")
            return


def start_client() -> int:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((HOST, PORT))
    except OSError as e:
        print(f"Failed to connect to {HOST}:{PORT}: {e}")
        return 1

    print(f"Connected to server {HOST}:{PORT}")
    print("Type messages and press Enter. Use /quit to exit.")

    recv_thread = threading.Thread(target=receiver_messages, args=(client,), daemon=True)
    recv_thread.start()

    try:
        while True:
            try:
                message = input()
            except EOFError:
                break

            if message.strip().lower() in {"/quit", "/exit", "quit", "exit"}:
                break

            try:
                client.sendall(message.encode("utf-8"))
            except OSError:
                print("Disconnected from server")
                break
    except KeyboardInterrupt:
        pass
    finally:
        try:
            client.close()
        except OSError:
            pass

    return 0


if __name__ == "__main__":
    raise SystemExit(start_client())
