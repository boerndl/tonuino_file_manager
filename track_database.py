# -*- coding: utf-8 -*-
"""
Created on Mon May 11 20:56:05 2020

@author: Bernd
"""
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation, sessionmaker
from pathlib import Path
from mutagen.id3 import ID3
import re


Base = declarative_base()


class Album(Base):
    __tablename__ = 'albums'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    folder_num = Column(Integer(), nullable=False)
    artist = Column(String(255), nullable=True)
    tracks = relation('Track')

    def __init__(self, title, folder_num, artist=None):
        self.folder_num = folder_num
        self.title = title
        self.artist = artist
        self.tracks = []

    def __repr__(self):
        return f'Album({self.title})'

    @property
    def folder_str(self):
        return f'{self.folder_num:02d}'


class Track(Base):
    __tablename__ = 'tracks'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    album_id = Column(Integer, ForeignKey('albums.id'))
    album_title = Column(String(255), nullable=True)
    artist = Column(String(255), nullable=True)
    
    def __init__(self, file, album_id=None):
        tags = ID3(file)
        if 'TIT2' in tags:
            self.title = tags['TIT2'].text[0]
        else:
            self.title = 'unknown'
        self.album_id = album_id
        if 'TPE1' in tags:
            self.artist = tags['TPE1'].text[0]
        if 'TALB' in tags:
            self.album_title = tags['TALB'].text[0]

    def __repr__(self):
        return f'Track({self.title})'


class TrackDataBase():

    def __init__(self, path):
        self.engine = create_engine('sqlite:///' + path + '/tracks.db')
        self.path = Path(path)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(self.engine)
        self.session = Session()
        self.update()

    def update(self):
        existing_dirs = [
            d .name for d in self.path.iterdir()
            if d.is_dir() and re.fullmatch('[0-9]{2}', d.name)]
        db_dirs = [a.folder_str for a in self.albums]
        for d in existing_dirs:
            if not d in db_dirs:
                print('Adding untracked album to database.')
                album = self.add_album('unknown', int(d))
                if album.tracks:
                    if album.tracks[0].album_title:
                        album.title = album.tracks[0].album_title
                    if album.tracks[0].artist:
                        album.artist = album.tracks[0].artist
                    self.session.commit()
            # ToDo: check tracks if album is in database

    def add_album(self, title, folder=None, artist=None):
        try:
            album = Album(title, folder, artist)
            album_dir = self.path / album.folder_str
            track_files = list(album_dir.glob('*.mp3'))
            for file in track_files:
                track = Track(file, album.id)
                album.tracks.append(track)
                self.session.add(track)
            self.session.add(album)
            self.session.commit()
            return album
        except Exception as e:
            print('Exception:', e)
            self.session.rollback()

    @property
    def albums(self):
        return self.session.query(Album).all()

    def close(self):
        self.session.close()
        self.engine.dispose()

    def __del__(self):
        self.close()


if __name__ == '__main__':
    db = TrackDataBase(r'.')
