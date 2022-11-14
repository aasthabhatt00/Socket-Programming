from core import *
from threading import Thread


def main(argv) -> None:
    # Connect to a server waiting for a connection. Note: the server must be activated
    # first (otherwise an error will be thrown).
    conn = socket(AF_INET, SOCK_STREAM)
    conn.connect((argv.host, argv.port))
    print(f"[{ctime()}] Connected to server '{argv.host}:{argv.port}'.")

    # Initialize the threads for both sending/receiving functionalities and then
    # start the threads. The purpose of this is to allow the client to have a more
    # seamless communication with the server on the other end. Otherwise, communication
    # becomes more complicated.
    sender_thread = Thread(target=sender, args=(conn, "client_dir"))
    receiver_thread = Thread(target=receiver, args=(conn, "client_dir"))

    # Start and join the threads.
    sender_thread.start()
    receiver_thread.start()
    sender_thread.join()
    receiver_thread.join()


if __name__ == "__main__":
    main(parse_args())
