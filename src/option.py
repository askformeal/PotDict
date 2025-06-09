import tkinter as tk
from tkinter import filedialog
import logging
import json

from src import main
from src.settings import Settings
from src.logger import Logger

class Option:
    def __init__(self, root):
        self.root: main.PotDict = root
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
                    self.root.exit(code=1, note='invalid option file formate')
        except FileNotFoundError:
            self.logger.info('Option file not found, restore to default')
            with open(self.settings.DATA_PATHS['default_options'], 'r', encoding='utf-8') as f:
                self.options = json.load(f)
            with open(self.settings.PATHS['options'], 'w', encoding='utf-8') as f:
                json.dump(self.options, f, indent=4)
        
        try:
            self.dict_paths = self.options['dict_paths']
            self.log_level = getattr(logging, self.options['log_level'], logging.NOTSET)
            self.eolf = self.options['exit_on_focus_out']
            self.lang = self.options['lang']
        except KeyError as e:
            self.logger.critical(f'Invalid option file: {e}')
            self.root.exit(code=1, note='invalid option file formate')


    def set_options(self):
        def apply_options():
            self.options['dict_paths'] = []
            for i in range(dict_paths.size()):
                self.options['dict_paths'].append(dict_paths.get(i))
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
            add_dicts(self.options['dict_paths'])
            log_level.set(options['log_level'])
            exit_on_focus_out.set({True: 'Yes', False:'No'}[options['exit_on_focus_out']])

        def reset():
            self.logger.info('Reset options')
            with open(self.settings.DATA_PATHS['default_options'], 'r') as f:
                default_options = json.load(f)
            load(default_options)

        def update_dict_lb_width():
            max_len = 0
            for i in range(dict_paths.size()):
                l = len(dict_paths.get(i))
                if l > max_len:
                    max_len = l
            dict_paths.config(width=max_len)

        def move_dict_up():
            selection = dict_paths.curselection()
            if len(selection) > 0:
                index = selection[0]
                if index > 0:
                    item = dict_paths.get(index)
                    dict_paths.delete(index)
                    dict_paths.insert(index-1, item)
                    dict_paths.select_set(index-1)
        
        def move_dict_down():
            selection = dict_paths.curselection()
            if len(selection) > 0:
                index = selection[0]
                if index < dict_paths.size() - 1:
                    item = dict_paths.get(index)
                    dict_paths.delete(index)
                    dict_paths.insert(index+1, item)
                    dict_paths.select_set(index+1)

        def del_dict():
            selection = dict_paths.curselection()
            if len(selection) > 0:
                index = selection[0]
                dict_paths.delete(index)
                update_dict_lb_width()

        def add_dicts(path=None):
            if path == None:
                tmp = lambda: filedialog.askopenfilenames(parent=self.options_win, 
                                                          title='Open dictionaries',
                                                          filetypes=[('Dictionary file (.mdx)', '.mdx')]
                                                          )
                path = self.root.win.pause_eolf(tmp)
            dicts = []
            for i in range(dict_paths.size()):
                dicts.append(dict_paths.get(i))

            for file in path:
                if not file in dicts:
                    self.logger.info(f'Add dict: {file}')
                    dict_paths.insert('end', file)
            update_dict_lb_width()

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
            
            lbl = tk.Label(fr, text='Dictionary Paths')
            lbl.pack(fill='both', expand=True, padx=(0,5))

            # scroll_x = tk.Scrollbar(fr, orient='horizontal')
            # scroll_x.pack(fill='both')
            
            scroll_y = tk.Scrollbar(fr)
            scroll_y.pack(side='left', fill='both')
            
            dict_paths = tk.Listbox(fr, yscrollcommand= scroll_y.set)
            dict_paths.pack(side='top', fill='both', expand=True, padx=5,pady=5)

            # scroll_x.config(command=dict_paths.xview)
            scroll_y.config(command=dict_paths.yview)

            fr = tk.Frame(self.options_win)
            fr.pack(fill='x', expand=True, padx=5,pady=5)
            
            btn_fr = tk.Frame(fr)
            btn_fr.pack(fill='x', expand=True, padx=5,pady=5)

            btn = tk.Button(btn_fr, text='Delete', command=del_dict)
            btn.pack(side='right', padx=(5,0))

            btn = tk.Button(btn_fr, text='Add', command=add_dicts)
            btn.pack(side='right', padx=(5,0))

            btn = tk.Button(btn_fr, text='Down', command=move_dict_down)
            btn.pack(side='right', padx=(5,0))

            btn = tk.Button(btn_fr, text='Up', command=move_dict_up)
            btn.pack(side='right', padx=(5,0))

            fr = tk.Frame(self.options_win)
            fr.pack(fill='x', padx=5,pady=5)
            
            lbl = tk.Label(fr, text='Log Level')
            lbl.pack(side='left', fill='both', expand=True, padx=(0,5))

            log_level = tk.StringVar()
            log_level_menu = tk.OptionMenu(fr,log_level, 
                                        'NOTSET', 'DEBUG',
                                        'INFO', 'WARNING',
                                        'ERROR', 'CRITICAL')
            log_level_menu.pack(side='left')

            fr = tk.Frame(self.options_win)
            fr.pack(fill='x', padx=5,pady=5)
            
            lbl = tk.Label(fr, text='Exit on lost focus')
            lbl.pack(side='left', fill='both', expand=True, padx=(0,5))

            exit_on_focus_out = tk.StringVar()
            exit_on_focus_out_menu = tk.OptionMenu(fr, exit_on_focus_out,
                                            'Yes', 'No')
            exit_on_focus_out_menu.pack(side='left', fill='both', expand=True)
            
            fr = tk.Frame(self.options_win)
            fr.pack(fill='x', padx=5,pady=5)

            apply_btn = tk.Button(fr, text='Apply', command=lambda: apply_options())
            apply_btn.pack(side='right', fill='both', padx=(15, 0))

            cancel_btn = tk.Button(fr, text='Cancel', command=lambda: on_close(False))
            cancel_btn.pack(side='right', fill='both', padx=(15, 0))

            ok_btn = tk.Button(fr, text='OK', command=lambda: on_close(True))
            ok_btn.pack(side='right', fill='both', padx=(15, 0))

            reset_btn  = tk.Button(fr, text='Reset', command=lambda: reset())
            reset_btn.pack(side='left', fill='both')


            load(self.options)

            self.options_win.mainloop()
        else:
            self.options_win.focus_set()