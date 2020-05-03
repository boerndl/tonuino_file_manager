# -*- coding: utf-8 -*-
"""
Created on Sun Dec  8 20:14:17 2019

@author: Bernd
"""

import re
from tkinter import *
from tkinter.ttk import Progressbar
from tkinter.filedialog import askdirectory
from pathlib import Path

class Window(Frame):
    
    def __init__(self, master):
        Frame.__init__(self, master)                 
        self.master = master
        self.init_window()
        self.src_dir = None
        self.src_files = []
        self.dest_dir = None

    def init_window(self):     
        self.master.title("TonUino File Transfer")
        self.grid(row=0, column=0, sticky='nsew')
        for col in range(2):
            self.columnconfigure(col, weight=1)
        self.rowconfigure(0, weight=10)
        self.rowconfigure(1, weight=1)
        
        # source directory control
        src_frame = LabelFrame(self, text='source')
        src_frame.grid(row=0, column=0, padx=5, pady=5, sticky='nswe')
        src_frame.columnconfigure(0, weight=10)
        src_frame.columnconfigure(1, weight=1)
        self.src_dir_entry = Entry(src_frame, bg='#333', fg='#fff')
        self.src_dir_entry.grid(row=0, column=0, padx=10, pady=10, sticky='nwe')
        Button(src_frame, text="...", command=self.load_src_dir,
               width=3).grid(row=0, column=1, padx=0, pady=10, sticky='nw')
        self.src_file_list = Listbox(src_frame)
        self.src_file_list.grid(row=1, column=0, columnspan=2,
                                padx=10, pady=10, sticky='nswe')
        
        # destination directory control
        dest_frame = LabelFrame(self, text='destination')
        dest_frame.grid(row=0, column=1, padx=5, pady=5, sticky='nswe')
        self.dest_dir_label = Label(dest_frame, bg='#333', fg='#fff')
        self.dest_dir_label.grid(row=0, column=0, padx=10, pady=10, sticky='nwe')
        Button(dest_frame, text="...", command=self.load_dest_dir,
               width=3).grid(row=0, column=1, padx=0, pady=10, sticky='nw')
        
        cp_btn = Button(self, text='Copy Files', command=self.copy_files)
        cp_btn.grid(row=1, column=0, padx=10, pady=10, ipadx=40)
        self.progress_bar = Progressbar(self, orient=HORIZONTAL, 
                                        length=100, mode='determinate')
        self.progress_bar.grid(row=1, column=1,
                               padx=10, pady=10, ipadx=40)

    def load_src_dir(self):
        '''
        Puts all MP3 files from the specified source directroy into the list
        of source files.
        '''
        self.src_dir = askdirectory()
        self.src_dir_entry.delete(0, END)
        self.src_dir_entry.insert(0, self.src_dir)
        self.src_files = list(Path(self.src_dir).glob('*.mp3'))
        self.src_file_list.delete(0, END)
        for idx, file in enumerate(self.src_files):
            self.src_file_list.insert(idx, file.stem)

    def load_dest_dir(self):
        '''
        Trys to open the TonUino storage.
        '''
        self.dest_dir = askdirectory()
        self.dest_dir_label.config(text=self.dest_dir)
    
    def copy_files(self):
        '''
        Copies all files from the source file list to the destination directory
        in a new sub folder.
        '''
        dest_path = Path(self.dest_dir)
        existing_dirs = [d.name for d in dest_path.iterdir() if d.is_dir()]
        print('exisitng directories: ', existing_dirs)
        dir_nums = [int(d) for d in existing_dirs
                    if re.fullmatch('[0-9]{2}', d)]
        new_dir = dest_path / '{:02d}'.format(max(dir_nums, default=0) + 1)
        print('creating new directory: ', new_dir)
        new_dir.mkdir()
        for num, file in enumerate(self.src_files):
            self.progress_bar['value'] = 0
            self.update_idletasks()
            new_name = f'{num + 1:03}.mp3'
            print(f'copying {file} to {new_name}...')
            dest = new_dir / new_name
            dest.write_bytes(file.read_bytes())
            self.progress_bar['value'] = (num + 1) / len(self.src_files) * 100
            self.update_idletasks()


root = Tk()
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)
root.geometry('600x400')
app = Window(root)
root.mainloop()