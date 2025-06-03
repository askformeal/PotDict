import os 
import urllib.parse

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
    
    def search(self, word: str, search) -> bool:
        """Search a word

        Args:
            word (str): query word

        Returns:
            None: not found
            str: definition of the query word (html)
        """
        """ headwords = [*self.mdx]
        items = [*self.mdx.items()]
        word = urllib.parse.unquote(word.strip())
        try:
            index = headwords.index(word.encode('utf-8'))
        except ValueError:
            try:
                index = headwords.index(word.lower().encode('utf-8'))
            except ValueError:
                return None
            
        html = items[index][1]
        html = html.decode('utf-8')
        return html """
        word = urllib.parse.unquote(word.strip())
        word = word.encode('utf-8')
        for k,v in self.mdx.items():
            if word == k or word.lower() == k:
                self.root.load_html(f'''
                                <h3 style="color: red;">{self.name}</h3>
                                <hr color="red" size="3"/>
                                {v.decode('utf-8')}
                                ''',
                                'a')
                return True
        return False

    def __str__(self):
        return self.name