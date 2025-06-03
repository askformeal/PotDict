import sys
import os

class Settings:
    def __init__(self):
        self.VERSION = 'v2.0.3'
        self.GITHUB_REPO = 'https://github.com/askformeal/potdict'

        self.SIZE_RATIO = 5/7 # Width/Height
        self.HEIGHT_RATE = 0.6 # Actual height = screen_height * HEIGHT_RATE
        self.RESIZABLE = False
        self.WIN_PADX = 70
        self.WIN_PADY = 70

        self.DICT_ICON_SIZE = (35,35)
        self.SIMILAR_WORD_SHOWN = 10

        self.LOG_MAX_BYTES = 1024*1024
        self.LOG_BACKUP_CNT = 3
        
        self.PATHS = {
            'log_dir': './logs',
            'options': './options.json'
        }
        work_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
        for k,v in self.PATHS.items():
            self.PATHS[k] = os.path.join(work_dir, v)

        self.DATA_PATHS = {
            'default_options': './data/default_options.json',
            'icon': './data/app.ico',
            'dict_ready': './data/dict_ready.png',
            'dict_loading': './data/dict_loading.png',
            'dict_error': './data/dict_error.png'
        }
        for k,v in self.DATA_PATHS.items():
            self.DATA_PATHS[k] = self.resource_path(v)
    
    def resource_path(self, relative_path):
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        path = os.path.join(base_path, relative_path)
        return path