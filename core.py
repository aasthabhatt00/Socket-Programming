import argparse
import os
import os.path as osp
import pathlib
import pickle

from socket import socket, AF_INET, SOCK_STREAM
from tabulate import tabulate
from time import ctime
from datetime import datetime, timezone
from utils import *
import pathlib


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

    return host, port


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

    with open(filename, "r") as file:
        text = file.read()

    message = {
        PACKET_HEADER: ":DOWNLOAD:",
        PACKET_PAYLOAD: {"filename": filename, "text": text},
    }
    if message:
        send_msg(conn, pickle.dumps(message))


def delete(conn: socket, filename: str) -> None:
    """Prepares a message to be sent with the filename attached that is to be deleted.

    Args:
        conn (socket): Socket to delete the file from.
        filename (str): Name of the file to be deleted.
    """
    message = {PACKET_HEADER: ":DELETE:", PACKET_PAYLOAD: filename}
    if message:
        send_msg(conn, pickle.dumps(message))


def dir(conn: socket, home_dir) -> None:
    """Prepares a message to be sent to list files existing in the directory.

    Args:
        conn (socket): Socket to list the files from.
        home_dir (str): Name of the directory where the server stores files.
    """
    message = {PACKET_HEADER: ":DIR:", PACKET_PAYLOAD: home_dir}
    if message:
        send_msg(conn, pickle.dumps(message))


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
                upload(conn, f"{home_dir}/{filename}")
                print(f"{filename} successfully uploaded to the server.")
            elif command[0] == ":DELETE:" and len(command) == 2:
                filename = message.split()[1]
                filename = os.path.basename(filename)
                delete(conn, f"{home_dir}/{filename}")
                print(f"{filename} successfully deleted from the server.")
            elif command[0] == ":DIR:":
                dir(
                    conn,
                    osp.join(pathlib.Path(__file__).parent.absolute(), "server_data"),
                )
            elif command[0] == ":DISCONNECT":
                conn.close()
            elif command[0] == ":DOWNLOAD:" and len(command) == 2:
                dir1 = osp.join(pathlib.Path(__file__).parent.absolute(), "server_data")
                filename = message.split()[1]
                filename = os.path.basename(filename)
                download(conn, f"{dir1}/{filename}")
                print(f"{filename} successfully downloaded from the server.")

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
            with open(f"{home_dir}/{filename}", "w") as file:
                file.write(text)
            print(f"[{ctime()}] Saved file '{filename}' to your directory!")

        elif message[PACKET_HEADER] == ":DOWNLOAD:":
            # (1) Get just the filename without the prefacing path.
            # (2) Get the text object.
            # (3) Save the data as a text file to the device's directory.
            dir2 = osp.join(pathlib.Path(__file__).parent.absolute(), "client_data")
            filename = message[PACKET_PAYLOAD]["filename"].split(os.sep)[-1]
            text = message[PACKET_PAYLOAD]["text"]
            with open(f"{dir2}/{filename}", "w") as file:
                file.write(text)
            print(f"[{ctime()}] Downloaded file '{filename}' from the server!")

        elif message[PACKET_HEADER] == ":DELETE:":
            # (1) Get just the filename without the prefacing path.
            # (2) Delete the file from the device's directory.
            filename = message[PACKET_PAYLOAD].split(os.sep)[-1]
            filename = os.path.basename(filename)
            os.remove(f"{home_dir}/{filename}")
            print(f"[{ctime()}] Deleted file '{filename}' from your directory!")

        elif message[PACKET_HEADER] == ":DIR:":
            files = os.scandir(message[PACKET_PAYLOAD])
            if len(os.listdir(message[PACKET_PAYLOAD])) == 0:
                print("The server directory is empty.")
            else:
                table = []
                for file in files:
                    file_stats = os.stat(file)
                    filename = file.name
                    filesize = round(float(file_stats.st_size) / (1024 * 1024), 2)
                    fileupload = datetime.fromtimestamp(
                        file_stats.st_mtime, tz=timezone.utc
                    )
                    table.append([filename, filesize, fileupload, "[PLACEHOLDER]"])

                headers = [
                    "Name",
                    "Size (in MB)",
                    "Upload Date & Time",
                    "Number of Downloads",
                ]
                print(tabulate(table, headers, tablefmt="fancy_grid"))

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