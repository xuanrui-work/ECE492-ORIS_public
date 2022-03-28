from web_server import close_http_server

from .main_page import MainPage
from .dresult_page import DResultPage
from .config_page import ConfigPage

import tkinter as tk

class TkRoot(tk.Tk):
    def __init__(self, *args, **kwargs):
        """
        Initializes the TkRoot object, which is a tkinter Tk for containing all the widgets
        in the GUI.
        """
        super().__init__(*args, **kwargs)

        self.title('ECE492 - ORIS')
        self.geometry(f'{self.winfo_screenwidth()}x{self.winfo_screenheight()}')

        self.grid_rowconfigure(index=0, weight=1)
        self.grid_columnconfigure(index=0, weight=1)
        self.update_idletasks()
        
        self.main_page = MainPage(self, self)
        self.main_page.grid(row=0, column=0, sticky='nsew')

        self.dresult_page = DResultPage(self, self)
        self.dresult_page.grid(row=0, column=0, sticky='nsew')

        self.config_page = ConfigPage(self, self)
        self.config_page.grid(row=0, column=0, sticky='nsew')

        self.protocol('WM_DELETE_WINDOW', self.close)

        self.active_frame = None
        self.raise_main_page()

    def raise_main_page(self):
        """
        Raises the main-page to the top to make it active.
        """
        self.active_frame = self.main_page
        self.active_frame.tkraise()

    def raise_dresult_page(self):
        """
        Raises the result-page to the top to make it active.
        """
        if self.active_frame is self.main_page:
            self.main_page.suspend_processing()

        self.active_frame = self.dresult_page
        self.active_frame.tkraise()

    def raise_config_page(self):
        """
        Raises the config-page to the top to make it active.
        """
        if self.active_frame is self.main_page:
            self.main_page.suspend_processing()

        self.active_frame = self.config_page
        self.active_frame.tkraise()

    def close(self):
        """
        Closes this TkRoot object and releases all its resources.
        """
        self.main_page.close()
        close_http_server()
        self.destroy()
