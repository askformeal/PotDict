from threading import Thread
from typing import Callable
import os

from src.settings import Settings
from src.logger import Logger

class Tools:
    def __init__(self, root, logger: Logger|None=None):
        self.root = root
        self.settings = Settings()
        if logger:
            self.logger = logger
        else:
             self.logger = Logger('tools', root)

    def start_thread(self, target: Callable, args=(), join=False) -> Thread:
            """Start a thread (daemon mode)

            Args:
                target (Callable): target function
                args (tuple, optional): parameter. Defaults to ().
                join (bool, optional): wait for the thread to complete. Defaults to False.

            Returns:
                Thread: started thread
            """
            t = Thread(target=target, args=args, daemon=True)
            self.logger.debug(f'Start Thread: <{target.__qualname__}>')
            t.start()
            if join:
                t.join()
                self.logger.debug(f'Thread joined: <{target.__qualname__}>')
            return t
    
    def create_file(self, path):
        folder = os.path.dirname(path)
        if not os.path.exists(folder):
              os.makedirs(folder)
        with open(path, 'w') as f:
             ...
        self.logger.debug(f'Create file {path}')