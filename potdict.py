import socket
from urllib.parse import urlparse, parse_qs
import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext
from readmdict import MDX
from Levenshtein import distance
import webbrowser
import threading
from datetime import datetime
import json
import os
import sys

class Logger():
    def __init__(self, path, display_cmd, level='DEBUG', print_log=False, max_bytes=0):
        self.path = path
        self.display_cmd = display_cmd
        self.level = level
        self.print_log = print_log
        self.max_bytes = max_bytes

    def log(self, msg, level, output=False, nl = False, max_log_bytes=None, log_level=None, print_log=None):
        """ 
        d -> DEBUG
        i -> INFO
        w -> WARNING
        e -> ERROR
        c -> CRITICAL
        """
        
        try:
            self.max_bytes
        except AttributeError:
            self.max_bytes = max_log_bytes
        
        try:
            self.level
        except AttributeError:
            self.level = log_level

        try:
            self.print_log
        except AttributeError:
            self.print_log = print_log

        if not os.path.exists(self.path):
            with open(self.path, 'w', encoding='utf-8') as f:
                self.log('Log file app.log not found, created', 'i')

        size = os.stat(self.path).st_size

        try:
            if size > self.max_bytes and self.max_bytes != 0:
                with open(self.path, 'w', encoding='utf-8') as f:
                    pass
                self.log('Reach max log size, log cleared', 'd')
        except Exception:
            pass

        levels = {
            'd' : 'DEBUG',
            'i': 'INFO',
            'w' : 'WARNING',
            'e' : 'ERROR',
            'c' : 'CRITICAL',
        }

        importance = {
            'DEBUG' : 1,
            'INFO' : 2,
            'WARNING' : 3,
            'ERROR' : 4,
            'CRITICAL' : 5,
        }
        
        level = levels[level]
        if importance[level] >= importance[self.level]:
            
            if output:
                self.display_cmd(f"{msg}")

            if self.print_log:
                print(msg)

            msg = msg.replace('\n', '')

            if nl:
                msg += '\n'
            
            with open(self.path, 'a', encoding='utf-8') as f:
                t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f'[{t}] [{level}] {msg}\n')

    
class Dict():
    def __init__(self, name, headwords, items):
        self.name = name
        self.headwords = headwords
        self.items = items

    def search(self, query_word):
        query_word = query_word.strip()
        try:
            index = self.headwords.index(query_word.encode('utf-8'))
        except ValueError:
            try:
                index = self.headwords.index(query_word.lower().encode('utf-8'))
            except ValueError:
                return None
        
        word, html = self.items[index]
        html = html.decode('utf-8')
        return html

class PotDict(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.VERSION = 'v0.7.0'
    
        self.file_paths = {
            'homepage_html' : './data/html/homepage.html',
            'result_html' : './data/html/result.html',
            'not_found_html' : './data/html/not_found.html',
            '400_html' : './data/html/400.html',
            'default_settings' : './data/default_settings.json',
            'ico' : './data/ico.ico',
        }

        for k, v in self.file_paths.items():
            self.file_paths[k] = self.convert_path(v)
        
        self.HISTORY_PATH = './history.txt'
        self.LOG_PATH = './app.log'
        
        self.logger = Logger(self.LOG_PATH, self.display)
        
        self.load_files()

        self.handling = False
        self.retries_left = self.MAX_RETRIES

        self.code = 0

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.HEADER_200 = f'''HTTP/1.1 200 OK
        Content-Type: text/html; charset=UTF-8
        '''

        self.HEADER_400 = f'''HTTP/1.1 400 Bad Request
        Content-Type: text/html; charset=UTF-8
        '''

        self.running = True

        self.setup_tk()

    def load_settings(self, settings):
        window = settings['window']
        self.WIDTH = window['width']
        self.HEIGHT = window['height']
        self.RESIZE = window['resize']
        self.START_POS_X = window['start_pos_x']
        self.START_POS_Y = window['start_pos_y']
        self.FONT = window['font']
        self.FONT_SIZE = window['font_size']
        
        """ self.BG_COLOR = window['color']['bg_color']
        self.FONT_COLOR = window['color']['font_color']
        self.BG_COLOR_CLICK = window['color']['bg_color_click']
        self.FONT_COLOR_CLICK = window['color']['font_color_click'] """
        
        network = settings['network']
        self.HOST = network['host']
        self.PORT = network['port']
        self.MAX_CONNECT = network['max_connect']
        self.TIMEOUT = network['timeout']
        self.MAX_RETRIES = network['max_retries']
        
        search = settings['search']
        self.DICT_PATHS = search['dict_paths']
        self.SIMILAR_WORD_SHOWN = search['similar_words_shown']
        
        log = settings['log']
        self.logger.level = log['log_level']
        self.logger.print_log = log['print_log']
        self.logger.max_bytes = log['log_max_bytes']
        
    def load_files(self):
        try:
            with open('./settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)

        except FileNotFoundError:
            settings = self.restore_default_settings()
            self.logger.log("File not found: settings.json, create default setting file", 'i',
                     max_log_bytes=settings['log']['log_max_bytes'],
                     log_level=settings['log']['log_level'],
                     print_log=settings['log']['print_log'],)
        except json.decoder.JSONDecodeError:
            self.logger.log("Invalid index in settings.json", 'c',
                        log_level='DEBUG',
                        print_log=False)
            sys.exit(1)

        self.load_settings(settings)

        self.dicts = []
        self.headwords = []
        for path in self.DICT_PATHS:
            if not os.path.exists(path):
                self.logger.logger(f'Dictionary not found: {path}', 'c')
                self.exit_server(1)
            name = os.path.splitext(os.path.basename(path))[0]

            headwords = [*MDX(path, encoding='utf-8')]
            items = [*MDX(path, encoding='utf-8').items()]
            
            self.dicts.append(Dict(name, headwords, items))
            self.headwords += headwords
        self.headwords = set(self.headwords)

        try:
            with open(self.file_paths['homepage_html'], 'r', encoding='utf-8') as f:
                self.homepage_template = f.read()
        except FileNotFoundError:
            self.logger.log('File not found: homepage.html', 'c')
            self.exit_server(code=1)

        try:
            with open(self.file_paths['result_html'], 'r', encoding='utf-8') as f:
                self.result_template = f.read()
        except FileNotFoundError:
            self.logger.log('File not found: result.html', 'c')
            self.exit_server(code=1)

        try:
            with open(self.file_paths['not_found_html'], 'r', encoding='utf-8') as f:
                self.not_found_template = f.read()
        except FileNotFoundError:
            self.logger.log('File not found: not_found.html', 'c')
            self.exit_server(code=1)

        try:
            with open(self.file_paths['400_html'], 'r', encoding='utf-8') as f:
                self.bad_request_template = f.read()
        except FileNotFoundError:
            self.logger.log('File not found: 400.html', 'c')
            self.exit_server(code=1)

    def restore_default_settings(self):
        try:
            with open(self.file_paths['default_settings'], 'r', encoding='utf-8') as f1:
                settings = json.load(f1)
                with open('settings.json', 'w', encoding='utf-8') as f2:
                    json.dump(settings, f2, indent=4)
                return settings
        except:
            self.logger.log("File not found: default_settings.json", 'c',
                        log_level='DEBUG',
                        print_log=False)
            sys.exit(1)

    def convert_path(self, path):
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath('.')
        path_result = os.path.join(base_path, path)
        return path_result

    def display(self, text):
        try:
            self.text.config(state='normal')
        except AttributeError:
            self.logger.log("ScrolledText not found, display canceled", 'w', output=False)
        self.text.insert('end', f'{text}\n')
        self.text.see('end')
        self.text.config(state='disabled')

    # def log(self, msg, level = 'd', output=False, nl = False, max_log_bytes=None, log_level=None, print_log=None):
    #     """ 
    #     d -> DEBUG
    #     i -> INFO
    #     w -> WARNING
    #     e -> ERROR
    #     c -> CRITICAL
    #     """
        
    #     try:
    #         self.LOG_MAX_BYTES
    #     except AttributeError:
    #         self.LOG_MAX_BYTES = max_log_bytes
        
    #     try:
    #         self.LOG_LEVEL
    #     except AttributeError:
    #         self.LOG_LEVEL = log_level

    #     try:
    #         self.PRINT_LOG
    #     except AttributeError:
    #         self.PRINT_LOG = print_log

    #     if not os.path.exists(self.LOG_PATH):
    #         with open(self.LOG_PATH, 'w', encoding='utf-8') as f:
    #             self.log('Log file app.log not found, created', 'i')

    #     size = os.stat(self.LOG_PATH).st_size

    #     try:
    #         if size > self.LOG_MAX_BYTES:
    #             with open(self.LOG_PATH, 'w', encoding='utf-8') as f:
    #                 pass
    #             self.log('Reach max log size, log cleared', 'd')
    #     except Exception:
    #         pass

    #     levels = {
    #         'd' : 'DEBUG',
    #         'i': 'INFO',
    #         'w' : 'WARNING',
    #         'e' : 'ERROR',
    #         'c' : 'CRITICAL',
    #     }

    #     importance = {
    #         'DEBUG' : 1,
    #         'INFO' : 2,
    #         'WARNING' : 3,
    #         'ERROR' : 4,
    #         'CRITICAL' : 5,
    #     }
        
    #     level = levels[level]
    #     if importance[level] >= importance[self.LOG_LEVEL]:
            
    #         if output:
    #             self.display(f"{msg}")

    #         if self.PRINT_LOG:
    #             print(msg)

    #         msg = msg.replace('\n', '')

    #         if nl:
    #             msg += '\n'
            
    #         with open(self.LOG_PATH, 'a', encoding='utf-8') as f:
    #             t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #             f.write(f'[{t}] [{level}] {msg}\n')

    
    def get_similar_words(self, word, headwords):
        similar_words = {}
        for headword in headwords:
            headword = headword.decode('utf-8')
            sim = distance(word, headword)
            if len(similar_words) < self.SIMILAR_WORD_SHOWN:
                similar_words[headword] = sim
            else:
                similar_words = dict(sorted(similar_words.items(), key=lambda item: item[1]))
                del similar_words[list(similar_words.keys())[-1]]
                similar_words[headword] = sim
        return list(similar_words.keys())

    def search(self, query_word):
        results = ''
        last = ''
        blank_file = False
        if not os.path.exists(self.HISTORY_PATH):
            with open(self.HISTORY_PATH, 'w') as f:
                self.logger.log('History file not found, created', 'i')
        with open(self.HISTORY_PATH, 'r', encoding='utf-8') as f:
            try:
                last = f.readlines()[-1].split()[-1]
            except IndexError:
                blank_file = True
        
        with open(self.HISTORY_PATH, 'a', encoding='utf-8') as f:
            if last != query_word or blank_file:
                t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f'{t} | {query_word}\n')
        
        for dict in self.dicts:
            name = dict.name
            self.logger.log(f'Searching {query_word} in {name}...', 'd')
            result = dict.search(query_word)
            if result:
                self.logger.log(f'Found', 'd')
                results += f'''
                            <h2 style="color: red;">{name}</h2>
                            <hr color="red" size="3"/>
                            {result}
                            '''
            else:
                self.logger.log(f'Not found', 'd')
        if len(results) == 0:
            self.logger.log(f'No definition for \"{query_word}\"', 'd')
            return self.get_similar_words(query_word, self.headwords)
        else:
            return results

    def super_listener(self, start_time):
        if self.retries_left == 0:
            self.logger.log(f'Reached maximum retries, shutdown listener.')
            self.pause_listener()
        while self.handling:
            if (datetime.now().timestamp() - start_time) > self.TIMEOUT:
                if self.MAX_RETRIES != -1:
                    self.retries_left -= 1
                    self.logger.log(f'Connection timeout, {self.retries_left} retries remained', 'w', output=True)
                else:
                    self.logger.log(f'Connection timeout, retry', 'w', output=True)
                self.restart_listener()
                break

    def listen_network(self):
        self.server_socket.bind((self.HOST, self.PORT))

        self.server_socket.listen(self.MAX_CONNECT)
        self.logger.log(f'Listening at {self.HOST}:{self.PORT}...', 'i', output=True)

        while True:
            try:
                client_socket, client_address = self.server_socket.accept()
            except OSError:
                self.logger.log("Socket closed", 'd', output=True)
                return
            
            self.handling = True
            super_thread = threading.Thread(target=self.super_listener, args=(datetime.now().timestamp(),))
            super_thread.daemon = True
            super_thread.start()
            with client_socket:
                result = None
                self.logger.log(f"Connect from: {client_address}", 'd')
                tmp = client_socket.recv(1024).decode('utf-8')
                try:
                    data = urlparse(tmp.splitlines()[0].split()[1])
                    
                except IndexError:
                    self.logger.log(f'Bad Request: {tmp}', 'e')
                    continue

                params = parse_qs(data.query)
                path = data.path.split('/')
                while '' in path:
                    path.remove('')
                
                self.logger.log(f'Received path: {path}', 'd')
                self.logger.log(f'Received params: {params}', 'd')
                query_word = params.get('q', [None])[0]
                
                if len(path) == 0:
                    self.logger.log('Access homepage')
                    response = self.homepage_template
                    header = self.HEADER_200
                elif path[0] == 'search' and query_word:
                    result = self.search(query_word)
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
                    self.logger.log('Bad Request', 'e', output=False)
                    response = self.bad_request_template
                    header = self.HEADER_400
                
                if query_word:
                    response = response.replace('%Q', query_word)
                if result:
                    response = response.replace('%R', str(result))
                response = response.replace('%H', self.HOST)
                response = response.replace('%P', str(self.PORT))
                response = response.replace('entry://', f'http://{self.HOST}:{self.PORT}/search/?q=')
                response = f'{header}{response}'
                
                client_socket.sendall(response.encode('utf-8'))
                self.logger.log("Response sent\n", 'd')
                
                self.handling = False
                self.retries_left = self.MAX_RETRIES


    def start_listener(self):
        global thread
        self.logger.log('Starting Listener...', 'i', output=True)
        thread = threading.Thread(target=self.listen_network)
        thread.daemon = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        thread.start()

    def stop_listener(self):
        global thread
        self.logger.log('Stopping Listener...', 'i', output=True)
        self.server_socket.close()
    
    def pause_listener(self, event=None):
        self.running = not self.running
        if self.running:
            self.start_listener()
        else:
            self.stop_listener()                  

    def exit_server(self, code = 0, event=None):
        try:
            self.stop_listener()
            self.logger.log('Exiting server...', 'i', output=True, nl=True)
        except Exception as e:
            self.logger.log(f'Exception when exiting: {e}', 'e', log_level='DEBUG', print_log=True)
            sys.exit(code)
        self.code = code
        self.quit()
        self.destroy()

    def restart_listener(self, event=None):
        self.logger.log('Restarting...\n', 'i', output=True)
        self.stop_listener()
        self.start_listener()
    
    def search_in_browser(self, event=None):
        query_word = self.search_entry.get()
        if len(query_word) > 0:
            webbrowser.open(f'http://{self.HOST}:{self.PORT}/search/?q={query_word}')
        self.search_entry.delete(0, 'end')

    def open_homepage(self):
        webbrowser.open(f'http://{self.HOST}:{self.PORT}')

    def open_settings(self):
        try:
            os.startfile('./settings.json')
        except FileNotFoundError:
            self.logger.log("File not found: settings.json", 'c')
            sys.exit(1)

    def open_repo(self):
        webbrowser.open('https://github.com/askformeal/PotDict')

    def show_about(self):
        about = f'''PotDict {self.VERSION}
By Demons1014'''
        messagebox.showinfo(title='About', message = about)

    def clear_screen(self):
        self.text.config(state='normal')
        self.text.delete("1.0", 'end')
        self.text.config(state='disabled')

    def setup_tk(self):

        # Window
        self.title("PotDict - Demons1014")
        self.iconbitmap(self.file_paths['ico'])
        self.geometry(f'{self.WIDTH}x{self.HEIGHT}+{self.START_POS_X}+{self.START_POS_Y}')
        self.resizable(self.RESIZE,self.RESIZE)
        self.config(bg='LightGrey')
        self.option_add("*Font", f"{self.FONT} {self.FONT_SIZE}")

        # Events
        self.protocol('WM_DELETE_WINDOW', self.exit_server)

        self.bind('<Key-q>', self.exit_server)
        self.bind('<Key-r>', self.restart_listener)
        self.bind('<Key-p>', self.pause_listener)
        
        # Menus
        menu_frame = tk.Frame(self)
        menu_frame.pack()

        menu = tk.Menu(menu_frame)
        self.config(menu=menu)
        
        file_menu = tk.Menu(menu, tearoff=False)
        menu.add_cascade(label='File', menu=file_menu)

        file_menu.add_command(label="Open Homepage", command=self.open_homepage)
        file_menu.add_command(label='Open settings.json', command=self.open_settings)
        file_menu.add_command(label='Restart listener', accelerator='r', command=self.restart_listener)
        file_menu.add_command(label='Start/Stop Listener', accelerator='p', command=self.pause_listener)
        file_menu.add_separator()
        file_menu.add_command(label='Exit', accelerator='q', command=self.exit_server)


        edit_menu=tk.Menu(menu_frame, tearoff=False)
        menu.add_cascade(label='Edit', menu=edit_menu)

        edit_menu.add_command(label='Clear screen', accelerator='c', command=self.clear_screen)


        help_menu = tk.Menu(menu, tearoff=False)
        menu.add_cascade(label='Help', menu=help_menu)

        help_menu.add_command(label='Open GitHub Repository', command=self.open_repo)
        help_menu.add_separator()
        help_menu.add_command(label='About', command=self.show_about)

        # Search entry
        search_fr = tk.Frame(self, bg='LightGrey')
        search_fr.pack(fill='x', padx=5, pady=5)

        self.search_entry = tk.Entry(search_fr)
        self.search_entry.bind('<Return>', self.search_in_browser)
        self.search_entry.pack(side='left', expand=True, fill='both', padx=(0,5))
        self.search_entry.focus_set()

        search_button = tk.Button(search_fr, text="Search", command=self.search_in_browser)
        search_button.pack(side='left')

        # Buttons
        buttons_fr = tk.Frame(self, bg='LightGrey')
        buttons_fr.pack(fill='x', padx=5, pady=(5,5))

        exit_button = tk.Button(buttons_fr, text='Exit', relief='raised', command=self.exit_server)
        exit_button.pack(side='left', expand=True, fill='x', padx=(0,5))

        restart_button = tk.Button(buttons_fr, text='Restart', relief='raised', command=self.restart_listener)
        restart_button.pack(side='left', expand=True, fill='x', padx=(0,5))
        
        pause_button = tk.Button(buttons_fr, text='Pause', relief='raised', command=self.pause_listener)
        pause_button.pack(side='left', expand=True, fill='x', padx=(0, 5))

        clear_button = tk.Button(buttons_fr, text='Clear', relief='raised', command=self.clear_screen)
        clear_button.pack(side='left', expand=True, fill='x')

        # text
        text_fr = tk.Frame(self)
        text_fr.pack(side='top', fill='both', expand=True, pady=(0,5))
        
        self.text = scrolledtext.ScrolledText(text_fr)
        self.text.config(height=12, state='disabled')
        self.text.pack(side='top', fill='both', expand=True, padx=(5,0))

        # Label
        label = tk.Label(self, text=f'PotDict {self.VERSION}\nBy Demons1014', 
                        height=5, 
                        bg='DimGray', fg='Lime', 
                        relief='groove', bd=3, 
                        font=(self.FONT, self.FONT_SIZE, 'bold'))
        label.pack(fill='both', padx=20, pady=(5,10))

    def main(self):
        
        self.display("Press q to exit")
        self.display("Press r to restart listener")
        self.display("Press p to pause")
        self.display("Press c to clear screen\n")

        self.start_listener()

        self.mainloop()
           

if __name__ == '__main__':
    potdict = PotDict()
    try:
        potdict.main()
        sys.exit(0)
    except Exception as e:
        potdict.logger.log(f'Almost uncaught Exception: \"{e}\"', 'c', True, True)
        sys.exit(1)