import os 
from urllib.parse import urlparse, unquote
import re

from readmdict import MDX, MDD

from src.settings import Settings
from src.tools import Tools

class Dict:
    def __init__(self, root, path: str):
        self.root = root
        self.name = os.path.basename(path)[:-4]

        self.settings = Settings()

        self.mdx = MDX(path, encoding='utf-8')
        self.tools = Tools(self.root, self.root.logger)
        mdd_path = path[:-4]+'.mdd'
        self.has_mdd = False
        if os.path.exists(mdd_path):
            self.has_mdd = True
            self.mdd = MDD(mdd_path)
        self.tools = Tools(self.root, self.root.logger)

    def search(self, query_word: str, search) -> bool:
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
            src_links = list(set(src_links))
            href_links = list(set(href_links))
            links = src_links + href_links
            for i in range(len(links)):
                links[i] = re.findall(r'[^(src=|href=)].+$', links[i])[0][1:-1]
                tmp = urlparse(links[i])
                tmp = tmp.netloc + tmp.path
                path = os.path.join(self.settings.DATA_PATHS['dict_res'],tmp)
                path = os.path.relpath(path)
                path = path.replace('\\', '/')
                links[i] = data = data.replace(links[i], path)
                links[i] = tmp
            return (data, links)
        
        query_word = unquote(query_word.strip())
        query_word = query_word.encode('utf-8')
        for word, html in self.mdx.items():
            if query_word == word or query_word.lower() == word:
                html, links = get_links(html.decode('utf-8'))
                for link in links:
                    self.get_res(link)
                self.root.set_page(f'<h3 style="color: red;">{self.name}</h3>'\
                                    '<hr color="red" size="3"/>'\
                                    f'{html}',
                                    'a')

                return True
        return False

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