from tkinter import filedialog
from tkinter import messagebox
from time import perf_counter
import shutil
import os

from Levenshtein import distance

from src.settings import Settings
from src.dict import Dict
from src.logger import Logger
from src.tools import Tools

class Search:
    def __init__(self, root):
        self.root = root
        self.dir = self.root.option.dict_path
        self.settings = Settings()
        self.logger = Logger(__name__, self.root)
        self.dicts: list[Dict] = []
        self.headwords = []
        
        self.tools = Tools(self.root)
        self.set_dict_state(0)
        self.results = ''
        self.dicts_left = len(self.dicts)
        self.logger.debug('Search module initialized')
        
    def set_dict_state(self, code, progress: tuple[int, int]|None=None, clear=False):
        """
        codes:\n
        0 -> ready\n
        1 -> loading\n
        2 -> error\n
        """
        if code == 0:
            self.dict_state = 'ready'
        
        elif code == 1:
            self.dict_state = 'loading'
            
        elif code == 2:
            self.dict_state = 'error'

    def load(self, load_single=False):
        """Load dicts
        """
        with open(self.settings.DATA_PATHS['loading_html'], 'r', encoding='utf-8') as f:
            self.root.set_page(f.read(), 's')
        start_time = perf_counter()
        self.set_dict_state(1, clear=True)
        if load_single:
            self.logger.info('Loading single dict...')
            path = filedialog.askopenfilename(title='Open a dictionary', 
                                          parent=self.root.win,
                                          filetypes=[('Dictionary file (*.mdx)', '*.mdx')])
            if path == '':
                self.logger.debug('Cancelled')
                self.set_dict_state(0)
                return                
            self.set_dict_state(1)

            tmp = Dict(self.root, path)
            self.dicts.append(tmp)
            self.set_dict_state(0)
            self.logger.info(f'Loaded dict: {str(tmp)}')
        else:
            if not os.path.exists(self.dir):
                self.logger.error(f'Dict Folder not found: {self.dir}')
                with open(self.settings.DATA_PATHS['error_html'], 'r', encoding='utf-8') as f:
                    self.root.set_page(f.read())
                self.set_dict_state(2)
                return
            else:
                paths = os.listdir(self.dir)
                dicts = []
                for i in range(len(paths)):
                    path = paths[i]
                    path = os.path.abspath(os.path.join(self.dir, path))
                    if os.path.isfile(path) and (os.path.splitext(path)[-1].lower() == '.mdx'):
                        dicts.append(path)
                
                self.set_dict_state(1)
                
                for i in range(len(dicts)):
                    tmp = Dict(self.root, dicts[i])
                    self.dicts.append(tmp)
                    # self.headwords += tmp.headwords
                    self.logger.info(f'Loaded dict: {str(tmp)} ({i+1}/{len(dicts)})')
                    self.set_dict_state(1)
            # self.headwords = set(self.headwords)
            self.set_dict_state(0)
            end_time = perf_counter()
            self.root.set_page('', 's')
            self.logger.info(f'All dicts loaded in {end_time-start_time}s')

    def get_similar_words(self, word: str) -> list[str]:
        """Get similar words

        Args:
            word (str): query word

        Returns:
            list[str]: a list of similar words
        """        
        similar_words = {}
        headwords = []
        for d in self.dicts:
            headwords += ([*d.mdx])
        headwords = set(headwords)
        for headword in headwords:
            headword = headword.decode('utf-8')
            sim = distance(word, headword)
            if len(similar_words) < self.settings.SIMILAR_WORD_SHOWN:
                similar_words[headword] = sim
            else:
                similar_words = dict(sorted(similar_words.items(), key=lambda item: item[1]))
                del similar_words[list(similar_words.keys())[-1]]
                similar_words[headword] = sim
        return list(similar_words.keys())

    def search(self, word: str=None):
        
        """search a word

        Args:
            word (str): query word

        Returns:
            str: html of the definition
            list[str]: a list of similar words
        """
        def on_search(word: str=None):
            self.clear_res()
            if self.dict_state == 'loading':
                self.root.disable_exit_on_focus_out = True
                messagebox.showinfo('INFO', 'Please wait until all the dictionaries are loaded')
                self.root.disable_exit_on_focus_out = False
                return
            elif self.dict_state == 'error':
                self.root.disable_exit_on_focus_out = True
                messagebox.showerror('ERROR', 'Failed to load dictionaries:\n'\
                                    f'Path not found: \"{self.root.option.dict_path}\"')
                self.root.disable_exit_on_focus_out = False
                return

            flag = False
            self.root.set_page(f'<h2>Search results for \"{word}\"...</h2>')
            for dict in self.dicts:
                name = dict.name
                self.logger.info(f'Searching \"{word}\" in {name}...')
                tmp = dict.search(word, self)[0]
                if tmp:
                    self.logger.info('Found')
                else:
                    self.logger.info('Not found')
                flag = flag or tmp

            if not flag:
                self.logger.info(f'No definition for \"{word}\"')
                similar_words = self.get_similar_words(word)
                self.root.set_similar_list(word, similar_words)
        
        self.tools.start_thread(on_search, (word,))
    def clear_res(self):
        if os.path.exists(self.settings.DATA_PATHS['dict_res']):
            shutil.rmtree(self.settings.DATA_PATHS['dict_res'])