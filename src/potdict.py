import tkinter as tk
from tkinter import messagebox
import webbrowser
from urllib.parse import urlparse
from random import choice
import winsound
import sys
import os

from tkinterweb import HtmlFrame

import src
from src.settings import Settings
from src.option import Option
from src.logger import Logger
from src.search import Search
from src.tools import Tools

class PotDict:
    def __init__(self):
        self.settings = Settings()
        self.option = Option(self)
        self.option.load()
        self.logger = Logger(__name__, self)

        work_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
        self.logger.debug(f'Work dir: {work_dir}')

        if hasattr(sys, '_MEIPASS'):
            self.env = 'app'
            self.logger.debug('Environment: Application')
        else:
            self.env = 'dev'
            self.logger.debug('Environment: Developing')

        self.query_word = ''
        self.logger.debug(f'argv: {sys.argv}')
        if len(sys.argv) > 1:
            for arg in sys.argv[1:]:
                if arg == '--exit-on-lost-focus':
                    self.option.exit_on_focus_out = True
                    self.logger.info('Will exit on lost focus')
                else:
                    self.query_word = arg
                    self.logger.info(f'Query word set to \"{self.query_word}\"')

        self.tools = Tools(self)
        self.setup_win()
        self.search = Search(self)
        self.search.load()
        # self.tools.start_thread(self.search.load, join=True)

        self.disable_exit_on_focus_out = False

        self.logger.debug('Main module initialized')

    def clear_logs(self):
        """Clear log files
        """        
        self.logger.clear()
        self.option.logger.clear()
        self.search.logger.clear()
        self.tools.logger.clear()
        
    def on_link_click(self, url):
        self.logger.debug(f'Page link clicked: {url}')
        url = urlparse(url)
        if url.scheme == 'entry':
            self.search.search(url.netloc)

    def set_page(self, data: str, mode: str='s'):
        """
        modes:
        s -> set (overwrite)
        a -> append
        """
        if mode == 's':
            self.page_content = data
        elif mode == 'a':
            self.page_content += data
        self.page.load_html(self.page_content)
        self.win.update()

    def set_similar_list(self, query_word: str, sim_words: list[str]):
        self.set_page('')
        with open(self.settings.DATA_PATHS['not_found_html'], 'r', encoding='utf-8') as f:
            template = f.read()

        template = template.replace('%Q', query_word)
        sim_list = ''
        for i in range(len(sim_words)):
            word = sim_words[i]
            sim_list += '<font size=\"4\">'\
                        f'<a id=\"{i}\" href=\"entry://{word}\">{word}</a>'\
                        '</font><br>\n'
        print(sim_list)
        template = template.replace('%S', sim_list)
        self.set_page(template)            
    
    def shake_win(self):
        def on_shake():
            x = self.win.winfo_x()
            y = self.win.winfo_y()
            for i in range(1500):
                self.win.geometry(f'+{x+choice((-2,2))}+{y+choice((-2,2))}')
            self.win.geometry(f'+{x}+{y}')
        self.tools.start_thread(target=on_shake)


    def setup_win(self):
        def on_focus_out(event):
            if event.widget.focus_get() == None and self.option.exit_on_focus_out and not self.disable_exit_on_focus_out:
                self.logger.debug('Lost focus, exit')
                self.exit()

        def show_about():
            self.disable_exit_on_focus_out = True
            messagebox.showinfo('About', f'PotDict v{src.__version__}\n'\
                                         'By Demons1014\n'\
                                         'License: GPL v3.0')
            self.disable_exit_on_focus_out = False
        self.win = tk.Tk()
        
        self.win.protocol('WM_DELETE_WINDOW', self.exit)
        self.win.bind_all('<FocusOut>', on_focus_out)
        self.win.bind('<Control-p>', lambda event: self.option.set_options())

        self.win.title(f'PotDict v{src.__version__}')
        height = int(self.win.winfo_screenheight() * self.settings.HEIGHT_RATE)
        width = int(self.settings.SIZE_RATIO * height)

        self.win.geometry(f'{width}x{height}+{self.settings.WIN_PADX}+{self.settings.WIN_PADY}')
        self.win.resizable(self.settings.RESIZABLE, self.settings.RESIZABLE)
        self.win.iconbitmap(self.settings.DATA_PATHS['icon'])

        menubar = tk.Menu(self.win)
        self.win.config(menu=menubar)

        file_menu = tk.Menu(self.win, tearoff=False)
        file_menu.add_separator()
        file_menu.add_command(label='Exit', command=self.exit, underline=0)

        edit_menu = tk.Menu(self.win, tearoff=False)
        edit_menu.add_command(label='Clear log', command=self.clear_logs, underline=0)
        edit_menu.add_command(label='Shake', command=self.shake_win, underline=0)
        edit_menu.add_separator()
        edit_menu.add_command(label='Options', accelerator='Ctrl+P',
                              command=self.option.set_options, underline=0)
        
        help_menu = tk.Menu(self.win, tearoff=False)
        help_menu.add_command(label='Open GitHub repo', 
                              command=lambda: webbrowser.open(self.settings.GITHUB_REPO),
                              underline=0)
        help_menu.add_separator()
        help_menu.add_command(label='About', command=show_about, underline=0)
        
        menubar.add_cascade(label='File', menu=file_menu, underline=0)
        menubar.add_cascade(label='Edit', menu=edit_menu, underline=0)
        menubar.add_cascade(label='Help', menu=help_menu, underline=0)

        fr = tk.Frame(self.win)
        fr.pack(fill='x',padx=2, pady=2)

        self.search_entry = tk.Entry(fr)
        self.search_entry.bind('<Return>', 
                               lambda event: self.search.search(self.search_entry.get()))
        self.search_entry.pack(side='left', fill='both', expand=True)

        btn = tk.Button(fr, text='Search', 
                        command=lambda: self.search.search(self.search_entry.get()))
        btn.pack(side='left', fill='both', expand=True, padx=(3,0))

        self.page = HtmlFrame(self.win, messages_enabled=False, on_link_click=self.on_link_click)
        self.page_content = ''
        self.page.pack(fill='both', expand=True)

        self.logger.debug('Window setup completed')

    def exit(self, code=0):
        try:
            self.search.clear_res()
            if code == 0:
                self.logger.info('Exit with code 0')
            else:
                self.logger.critical(f'Exit with code {code}')
            self.win.destroy()
            self.win.quit()
        except:
            sys.exit()


    def start(self):
        self.logger.info('Start main')
        if self.query_word != '':
            self.search_entry.insert('end', self.query_word)
            self.search.search(self.query_word)
        self.win.update()
        self.win.mainloop()