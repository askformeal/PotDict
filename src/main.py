import sys
import os

from pystray import Menu, MenuItem, Icon
from PIL import Image

from src.settings import Settings
from src.option import Option
from src.logger import Logger
from src.window import Window
from src.search import Search
from src.listener import Listener
from src.tools import Tools

class PotDict:
    def __init__(self):
        self.settings = Settings()
        self.option_ready = False
        self.option = Option(self)
        self.option.load()
        self.option_ready = True
        self.logger = Logger(__name__, self)

        work_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
        self.logger.debug(f'Work dir: {work_dir}')

        if hasattr(sys, '_MEIPASS'):
            self.env = 'app'
            self.logger.debug('Environment: Application')
        else:
            self.env = 'dev'
            self.logger.debug('Environment: Developing')

        self.logger.debug(f'argv: {sys.argv}')
        
        self.query_word = ''
        start_listener = True
        if len(sys.argv) > 1:
            for arg in sys.argv[1:]:
                if arg == '--exit-on-lost-focus':
                    self.option.eolf = True
                    self.logger.info('Will exit on lost focus')
                elif arg == '--no-listener':
                    self.logger.info('No-listener mode activated')
                    start_listener = False
                else:
                    self.query_word = arg
                    self.logger.info(f'Query word set to \"{self.query_word}\"')

        self.tools = Tools(self)
        self.win = Window(self)
        self.win.setup()

        menu = (MenuItem('Show Window', self.win.show_win, default=True),
                Menu.SEPARATOR, 
                MenuItem('Exit', lambda: self.exit(note='via stray icon'))
                )
        image = Image.open(self.settings.DATA_PATHS['icon'])
        self.icon = Icon('potdict', image, 
                    'PotDict', menu)

        self.search = Search(self)
        self.search.load()
        # self.tools.start_thread(self.search.load, join=True)

        self.disable_eolf = False

        self.listener = Listener(self)
        if start_listener:
            self.listener.start()
        self.logger.debug('Main module initialized')

    def clear_logs(self):
        """Clear log files
        """        
        self.logger.clear()
        self.option.logger.clear()
        self.search.logger.clear()
        self.tools.logger.clear()

    def start(self):
        self.logger.info('Start main')
        self.tools.start_thread(self.icon.run)
        if self.query_word != '':
            self.win.search_entry.insert('end', self.query_word)
            self.search.search(self.query_word)
        self.win.update()
        self.win.mainloop()
    
    def exit(self, code=0, note=''):
        try:
            self.search.clear_res()
            if code == 0:
                self.logger.info(f'Exit with code 0, \"{note}\"')
            else:
                self.logger.critical(f'Exit with code {code}, \"{note}\"')
            self.win.destroy()
            self.win.quit()
        except:
            sys.exit()