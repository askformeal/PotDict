import socket

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
                    server.bind((self.settings.HOST, self.settings.PORT))
                except OSError as e:
                    self.logger.critical(f'Failed to bind to {self.settings.HOST}:{self.settings.PORT}:\n'\
                                         f'    {e}\n'\
                                         '    Possibly because another instance of PotDict is already running, try --no-listener')
                    self.root.exit(code=1, note='Binding failed')
                    
                server.listen(self.settings.MAX_LISTEN)
                self.logger.debug(f'Listening at {self.settings.HOST}:{self.settings.PORT}')
                while True:
                    conn, addr = server.accept()
                    self.logger.debug(f'Connection from {addr}')
                    request = conn.recv(1024).decode('utf-8')
                    request = request.splitlines()[0].split()[1]
                    self.logger.debug(f'Received: {request}')
                    word = request[1:]
                    """ result = self.root.search.on_search(word, False)
                    conn.send(self.get_response(200, result)) """
                    self.root.search.search(word)
                    self.root.win.show_win()
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