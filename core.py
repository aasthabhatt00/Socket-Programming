import argparse
import os
import pickle
import os.path as osp
from socket import socket, AF_INET, SOCK_STREAM
from time import ctime
from utils import *


def connect():
    """This function opens a connection with the server on the port specified by user.

    Returns:
        A tuple containing the host and port number to create or connect to the server.
    """

    # Default host and port number
    host = "localhost"
    port = 8080

    print("Welcome! Start by connecting to a server. Type ':HELP:' for assistance.")
    while True:
        command = input("> ").split(" ")
        if command[0] == ":HELP:":
            print("Here are the list of available commands:")
            print(
                "   :CONNECT: [HOST] [PORT] - Opens a connection with the server on the specified port.\n"
                "   :EXIT:                  - Terminates the program."
            )
        elif command[0] == ":CONNECT:" and len(command) == 3:
            host = command[1]
            port = int(command[2])
            break
        elif command[0] == ":EXIT:":
            print("Terminating the program.")
            exit()
        else:
            print("Invalid command entered. Starting server on default port number.")
            break
        print()

    return (host, port)


def parse_args() -> argparse.Namespace:
    """Simple function that parses command-line arguments. Currently supports args
    for hostname and port number.

    Returns:
        argparse.Namespace: Arguments for establishing client-server connection.
    """
    host, port = connect()
    args = argparse.ArgumentParser()
    args.add_argument("-n", "--host", type=str, default=host)
    args.add_argument("-p", "--port", type=int, default=port)
    return args.parse_args()


def upload(conn: socket, filename: str) -> None:
    """Prepares a message to be sent with an text file attached to it.

    Args:
        conn (socket): Socket to send message with text to.
        filename (str): Name of the file.
    """
    with open(filename, "r") as file:
        text = file.read()

    message = {
        PACKET_HEADER: ":UPLOAD:",
        PACKET_PAYLOAD: {"filename": filename, "text": text},
    }
    if message:
        send_msg(conn, pickle.dumps(message))


def download(conn: socket, filename: str) -> None:
    """Prepares a message to be sent with the filename attached that is to be downloaded.

    Args:
        conn (socket): Socket to download message with text from.
        filename (str): Name of the file requested for download.
    """


def delete(conn: socket, filename: str) -> None:
    """Prepares a message to be sent with the filename attached that is to be deleted.

    Args:
        conn (socket): Socket to delete the file from.
        filename (str): Name of the file to be deleted.
    """
    message = {PACKET_HEADER: ":DELETE:", PACKET_PAYLOAD: filename}
    if message:
        send_msg(conn, pickle.dumps(message))


def dir(conn: socket, filename: str) -> None:
    """Prepares a message to be sent to list files existing in the directory.

    Args:
        conn (socket): Socket to delete the file from.
        filename (str): Name of the file to be deleted.
    """


def sender(conn: socket, home_dir: str) -> None:
    """Function that will be used in a thread to handle any outgoing messages to
    the provided socket connection.

    Args:
        conn (socket): Socket connection to send messages to.
        home_dir (str): Directory where the client/server's data will be stored.
    """

    while True:
        try:
            message = input(f"[{ctime()}] > ")
            command = message.split(" ")
            if command[0] == ":UPLOAD:" and len(command) == 2:
                filename = message.split()[1]
                upload(conn, f"{home_dir}\{filename}")
                print(f"{filename} successfully uploaded to the server.")
            elif command[0] == ":DELETE:" and len(command) == 2:
                filename = message.split()[1]
                filename = os.path.basename(filename)
                delete(conn, f"{home_dir}\{filename}")
                print(f"{filename} successfully deleted from the server.")
            else:
                message = {PACKET_HEADER: ":MESSAGE:", PACKET_PAYLOAD: message}
                if message:
                    send_msg(conn, pickle.dumps(message))
        except KeyboardInterrupt:
            conn.close()


def handle_received_message(message: dict, home_dir: str) -> None:
    """Function that takes a message and then executes the appropriate actions to
    do the proper functionality in response.

    Args:
        message (dict): The message provided by the connected device.
        home_dir (str): Directory of this client/server's data (in case of uploading).
    """
    if message is not None:
        if message[PACKET_HEADER] == ":UPLOAD:":
            # (1) Get just the filename without the prefacing path.
            # (2) Get the text object.
            # (3) Save the data as a text file to the device's directory.
            filename = message[PACKET_PAYLOAD]["filename"].split(os.sep)[-1]
            text = message[PACKET_PAYLOAD]["text"]
            with open(f"{home_dir}\{filename}", "w") as file:
                file.write(text)
            print(f"[{ctime()}] Saved file '{filename}' to your directory!")
        
        elif message[PACKET_HEADER] == ":DELETE:":
            # (1) Get just the filename without the prefacing path.
            # (2) Delete the file from the device's directory.
            filename = message[PACKET_PAYLOAD].split(os.sep)[-1]
            filename = os.path.basename(filename)
            os.remove(f"{home_dir}\{filename}")
            print(f"[{ctime()}] Deleted file '{filename}' from your directory!")
        
        else:
            print(f"{message[PACKET_PAYLOAD]}")



def receiver(conn: socket, home_dir: str) -> None:
    """Function that will be used in a thread to handle any incoming messages from
    the provided socket connection.

    Args:
        conn (socket): Socket connection to listen to.
        home_dir (str): Directory where the client/server's data will be stored.
    """
    while True:
        try:
            received_msg = recv_msg(conn)
            received_msg = pickle.loads(received_msg)
            handle_received_message(received_msg, home_dir)
        except KeyboardInterrupt:
            conn.close()