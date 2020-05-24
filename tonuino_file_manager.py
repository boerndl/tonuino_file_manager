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
from mutagen.id3 import ID3
from track_database import TrackDataBase


class Window(Frame):
    
    def __init__(self, master):
        Frame.__init__(self, master)                 
        self.master = master
        self.init_window()
        self.src_dir = None
        self.src_files = []
        self.dest_dir = None
        self.db = None

    def init_window(self):     
        self.master.title("TonUino File Manager")
        self.grid(row=0, column=0, sticky='nsew')
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=10)
        self.rowconfigure(1, weight=1)
        
        # source directory control
        src_frame = LabelFrame(self, text='Source')
        src_frame.grid(row=0, column=0, padx=5, pady=5, sticky='nswe')
        src_frame.columnconfigure(0, weight=10)
        src_frame.columnconfigure(1, weight=1)
        src_frame.rowconfigure(0, weight=1)
        src_frame.rowconfigure(1, weight=20)
        self.src_dir_entry = Entry(src_frame, bg='#333', fg='#fff')
        self.src_dir_entry.grid(row=0, column=0, padx=10, pady=10, sticky='nwe')
        Button(src_frame, text="...", command=self.load_src_dir,
               width=3).grid(row=0, column=1, padx=0, pady=10, sticky='nw')
        self.src_file_list = Listbox(src_frame)
        self.src_file_list.grid(row=1, column=0, columnspan=2,
                                padx=10, pady=10, sticky='nswe')
        
        # destination directory control
        dest_frame = LabelFrame(self, text='TonUino SD Card')
        dest_frame.grid(row=0, column=1, padx=5, pady=5, sticky='nswe')
        dest_frame.columnconfigure(0, weight=10)
        dest_frame.columnconfigure(1, weight=1)
        dest_frame.columnconfigure(2, weight=11)
        dest_frame.rowconfigure(0, weight=1)
        dest_frame.rowconfigure(1, weight=20)
        self.dest_dir_label = Label(dest_frame, bg='#333', fg='#fff')
        self.dest_dir_label.grid(row=0, column=0, padx=10, pady=10, sticky='nwe')
        Button(dest_frame, text="...", command=self.load_dest_dir,
               width=3).grid(row=0, column=1, padx=0, pady=10, sticky='nw')
        self.album_list = Listbox(dest_frame)
        self.album_list.grid(row=1, column=0, columnspan=2,
                             padx=10, pady=10, sticky='nswe')
        self.album_list.bind('<<ListboxSelect>>',
                             lambda _: self.update_track_list())
        self.track_list = Listbox(dest_frame)
        self.track_list.grid(row=1, column=2,
                             padx=10, pady=10, sticky='nswe')

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
        self.src_dir = Path(askdirectory())
        self.src_dir_entry.delete(0, END)
        self.src_dir_entry.insert(0, str(self.src_dir))
        self.src_files = list(self.src_dir.glob('*.mp3'))
        self.src_file_list.delete(0, END)
        for idx, file in enumerate(self.src_files):
            self.src_file_list.insert(idx, file.stem)

    def load_dest_dir(self):
        '''
        Trys to open the TonUino storage.
        '''
        self.dest_dir = Path(askdirectory())
        self.dest_dir_label.config(text=str(self.dest_dir))
        self.db = TrackDataBase(str(self.dest_dir))
        self.update_album_list()

    def update_album_list(self):
        '''
        Show all albums on the TonUino storage.
        '''
        self.album_list.delete(0, END)
        for idx, album in enumerate(self.db.albums):
            print('album: ', album, 'type', type(album))
            self.album_list.insert(idx, f'{idx + 1:02d} - ' + album.title)
        self.update_track_list()

    @property
    def album(self):
        selected = self.album_list.curselection()
        if selected and self.db.albums:
            return self.db.albums[selected[0]]
        else:
            return None

    def update_track_list(self):
        '''
        Show all tracks in album.
        '''
        self.track_list.delete(0, END)
        if self.album:
            for idx, track in enumerate(self.album.tracks):
                self.track_list.insert(idx, f'{idx + 1:03d} - ' + track.title)

    def copy_files(self, new_num=None):
        '''
        Copies all files from the source file list to the destination directory
        in a new sub folder.
        '''
        if new_num is None:
            existing_dirs = [d.name for d in self.dest_dir.iterdir() if d.is_dir()]
            print('exisitng directories: ', existing_dirs)
            dir_nums = [int(d) for d in existing_dirs
                        if re.fullmatch('[0-9]{2}', d)]
            new_num = max(dir_nums, default=0) + 1
        new_dir = self.dest_dir / '{:02d}'.format(new_num)
        if not new_dir.exists():
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
        self.db.add_album(
            self.src_dir.parts[-1], new_num)
        self.update_album_list()


if __name__ == '__main__':
    root = Tk()
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    root.geometry('800x600')
    app = Window(root)
    
    def on_closing():
        if app.db:
            app.db.close()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
