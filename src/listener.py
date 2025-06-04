import socket
import os

from src.settings import Settings
from src.logger import Logger
from src.tools import Tools

class Listener:
    def __init__(self, root):
        self.root = root
        self.settings = Settings()
        self.logger = Logger(__name__, self.root)
        self.tools = Tools(self.root, self.logger)

    def start(self):
        def on_start():
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
                try:
                    server.bind((self.settings.HOST, 
                                self.settings.PORT
                                ))
                except OSError as e:
                    self.logger.critical(f'Failed to bind to {self.settings.HOST}:{self.settings.PORT}:\n'\
                                         f'    {e}\n'\
                                         '    Possibly because an instance of PotDict is already running.')
                    self.root.exit(1)
                    
                server.listen(self.settings.MAX_LISTEN)
                self.logger.debug(f'Listening at {self.settings.HOST}:{self.settings.PORT}')
                while True:
                    conn, addr = server.accept()
                    self.logger.debug(f'Connection from {addr}')
                    request = conn.recv(1024).decode('utf-8')
                    request = request.splitlines()[0].split()[1]
                    self.logger.debug(f'Received: {request}')
                    """ if request == '/':
                        conn.send(self.get_response(200, self.root.html.get('home')))
                    elif request == '/test':
                        conn.send(self.get_response(200, 'hello!'))
                    elif request.startswith('/res'):
                        request = request[5:] # /res/xxxx -> xxxx
                        path = os.path.join(self.settings.DATA_PATHS['res'], request)
                        self.logger.debug(f'Send file: {path}')
                        with open(path, 'rb') as f:
                            data = f.read()
                        t = self.get_type(path)
                        conn.send(self.get_response(200, data, t))
                    elif request.startswith('/entry'):
                        word = request[7:] # /entry/xxxx -> xxxx
                        result = self.root.search.search(word)
                        result = result.replace('entry://', 
                                                f'http://{self.settings.HOST}:{self.settings.PORT}/entry/')
                        result = result.replace('%Q', word)
                        conn.send(self.get_response(200, result)) """
                    conn.close()

        self.tools.start_thread(on_start)

    def get_response(self, code: int, data: str|bytes, 
                     mime_type='text/html') -> bytes:
        if code == 200:
            header = self.settings.HEADER200
        
        if str(type(data)) == '<class \'str\'>':
            data = data.encode('utf-8')

        header = header.replace('%CT', mime_type)
        header = header.replace('%CL', str(len(data)))
        header = header.encode('utf-8')
        
        return header + data