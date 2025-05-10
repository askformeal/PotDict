import os
from datetime import datetime

class Logger():
    def __init__(self, master, path, level='DEBUG', print_log=False, max_bytes=0):
        self.master = master
        self.path = path
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
                self.master.display(f"{msg}")

            if self.print_log:
                print(msg)

            msg = msg.replace('\n', '')

            if nl:
                msg += '\n'
            
            with open(self.path, 'a', encoding='utf-8') as f:
                t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f'[{t}] [{level}] {msg}\n')

    def clear(self):
        with open(self.path, 'w') as f:
            self.master.display('Log cleared')