import socket


def main():
    host = socket.gethostname()
    print(host)
    port = 4000

    socket_server = socket.socket()
    socket_server.bind((host, port))
    socket_server.listen()

    conn, address = socket_server.accept()
    print(f"connection from {address}")
    while True:
        msg = conn.recv(1024).decode()
        if not msg:
            break
        print(msg)
        message = input(">>> ")
        conn.send(message.encode())
    conn.close()
    socket_server.close()




if __name__ == '__main__':
    main()