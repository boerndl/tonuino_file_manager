# -*- coding: utf-8 -*-
"""
Created on Mon May 11 20:56:05 2020

@author: Bernd
"""
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation, sessionmaker


Base = declarative_base()


class Album(Base):
    __tablename__ = 'albums'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    folder = Column(Integer(), nullable=False)
    artist = Column(String(255), nullable=True)
    
    def __init__(self, title, folder):
        self.title = title
        self.folder = folder

    def __repr__(self):
        return f'Album({self.title})'


class TrackDataBase():
    
    def __init__(self, path):
        self.engine = create_engine('sqlite:///' + path + 'tracks.db')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(self.engine)
        self.session = Session()

    def add_album(self, title, folder):
        try:
            self.session.add(Album(title, folder))
            self.session.commit()
        except:
            self.session.rollback()

    def get_albums(self):
        return self.session.query(Album).all()

    def close(self):
        self.session.close()
        self.engine.dispose()

    def __del__(self):
        self.close()


if __name__ == '__main__':
    db = TrackDataBase('')
    db.add_album('Dubidu', 1)
    for album in db.get_albums():
        print(album)
    db.close()