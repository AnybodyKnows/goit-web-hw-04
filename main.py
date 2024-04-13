import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import mimetypes
from jinja2 import Environment, FileSystemLoader
import json
import logging
from threading import Thread
import socket
from datetime import datetime

# command to build docker image:
# docker build . -t anybodyknows/http-server

BASE_DIR = Path()
BUFFER_SIZE = 1024
HTTP_PORT = 3000
HTTP_HOST = '0.0.0.0'
SOCKET_HOST = "127.0.0.1"
SOCKET_PORT = 5000


class GoitFramework(BaseHTTPRequestHandler):

    def do_GET(self):
        route = (urllib.parse.urlparse(self.path))
        match route.path:
            case '/':
                self.send_html("index.html")
            case '/message.html':
                self.send_html("message.html")
            case _:
                file = BASE_DIR.joinpath(route.path[1:])
                if file.exists():
                    self.send_static(file)
                else:
                    self.send_html("error.html", 404)

    def do_POST(self):
        size = self.headers.get('Content-Length')
        data = self.rfile.read(int(size))
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.sendto(data, (SOCKET_HOST, SOCKET_PORT))
        client_socket.close()
        self.send_response(302)
        self.send_header('Location', '/message.html')
        self.end_headers()

    def send_html(self, filename, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        with open(filename, "rb") as file:
            self.wfile.write(file.read())

    def send_static(self, filename, status_code=200):
        self.send_response(status_code)
        mime_type = mimetypes.guess_type(filename)[0]
        if mime_type:
            self.send_header('Content-Type', mime_type)
        else:
            self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        with open(filename, "rb") as file:
            self.wfile.write(file.read())


def save_message(data, timestamp):
    parse_data = urllib.parse.unquote_plus(data.decode())

    try:
        parse_dict = {key: value for key, value in [el.split('=') for el in parse_data.split('&')]}
        parse_dict = {timestamp: parse_dict}
        print(parse_dict)
        with open("storage/data.json", 'a', encoding='utf-8') as file:
            json.dump(parse_dict, file, ensure_ascii=False, indent=4)
    except ValueError as err:
        logging.error(err)
    except OSError as err:
        logging.error(err)


def run_socket_server(host, port):
    socket_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket_server.bind((host, port))
    logging.info("Starting socket server")
    try:
        while True:
            msg, address = socket_server.recvfrom(BUFFER_SIZE)
            logging.info(f"Socket received{address}: {msg}")
            save_message(msg, str(datetime.now()))
    except KeyboardInterrupt:
        socket_server.close()


def run_http_server(host, port):
    address = (host, port)
    http_server = HTTPServer(address, GoitFramework)
    logging.info("Starting http server")
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        http_server.server_close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format="%(threadName)s %(message)s")

    server = Thread(target=run_http_server, args=(HTTP_HOST, HTTP_PORT))
    server.start()

    server_socket = Thread(target=run_socket_server, args=(SOCKET_HOST, SOCKET_PORT))
    server_socket.start()

