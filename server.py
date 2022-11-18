from core import *
from threading import Thread


def main(argv) -> None:
    # Initialize the server socket that a client will connect to.
    with socket(AF_INET, SOCK_STREAM) as server_socket:
        server_socket.bind((argv.host, argv.port))

        # Wait to establish a connection with a client that tries to connect.
        server_socket.listen()
        print("Server created. Waiting to establish a connection...")

        client_sock, client_addr = server_socket.accept()
        print(f"[{ctime()}] Connected to client {client_addr}.")

        # Initialize the threads for both sending/receiving functionalities and then
        # start the threads. The purpose of this is to allow the server to have a more
        # seamless communication with the client on the other end. Otherwise, communication
        # becomes more complicated.
        sender_thread = Thread(target=sender, args=(client_sock, "server_data"))
        receiver_thread = Thread(target=receiver, args=(client_sock, "server_data"))

        # Start and join the threads.
        sender_thread.start()
        receiver_thread.start()
        sender_thread.join()
        receiver_thread.join()


if __name__ == "__main__":
    main(parse_args())
