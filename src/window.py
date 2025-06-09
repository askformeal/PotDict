import tkinter as tk
from tkinter import messagebox
from urllib.parse import urlparse
from random import choice
import webbrowser

from tkinterweb import HtmlFrame

import src
import src.main
from src.settings import Settings
from src.logger import Logger
from src.tools import Tools

class Window(tk.Tk):
    def __init__(self, root):
        super().__init__()
        self.root: src.main.PotDict = root
        self.settings = Settings()
        self.logger = Logger(__name__, self.root)
        self.tools = Tools(self.root, self.logger)

    def setup(self):
        def on_focus_out(event):
            if event.widget.focus_get() == None and self.root.option.eolf and not self.disable_eolf:
                self.root.exit(note='lost focus')

        def show_about():
            tmp = lambda: messagebox.showinfo('About', 
                                              f'PotDict v{src.__version__}\n'\
                                              'By Demons1014\n'\
                                              'License: GPL v3.0'\
                                              'Translation API: https://appworlds.cn/translate')
            self.pause_eolf(tmp)
        self.protocol('WM_DELETE_WINDOW', self.hide_win)
        self.bind_all('<FocusOut>', on_focus_out)
        self.bind('<Control-p>', lambda event: self.option.set_options())

        self.title(f'PotDict v{src.__version__}')
        height = int(self.winfo_screenheight() * self.settings.HEIGHT_RATE)
        width = int(self.settings.SIZE_RATIO * height)

        self.geometry(f'{width}x{height}+{self.settings.WIN_PADX}+{self.settings.WIN_PADY}')
        self.resizable(self.settings.RESIZABLE, self.settings.RESIZABLE)
        self.iconbitmap(self.settings.DATA_PATHS['icon'])

        menubar = tk.Menu(self)
        self.config(menu=menubar)

        file_menu = tk.Menu(self, tearoff=False)
        file_menu.add_separator()
        file_menu.add_command(label='Exit', command=lambda: self.root.exit(note='via menu'), 
                              underline=0)

        edit_menu = tk.Menu(self, tearoff=False)
        edit_menu.add_command(label='Clear log', command=self.root.clear_logs, underline=0)
        edit_menu.add_command(label='Shake', command=self.shake_win, underline=0)
        edit_menu.add_separator()
        edit_menu.add_command(label='Options', accelerator='Ctrl+P',
                              command=self.root.option.set_options, underline=0)
        
        help_menu = tk.Menu(self, tearoff=False)
        help_menu.add_command(label='Open GitHub repo', 
                              command=lambda: webbrowser.open(self.settings.GITHUB_REPO),
                              underline=0)
        help_menu.add_separator()
        help_menu.add_command(label='About', command=show_about, underline=0)
        
        menubar.add_cascade(label='File', menu=file_menu, underline=0)
        menubar.add_cascade(label='Edit', menu=edit_menu, underline=0)
        menubar.add_cascade(label='Help', menu=help_menu, underline=0)

        fr = tk.Frame(self)
        fr.pack(fill='x',padx=2, pady=2)

        self.search_entry = tk.Entry(fr)
        self.search_entry.bind('<Return>', 
                               lambda event: self.root.search.search(self.search_entry.get()))
        self.search_entry.pack(side='left', fill='both', expand=True)

        btn = tk.Button(fr, text='Search', 
                        command=lambda: self.root.search.search(self.search_entry.get()))
        btn.pack(side='left', fill='both', expand=True, padx=(3,0))

        self.page = HtmlFrame(self, messages_enabled=False, on_link_click=self.on_link_click)
        self.page_content = ''
        self.page.pack(fill='both', expand=True)

        self.logger.debug('Window setup completed')

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
        self.update()

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
        template = template.replace('%S', sim_list)
        self.set_page(template)            
    
    def on_link_click(self, url):
        self.logger.debug(f'Page link clicked: {url}')
        url = urlparse(url)
        if url.scheme == 'entry':
            self.root.search.search(url.netloc)
            
    def shake_win(self):
        def on_shake():
            x = self.winfo_x()
            y = self.winfo_y()
            for i in range(1500):
                self.geometry(f'+{x+choice((-2,2))}+{y+choice((-2,2))}')
            self.geometry(f'+{x}+{y}')
        self.tools.start_thread(target=on_shake)

    def raise2top(self):
        self.attributes("-topmost", True)
        self.attributes("-topmost", False)

    def show_win(self):
        """Show window
        """        
        self.logger.info('Show window')
        self.deiconify()
        self.raise2top()
        
    def hide_win(self, event=None):
        """Hide window
        """        
        if self.state() == 'normal':
            self.logger.info('Hide window')
            self.withdraw()

    def pause_eolf(self, f):
        self.disable_eolf = True
        val = f()
        self.disable_eolf = False
        return val