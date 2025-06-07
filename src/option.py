import tkinter as tk
from tkinter import filedialog
import logging
import json
import sys
import os

from src.settings import Settings
from src.logger import Logger

class Option:
    def __init__(self, root):
        self.root = root
        self.settings = Settings()
        self.logger = Logger(__name__, self.root)
        self.options_win_open = False

    def load(self):
        """Load from options file
        """        
        try:
            with open(self.settings.PATHS['options'], 'r', encoding='utf-8') as f:
                try:
                    self.options = json.load(f)
                except json.decoder.JSONDecodeError as e:
                    self.logger.critical(f'Failed to load option file: {e}\n\tTry to delete options.json')
                    self.root.exit(code=1)
        except FileNotFoundError:
            self.logger.warning('Option file not found, restore to default')
            with open(self.settings.DATA_PATHS['default_options'], 'r', encoding='utf-8') as f:
                self.options = json.load(f)
            with open(self.settings.PATHS['options'], 'w', encoding='utf-8') as f:
                json.dump(self.options, f, indent=4)
        
        self.dict_path = self.options['dict_path']
        self.log_level = getattr(logging, self.options['log_level'], logging.NOTSET)
        self.exit_on_focus_out = self.options['exit_on_focus_out']


    def set_options(self):
        def apply_options():
            self.options['dict_path'] = dict_path_entry.get()
            self.options['log_level'] = log_level.get()
            self.options['exit_on_focus_out'] = {'Yes':True, 'No':False}[exit_on_focus_out.get()]

            with open(self.settings.PATHS['options'], 'w') as f:
                json.dump(self.options, f, indent=4)

            self.logger.info(f'New options saved: {self.options}')

        def on_close(apply=False):
            if apply:
                apply_options()
            self.options_win_open = False
            self.options_win.destroy()

        def load(options: dict):
            set_dict_sentry(options['dict_path'], True)
            log_level.set(options['log_level'])
            exit_on_focus_out.set({True: 'Yes', False:'No'}[options['exit_on_focus_out']])

        def reset():
            self.logger.info('Reset options')
            with open(self.settings.DATA_PATHS['default_options'], 'r') as f:
                default_options = json.load(f)
            load(default_options)

        def open_dir() -> str:
            self.root.disable_exit_on_focus_out = True
            path = filedialog.askdirectory(parent=self.options_win)
            self.root.disable_exit_on_focus_out = False
            self.logger.debug(f'Open dict dir: {path}')
            if not os.path.exists(path) and path != '':
                os.makedirs(path)
            return path
        
        def set_dict_sentry(path, blank=False):
            if path != '' or blank:
                dict_path_entry.delete(0, 'end')
                dict_path_entry.insert('end', path)
        if not self.options_win_open:
            self.options_win_open = True
            self.options_win = tk.Toplevel(self.root.win)
            self.options_win.attributes("-topmost", True)
            self.options_win.protocol('WM_DELETE_WINDOW', on_close)
            self.options_win.focus_set()

            self.options_win.iconbitmap(self.settings.DATA_PATHS['icon'])
            self.options_win.title('Options')

            fr = tk.Frame(self.options_win)
            fr.pack(fill='x', expand=True, padx=5,pady=5)
            
            lbl = tk.Label(fr, text='Dictionary Path')
            lbl.pack(side='left', fill='both', expand=True, padx=(0,5))
            
            dict_path_entry = tk.Entry(fr)
            dict_path_entry.pack(side='left', fill='both', expand=True)

            dict_path_btn = tk.Button(fr, text='...', command=lambda: set_dict_sentry(open_dir()))
            dict_path_btn.pack(side='left', fill='both', padx=(5,0))

            fr = tk.Frame(self.options_win)
            fr.pack(fill='x', expand=True, padx=5,pady=5)
            
            lbl = tk.Label(fr, text='Log Level')
            lbl.pack(side='left', fill='both', expand=True, padx=(0,5))

            log_level = tk.StringVar()
            log_level_menu = tk.OptionMenu(fr,log_level, 
                                        'NOTSET', 'DEBUG',
                                        'INFO', 'WARNING',
                                        'ERROR', 'CRITICAL')
            log_level_menu.pack(side='left', fill='both', expand=True)

            fr = tk.Frame(self.options_win)
            fr.pack(fill='x', expand=True, padx=5,pady=5)
            
            lbl = tk.Label(fr, text='Exit on lost focus')
            lbl.pack(side='left', fill='both', expand=True, padx=(0,5))

            exit_on_focus_out = tk.StringVar()
            exit_on_focus_out_menu = tk.OptionMenu(fr, exit_on_focus_out,
                                            'Yes', 'No')
            exit_on_focus_out_menu.pack(side='left', fill='both', expand=True)
            
            fr = tk.Frame(self.options_win)
            fr.pack(fill='x', expand=True, padx=5,pady=5)

            apply_btn = tk.Button(fr, text='Apply', command=lambda: apply_options())
            apply_btn.pack(side='right', fill='both', padx=(15, 0))

            cancel_btn = tk.Button(fr, text='Cancel', command=lambda: on_close(False))
            cancel_btn.pack(side='right', fill='both', padx=(15, 0))

            ok_btn = tk.Button(fr, text='OK', command=lambda: on_close(True))
            ok_btn.pack(side='right', fill='both')

            reset_btn  = tk.Button(fr, text='Reset', command=lambda: reset())
            reset_btn.pack(side='left', fill='both')


            load(self.options)

            self.options_win.mainloop()
        else:
            self.options_win.focus_set()