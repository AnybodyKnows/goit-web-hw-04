import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import mimetypes
from jinja2 import Environment, FileSystemLoader
import json


BASE_DIR = Path()

jinja = Environment(loader=FileSystemLoader("templates"))


class GoitFramework(BaseHTTPRequestHandler):

    def do_GET(self):
        route = (urllib.parse.urlparse(self.path))
        print(f"----{route}")
        match route.path:
            case '/':
                self.send_html("index.html")
            case '/message.html':
                self.send_html("message.html")
            case _:
                file = BASE_DIR.joinpath(route.path[1:])
                print(file)
                if file.exists():
                    self.send_static(file)
                else:
                    self.send_html("error.html", 404)

    def do_POST(self):
        pass

    def send_html(self, filename, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        with open(filename, "rb") as file:
            self.wfile.write(file.read())

    def render_template(self, filename, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        with open("storage/db.json", "r", encoding="utf-8") as file:
            data = json.load(file)

        template = jinja.get_template(filename)
        html = template.render(blogs=data)
        self.wfile.write(html.encode())


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


def run_server():
    address = ("localhost", 3000)
    http_server = HTTPServer(address, GoitFramework)
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        http_server.server_close()


if __name__ == '__main__':
    run_server()
