# TKINTER IMPORTS
import tkinter as tk
from tkinter import messagebox as mbox

# GET WINDOW IMPORT
import pygetwindow as gw

# REQUESTS IMPORT
import requests

# KEYBOARD & MOUSE INPUT 
import keyboard as kb
import pyautogui as pag

# SCREENSHOT INPUT
import pyscreenshot as scr
import base64
import io

ADDRESS = 'http://rentogether.azurewebsites.net/'

import platform
WINDOWS = platform.system() == 'Windows'

class MainApplication(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.protocol('WM_DELETE_WINDOW', self.close_callback)
        self._row = 0
        self.grid()
        self.construct()

    def construct(self):
        # Help and Config Buttons
        tk.Button(self, text='Help', command=self.help_window).grid(row=self.row(), column=1)
        tk.Button(self, text='Config', command=self.config_window).grid(row=self.row(1), column=2)

        # Variables Needed to get Window
        self.window = tk.StringVar(self, '--Choose a Window--')
        self.geometry = tk.StringVar(self, '')
        tk.Label(self, text='Window:').grid(row=self.row(), column=1)
        tk.OptionMenu(self, self.window, *gw.getAllTitles()).grid(row=self.row(1), column=2)

        # Username and Game Name to Create Server
        self.username = tk.StringVar(self, '')
        self.game_name = tk.StringVar(self, '')
        self.game_code = tk.StringVar(self, '')
        tk.Label(self, text='Username:').grid(row=self.row(), column=1)
        tk.Entry(self, textvariable=self.username).grid(row=self.row(1), column=2)
        tk.Label(self, text='Game Name:').grid(row=self.row(), column=1)
        tk.Entry(self, textvariable=self.game_name).grid(row=self.row(1), column=2)

        # Create the `Create` button
        self.game_status = tk.StringVar(self, 'Create Game')
        self.create_btn = tk.Button(self, textvariable=self.game_status, command=self.create_game)
        self.create_btn.grid(row=self.row(), column=1, columnspan=2)


        # CONFIG VARIABLES
        self.event_hotkey = tk.StringVar(self, 'f6')
        self.click_hotkey = tk.StringVar(self, 'f4')
        self.quit_hotkey = tk.StringVar(self, 'f2')
        self.submit_hotkey = tk.StringVar(self, 'f5')
        self.timeout = tk.IntVar(self, 15)
        
    def close_callback(self):
        self.quit_callback()
        self.master.quit()
    
    def quit_callback(self):
        if not self.game_code.get() or self.game_code.get() == 'None':
            # Don't need to end game
            return

        # Stop Reading Input
        kb.remove_hotkey(self.event_thread)
        kb.remove_hotkey(self.quit_thread)

        # Configure Button
        self.game_status.set('Create Game')
        self.create_btn.configure(command=self.create_game)

        # Request to end it all
        resp = requests.post(ADDRESS + 'end/' + self.game_code.get())
        if resp.status_code != 200:
            mbox.showerror('Error', 'Something went wrong')
        self.game_code.set('None')


    def event_callback(self):
        if self.window.get() not in gw.getAllTitles():
            mbox.showerror('Error', 'Window title has changed! Unable to track it.')
            return
        if not WINDOWS:
            self.geometry.set(self.to_tk_geo(gw.getWindowGeometry(self.window.get())))
        if WINDOWS:
            win = gw.getWindowsWithTitle(self.window.get())[0]
            w, h, x, y = win.width, win.height, win.left, win.top
            self.geometry.set(self.to_tk_geo(x, y, w, h))

        # Get Screenshot
        (w, h), x1, y1 = map(lambda s: map(int, s.split('x')) if 'x' in s else int(s), self.geometry.get().split('+'))
        image = scr.grab((x1, y1, x1+w, y1+h))
        byte_dump = io.BytesIO()
        image.save(byte_dump, format="PNG")
        byte_dump = byte_dump.getvalue()
        image = base64.standard_b64encode(byte_dump).decode('utf-8')
        

        self.block = tk.Toplevel(self)
        self.block.geometry(self.geometry.get())
        self.block.overrideredirect(1)
        self.block.attributes('-alpha', .0)

        coordinates = []
        # Add coordinates on click
        self.block_canvas = tk.Canvas(self.block, width=w, height=h)

        def click_callback():
            nonlocal coordinates
            pos = pag.position()
            x, y = pos.x - x1, pos.y - y1
            coordinates.append({'x': x, 'y': y})
            print(x, y)

        def submit():
            resp = requests.post(ADDRESS + 'event/' + self.game_code.get(), json={'choices': coordinates, 'image': image, 'timeout': self.timeout.get()})
            kb.remove_hotkey(self.submit_thread)
            kb.remove_hotkey(self.click_thread)
            if resp.status_code != 200:
                mbox.showerror('Error', 'Server could not be reached')
                return
            
            # Load top level with information

        self.block_canvas.grid()
        self.submit_thread = kb.add_hotkey(self.submit_hotkey.get(), submit)
        self.click_thread = kb.add_hotkey(self.click_hotkey.get(), click_callback)
        


    def create_game(self):
        if self.window.get() == '--Choose a Window--':
            # A window is needed
            mbox.showerror('Error', 'You have to choose a window!')
            return
        if not self.game_name.get() or not self.username.get():
            mbox.showerror('Error', 'Make sure you have inserted a game and user name!')
            return
        resp = requests.post(ADDRESS + 'create', json={'host': self.username.get(), 'name': self.game_name.get()})
        if resp.status_code != 200:
            mbox.showerror('Error', 'Could not connect to webserver')
            return
        self.game_code.set(str(resp.text)) # Set gamecode
        tk.Label(self, text='Game Code:').grid(row=self.row(), column=1)
        tk.Label(self, textvariable=self.game_code).grid(row=self.row(1), column=2)
        self.game_status.set('Close the Game')
        self.create_btn.configure(command=self.quit_callback)

        # Start CALLBACK THREAD HERE
        self.event_thread = kb.add_hotkey(self.event_hotkey.get(), self.event_callback)
        self.quit_thread = kb.add_hotkey(self.quit_hotkey.get(), self.quit_callback)

    def to_tk_geo(self, geo) -> str:
        geo = list(map(int, geo))
        return f'{geo[2]}x{geo[3]}+{geo[0]}+{geo[1]}'
        
    def row(self, _p=0):
        if not _p:
            self._row += 1
        return self._row

    def config_window(self):
        self.config_popup = tk.Toplevel(self)

    def help_window(self):
        self.help_popup = tk.Toplevel(self)        
        help = self.help_popup

        # Row Utility
        _row = 0
        def row(_p=0):
            nonlocal _row
            if not _p:
                _row += 1
            return _row

        # Add Content Below as needed