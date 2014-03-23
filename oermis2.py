#!/usr/bin/python
import sqlite3
import random
import datetime

class mopidyPlaylist:

    db = 0
    t_threshold = 3600

    def __init__(self, t_threshold):
        self.t_threshold = t_threshold
        #self.initializePlaylist()

    def connect_db(self):
        db = sqlite3.connect("mopidy.db")
        return db
    
    def initializePlaylist(self):
        if self.db == 0:
            self.db = self.connect_db()
        
        c = self.db.cursor()

        c.execute("drop table if exists corePlaylist;")
        c.execute("drop table if exists corePlaylistWeight;")
        c.execute("drop table if exists addPlaylist;")
        #c.execute("drop table if exists playingSet;")
        c.execute("drop table if exists playingHistory;")
        c.execute("drop table if exists queueHistory;")

        c.execute("create table if not exists corePlaylist(songnumber int, user text);")
        c.execute("create table if not exists corePlaylistWeight(weight int);")
        c.execute("create table if not exists addPlaylist(songnumber int, user text);")
        #c.execute("create table if not exists playingSet(songnumber int);")
        c.execute("create table if not exists playingHistory(songnumber int, playdatetime text);")
        c.execute("create table if not exists queueHistory(songnumber int, queuetime text);")

        self.dbResetPlayingSet()

        self.db.commit()
        self.db.close()
        self.db = 0
        print("Playlists reset")
        return

    def createPlayingSet(self):
        if self.db == 0:
            self.db = self.connect_db()

        c = self.db.cursor()
        
        self.dbResetPlayingSet()

        songlist = []
        historylist = []
        totalPlaytime = 0
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        query = c.execute("select * from mopidyDatabaseWeightsSum;").fetchone()
        totalPlaylistCount = query[0]
        totalWeightsSum = query[1]
        weightArray = c.execute("select * from mopidyDatabaseWeights;").fetchall()
        
        while totalPlaytime < self.t_threshold:
            rnd = random.randrange(totalWeightsSum)
            songnumber = 0
            while 1:
                if rnd <= weightArray[songnumber][0]:
                    songplaytime = c.execute("select time from mopidyDatabase where _rowid_=?", (songnumber,)).fetchone()[0]
                    totalPlaytime = totalPlaytime + songplaytime
                    break
                rnd = rnd - weightArray[songnumber][0]
                songnumber = songnumber + 1
                if songnumber > totalPlaylistCount:
                        songnumber = 0
            songlist.append((songnumber,))
            historylist.append((songnumber, now))
        
        c.executemany("insert into playingSet values (?);", songlist)
        c.executemany("insert into queueHistory (songnumber, queuetime) values (?, ?);", historylist) 

        self.db.commit()
        self.db.close()
        self.db = 0
        return songlist

    def getUriList(self, songlist):
        if self.db == 0:
            self.db = self.connect_db()

        c = self.db.cursor()
        uriList = []
        for song in songlist:
            uriList.append(c.execute("select file from mopidyDatabase where rowid=?;", (song[0],)).fetchone()[0])
            
        self.db.close()
        self.db = 0
        return uriList      

    def dbResetPlayingSet(self):
        c = self.db.cursor()
        c.execute("drop table if exists playingSet;")
        c.execute("create table if not exists playingSet(songnumber int);")
        self.db.commit()
        return



