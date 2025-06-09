from tkinter import filedialog
from tkinter import messagebox
from time import perf_counter
from urllib.parse import unquote, urlparse
import shutil
import json
import re
import os

from Levenshtein import distance
from readmdict import MDX, MDD
import requests

from src import main
from src.settings import Settings
from src.logger import Logger
from src.tools import Tools

class Dict:
    def __init__(self, root, path: str):
        self.root: main.PotDict = root
        self.name = os.path.basename(path)
        self.name = os.path.splitext(self.name)[0]

        self.settings = Settings()
        self.mdx = MDX(path, encoding='utf-8')
        self.tools = Tools(self.root, self.root.logger)
        mdd_path = os.path.splitext(path)[0] + '.mdd'
        if os.path.exists(mdd_path):
            self.has_mdd = True
            self.mdd = MDD(mdd_path)
        else:
            self.has_mdd = False
        self.tools = Tools(self.root, self.root.logger)

    def search(self, query_word: str, search, set_page=True) -> tuple[True, str] | tuple[False, None]:
        """Search a word

        Args:
            word (str): query word

        Returns:
            None: not found
            str: definition of the query word (html)
        """
        def get_links(data: str) -> tuple[str, list[str]]:
            src_links = re.findall('src=\".+?\"', data)
            href_links = re.findall('href=\"[^entry://].+?\"', data)
            links = src_links + href_links
            links = list(set(links))
            for i in range(len(links)):
                links[i] = re.findall(r'[^(src=|href=)].+$', links[i])[0][1:-1]
                tmp = urlparse(links[i])
                tmp = tmp.netloc + tmp.path
                path = os.path.join(self.settings.DATA_PATHS['dict_res'],tmp)
                path = os.path.relpath(path)
                path = path.replace('\\', '/')
                data = data.replace(links[i], path)
                links[i] = tmp
            return (data, links)
        
        query_word = query_word.encode('utf-8')
        for word, html in self.mdx.items():
            if query_word == word or query_word.lower() == word:
                html = html.decode('utf-8')
                html, links = get_links(html)
                for link in links:
                    self.get_res(link)
                if html.startswith('@@@LINK='):
                    html = f'<h3>Main entry: {html[8:]}</h3>'
                with open(self.settings.DATA_PATHS['dict_html'], 'r', encoding='utf-8') as f:
                    template = f.read()
                template = template.replace('%N', self.name)
                template = template.replace('%D', html)
                if set_page:
                    self.root.win.set_page(template, 'a')

                return (True, template)
        return (False, None)

    def get_res(self, query_name: str) -> str|None:
        if self.has_mdd:
            for name, data in self.mdd.items():
                if name.decode('utf-8') == f'\\{query_name}':
                    path = os.path.join(self.settings.DATA_PATHS['dict_res'], query_name)
                    self.tools.create_file(path)
                    with open(path, 'wb') as f:
                        f.write(data)
                    return path
            
    def __str__(self):
        return self.name
class Search:
    def __init__(self, root):
        self.root = root
        self.paths = self.root.option.dict_paths
        self.settings = Settings()
        self.logger = Logger(__name__, self.root)
        self.dicts: list[Dict] = []
        self.headwords = []
        self.searching = False
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
            self.root.win.set_page(f.read(), 's')
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
            ok_cnt = 0
            error_cnt = 0
            for i in range(len(self.paths)):
                path = self.paths[i]
                if not os.path.exists(path):
                    error_cnt += 1
                    self.logger.error(f'Dict not found: {path}')
                    continue
                else:
                    if os.path.isfile(path):
                        try:
                            tmp = Dict(self.root, path)
                        except Exception:
                            error_cnt += 1
                            self.logger.error(f'Invalid dict file: {path}')
                            continue
                        else:
                            self.dicts.append(tmp)
                            ok_cnt += 1
                            self.logger.info(f'Loaded dict: {str(tmp)} ({i+1}/{len(self.paths)})')
                    else:
                        error_cnt += 1
                        self.logger.error(f'Not a file: {path}')
                        continue

            self.set_dict_state(0)
            end_time = perf_counter()
            self.root.win.set_page('', 's')
            self.logger.info(f'Loaded {ok_cnt} dicts in {end_time-start_time}s, '\
                             f'{error_cnt} errors, total {len(self.paths)}')

    def on_search(self, word: str=None, set_page=True) -> str:
            self.clear_res()
            if self.dict_state == 'loading':
                tmp = lambda: messagebox.showinfo('INFO', 
                                                  'Please wait until all the '\
                                                  'dictionaries are loaded')
                self.root.win.pause_eolf(tmp)
                return
            elif self.dict_state == 'error':
                tmp = lambda: messagebox.showerror('ERROR', 
                                                   'Failed to load dictionaries:\n'\
                                                   'Path not found: '\
                                                   f'\"{self.root.option.dict_path}\"')
                self.root.win.pause_eolf(tmp)
                return
            elif self.searching:
                tmp = lambda: messagebox.showerror('ERROR', 
                                                   'Searching, please waite')
                self.root.win.pause_eolf(tmp)   
                return
            
            word = unquote(word).strip()
            self.searching = True
            flag = False
            cnt = 0
            result = ''
            self.root.win.set_page(f'<h2>Search results for \"{word}\"...</h2>')
            for dict in self.dicts:
                name = dict.name
                self.logger.info(f'Searching \"{word}\" in {name}...')
                is_found, tmp = dict.search(word, self, set_page)
                if is_found:
                    result += tmp
                    self.logger.info('Found')
                    cnt += 1
                else:
                    self.logger.info('Not found')
                flag = flag or is_found
            self.logger.info(f'Search done, {cnt} definition(s) found in '\
                             f'{len(self.dicts)} dicts')
            
            if not flag:
                self.logger.info(f'No definition for \"{word}\"')
                similar_words = self.get_similar_words(word)
                self.logger.debug(f'Similar words of {word}: {similar_words}')
                self.root.win.set_page('')
                with open(self.settings.DATA_PATHS['not_found_html'], 'r', encoding='utf-8') as f:
                    result = f.read()

                result = result.replace('%Q', word)
                sim_list = ''
                for i in range(len(similar_words)):
                    sim_word = similar_words[i]
                    sim_list += '<font size=\"4\">'\
                                f'<a id=\"{i}\" href=\"entry://{sim_word}\">{sim_word}</a>'\
                                '</font><br>\n'
                result = result.replace('%S', sim_list)
                if set_page:
                    self.root.win.set_page(result)
            self.searching = False
            return result

    def search(self, word: str=None, set_page=True):
        
        """search a word

        Args:
            word (str): query word

        Returns:
            str: html of the definition
            list[str]: a list of similar words
        """
        self.tools.start_thread(self.on_search, (word,set_page,))

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

    def translate(text, target_lang):
        if target_lang == '':
            return "[Target language not defined]"
        response = requests.get(f'https://translate.appworlds.cn?text={text}&from=auto&to={target_lang}')
        response.encoding = 'utf-8'
        if response.status_code != 200:
            return f'[Connection failed: code {response.status_code}]'
        else:
            result = json.loads(response.text)
            if result['code'] != 200:
                return f'[{result['msg']}]'
            else:
                return result['data']

    def clear_res(self):
        if os.path.exists(self.settings.DATA_PATHS['dict_res']):
            shutil.rmtree(self.settings.DATA_PATHS['dict_res'])