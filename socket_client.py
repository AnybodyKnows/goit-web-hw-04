import socket


def main():
    host = socket.gethostname()
    print(host)
    port = 4000

    socket_client = socket.socket()
    socket_client.connect((host, port))
    message = input(">>> ")

    while message.lower().strip() != "quite":
        socket_client.send(message.encode())
        msg = socket_client.recv(1024).decode()
        print(msg)
        message = input(">>> ")

    socket_client.close()


if __name__ == '__main__':
    main()
