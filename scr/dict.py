class Dict():
    def __init__(self, master, name, headwords, items):
        self.master = master
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