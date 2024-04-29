from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import mimetypes
import pathlib
import datetime
import json
import threading
from socketserver import ThreadingMixIn


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        if url.path == '/':
            self.send_html_file('index.html')
        elif url.path == '/message':
            self.send_html_file('message.html')
        else:
            if pathlib.Path().joinpath(url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('error.html', 404)

    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        data_parse = urllib.parse.unquote_plus(data.decode())
        data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}

        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        formatted_data = {
            current_time: {
                "username": data_dict.get("username", ""),
                "message": data_dict.get("message", "")
            }
        }

        with open("storage/data.json", "r") as jsonfile:
            json_data = json.load(jsonfile)

        json_data.update(formatted_data)

        with open('storage/data.json', 'w') as jsonfile:
            json.dump(json_data, jsonfile)

        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == '__main__':
    http_server_thread = threading.Thread(target=run)
    http_server_thread.start()
