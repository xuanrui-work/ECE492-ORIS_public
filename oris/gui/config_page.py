from web_server import start_http_server, close_http_server
from record import RECORD_SAVE_PATH
from . import font

import tkinter as tk
import os

class ConfigPage(tk.Frame):
    def __init__(self, parent: tk.Frame, controller: tk.Frame):
        """
        Initializes the ConfigPage object, which is a tkinter frame for providing the configuration UI.
        """
        super().__init__(parent)
        self.parent = parent; self.controller = controller

        self.share_record_l = tk.Label(
            self, font=font.NORMAL_LABEL_FONT,
            anchor='nw',
            text='Record sharing via HTTP server is currently OFF.'
        )
        self.share_record_l.grid(row=0, column=0, sticky='nsew')

        self.share_record_btn = tk.Button(
            self, font=font.NORMAL_BUTTON_FONT,
            text='Toggle ON/OFF',
            command=self.share_record_btn_callback
        )
        self.share_record_btn.grid(row=0, column=1, sticky='nsew')

        self.clear_record_l = tk.Label(
            self, font=font.NORMAL_LABEL_FONT,
            anchor='nw',
            text='Clear all saved scan record on this device.'
        )
        self.clear_record_l.grid(row=1, column=0, sticky='nsew')

        self.clear_record_btn = tk.Button(
            self, font=font.NORMAL_BUTTON_FONT,
            text='Clear Scan Record',
            command=self.clear_record_btn_callback
        )
        self.clear_record_btn.grid(row=1, column=1, sticky='nsew')

        self.back_btn = tk.Button(
            self, font=font.NORMAL_BUTTON_FONT,
            text='Back',
            command=self.controller.raise_main_page
        )
        self.back_btn.grid(row=3, column=0, columnspan=2, sticky='nsew')

        self.rowconfigure([0, 1, 2, 3], weight=1)
        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=1)

        # member variables of this frame
        self.http_server_running = False

    def share_record_btn_callback(self):
        if not self.http_server_running:
            start_http_server()
            self.http_server_running = True
            self.share_record_l.config(text='Record sharing via HTTP server is currently ON.')
        else:
            close_http_server()
            self.http_server_running = False
            self.share_record_l.config(text='Record sharing via HTTP server is currently OFF.')

    def clear_record_btn_callback(self):
        os.makedirs(RECORD_SAVE_PATH, exist_ok=True)

        for file in os.scandir(RECORD_SAVE_PATH):
            if file.is_file():
                os.remove(file.path)
                self.clear_record_l.config(text=f'Deleted: "{file.name}"')
                self.update_idletasks()

        self.clear_record_l.config(text='All scan records have been deleted.')
        self.clear_record_l.after(
            5000,
            lambda: self.clear_record_l.config(text='Clear all saved scan record on this device.')
        )
