from base64 import decode
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import socketserver
import sys
from ruamel.yaml import YAML
from json import loads, dumps
from os import environ
import hmac
import hashlib

class LoggerWriter:
    """
    Borrowed from http://plumberjack.blogspot.com/2009/09/how-to-treat-logger-like-output-stream.html 
    Assumes input is utf-8 encoded binary. Do not re-use without much testing
    """
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level
        self.buffer = ""

    def write(self, message):
        textmessage = message.decode('utf-8')
        self.buffer += textmessage

    def flush(self):
        self.logger.log(self.level, '\n' + self.buffer.rstrip())
        self.buffer = ""



class S(BaseHTTPRequestHandler):
    """
    Debugging http server. Borrowed from https://gist.github.com/mdonkers/63e115cc0c79b4f6b8b3a6b797e485c7
    """
    def _init_logger(self):
        if not hasattr(self, "logger"):
            self.logger = logging.getLogger("requesthandler")
            self.logger_fp = LoggerWriter(self.logger, logging.INFO)

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()


    def do_GET(self):
        self._init_logger()
        self.logger.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))


    def do_POST(self):
        self._init_logger()
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        self.logger.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                str(self.path), str(self.headers), post_data.decode('utf-8'))
        
        yaml=YAML()
        yaml.default_flow_style = False
        if self.headers.get("Content-Type", None) == "application/json":
            data = loads(post_data.decode('utf-8'))
            self.logger.info("POST data in yaml format")
            yaml.dump(data, self.logger_fp)
            headers = {k:v for k,v in self.headers.items() if isinstance(k, str) and isinstance(v, str)}
            self.logger.info("Headers as key/values")
            yaml.dump(headers, self.logger_fp)

        #Let's check the secret

        secret_token = environ.get("SECRET_TOKEN", None)
        if secret_token is not None:
            signature = hmac.new(bytes(secret_token , 'utf-8'), msg = post_data, digestmod = hashlib.sha256).hexdigest()
            expected_header = f"sha256={signature}"
            actual_header = self.headers.get("X-Hub-Signature-256", "")
            # `hmac.compare_digest` is a super special string comparison. Pretty confident we are still wide open to timing attacks though :D
            if hmac.compare_digest(expected_header, actual_header):
                self.logger.info(f"Security headers matched with signature {signature}")
            else:
                self.logger.info(f"Expected '{expected_header=}' but got '{actual_header}'")


        self._set_response()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))

def run(server_class=HTTPServer, handler_class=S, port=4567):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
