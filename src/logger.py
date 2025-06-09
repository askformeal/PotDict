import logging
import logging.handlers
import re
import os

from src import main
from src.settings import Settings

class Logger(logging.Logger):
    def __init__(self, name: str, root, level: int=0):
        """Init logger

        Args:
            name (str): name of logger
            level (int): level of logging:
                0 -> NOTSET
                10 -> DEBUG
                20 -> INFO
                30 -> WARNING
                40 -> ERROR
                50 -> CRITICAL
        """        
        super().__init__(name, level)
        self.root: main.PotDict = root
        if self.root.option_ready:
            self.setLevel(self.root.option.log_level)
        self.settings = Settings()
        if not os.path.exists(self.settings.PATHS['log_dir']):
            os.makedirs(self.settings.PATHS['log_dir'])
        self.path = os.path.join(self.settings.PATHS['log_dir'], f'{self.name}.log')
        handler = logging.handlers.RotatingFileHandler(self.path,
                                                    maxBytes=self.settings.LOG_MAX_BYTES,
                                                    backupCount=self.settings.LOG_BACKUP_CNT
                                                    )
        formatter = logging.Formatter('[%(asctime)s] - [%(name)s] - [%(levelname)s] - %(message)s')
        handler.setFormatter(formatter)
        self.addHandler(handler)
        
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.addHandler(handler)
        self.debug(f'Logger module \"{self.name}\" initialized')
        
    def clear(self):
        for file in os.listdir(self.settings.PATHS['log_dir']):
            if re.match(f'{os.path.basename(self.path)}(\\.[0-9]+)$', file) != None:
                file = os.path.join(self.settings.PATHS['log_dir'], file)
                try:
                    os.remove(file)
                    self.info(f'Delete log: {file}')
                except PermissionError as e:
                    self.error(f'Failed to delete log: {file}')
        with open(self.path, 'w') as f:
            ...
        self.info(f'Clear log: {self.path}')