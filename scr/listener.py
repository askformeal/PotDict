import socket
from urllib.parse import urlparse, parse_qs
import threading
from datetime import datetime

class Listener():
    def __init__(self, master, host, port, max_connect, 
                 timeout, max_retries, 
                 homepage_template,
                 result_template,
                 not_found_template,
                 bad_request_template
                 ):
        self.master = master
        self.host = host
        self.port = port
        self.port = port
        self.max_connect = max_connect
        self.timeout = timeout

        self.homepage_template = homepage_template
        self.result_template = result_template
        self.not_found_template = not_found_template
        self.bad_request_template = bad_request_template
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = True

        self.handling = False
        self.max_retries = max_retries
        self.retries_left = self.max_retries
        
        self.HEADER_200 = f'''HTTP/1.1 200 OK
        Content-Type: text/html; charset=UTF-8
        '''

        self.HEADER_400 = f'''HTTP/1.1 400 Bad Request
        Content-Type: text/html; charset=UTF-8
        '''
    
    def super_listener(self, start_time):
        if self.retries_left == 0:
            self.master.logger.log(f'Reached maximum retries, shutdown listener.')
            self.pause_listener()
        while self.handling:
            if (datetime.now().timestamp() - start_time) > self.timeout:
                if self.max_retries != -1:
                    self.retries_left -= 1
                    self.master.logger.log(f'Connection timeout, {self.retries_left} retries remained', 'w')
                else:
                    self.master.logger.log(f'Connection timeout, retry', 'w')
                self.restart_listener()
                break

    def listen_network(self):
        self.server_socket.bind((self.host, self.port))

        self.server_socket.listen(self.max_connect)
        self.master.logger.log(f'Listening at {self.host}:{self.port}...', 'i', output=True)

        while True:
            try:
                client_socket, client_address = self.server_socket.accept()
            except OSError:
                self.master.logger.log("Socket closed", 'd')
                return
            
            self.handling = True
            super_thread = threading.Thread(target=self.super_listener, args=(datetime.now().timestamp(),))
            super_thread.daemon = True
            super_thread.start()
            with client_socket:
                result = None
                self.master.logger.log(f"Connect from: {client_address}", 'd')
                tmp = client_socket.recv(1024).decode('utf-8')
                try:
                    data = urlparse(tmp.splitlines()[0].split()[1])
                    
                except IndexError:
                    self.master.logger.log(f'Bad Request: {tmp}', 'e')
                    continue

                params = parse_qs(data.query)
                path = data.path.split('/')
                while '' in path:
                    path.remove('')
                
                self.master.logger.log(f'Received path: {path}', 'd')
                self.master.logger.log(f'Received params: {params}', 'd')
                query_word = params.get('q', [None])[0]
                
                if len(path) == 0:
                    self.master.logger.log('Access homepage')
                    response = self.homepage_template
                    header = self.HEADER_200
                elif path[0] == 'search' and query_word:
                    result = self.master.search(query_word)
                    if str(type(result)) == '<class \'str\'>':
                        response = self.result_template
                        header = self.HEADER_200
                    else:
                        response = self.not_found_template
                        similar_list = ''
                        for word in result:
                            similar_list += f'''
                                            <font size=\"4\">
                                                    <a href=\"http://{self.HOST}:{self.PORT}/search/?q={word}\">    {word}</a>
                                            </font>
                                            <br>
                                            '''
                        response = response.replace('%S', similar_list)
                        header = self.HEADER_200
                else:
                    self.master.logger.log('Bad Request', 'e')
                    response = self.bad_request_template
                    header = self.HEADER_400
                
                if query_word:
                    response = response.replace('%Q', query_word)
                if result:
                    response = response.replace('%R', str(result))
                response = response.replace('%H', self.host)
                response = response.replace('%P', str(self.port))
                response = response.replace('entry://', f'http://{self.host}:{self.port}/search/?q=')
                response = f'{header}{response}'
                
                client_socket.sendall(response.encode('utf-8'))
                self.master.logger.log("Response sent\n", 'd')
                client_socket.close()
                
                self.handling = False
                self.retries_left = self.max_retries

    def start_listener(self):
        # global thread
        self.master.logger.log('Starting Listener...', 'i', output=True)
        thread = threading.Thread(target=self.listen_network)
        thread.daemon = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        thread.start()

    def stop_listener(self):
        # global thread
        self.master.logger.log('Stopping Listener...', 'i', output=True)
        self.server_socket.close()
    
    def pause_listener(self, event=None):
        self.running = not self.running
        if self.running:
            self.start_listener()
        else:
            self.stop_listener()

    def restart_listener(self, event=None):
        self.master.logger.log('Restarting...\n', 'i', output=True)
        if self.running:
            self.stop_listener()
        self.start_listener()
        self.running = True
