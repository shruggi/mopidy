#!/usr/bin/python
from mpd import MPDClient
import sqlite3
import random
import datetime

import oermis2 as mopidyPlaylist

class mopidyfront:

    address = ''
    port = 0
    client = 0

    playlistController = mopidyPlaylist.mopidyPlaylist(3600)

    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.start()

    def connect(self):
        client = MPDClient()
        client.connect(self.address, self.port)
        return client

    def start(self):
        self.client = self.connect() 
        
        #serverStatus = self.client.status()

        #if serverStatus['state'] == 'stop':
        #    self.client.play()
        #       print("Started!\n")
        #self.client.idle()
        self.refreshDatabase()
        self.client.consume(1)
        self.client.random(0)


        while 1:
            serverStatus = self.client.status()
            if int(serverStatus['playlistlength']) <= 1:
                playingSet = self.playlistController.createPlayingSet()
                uriList = self.playlistController.getUriList(playingSet)
                for song in uriList:
                    self.client.add(song)
                print("Queued next tracks")
            self.client.idle()        

    def refreshDatabase(self):

        self.db = sqlite3.connect("mopidy.db")
        c = self.db.cursor()
        c.execute("drop table if exists mopidyDatabase;")
        c.execute("create table if not exists mopidyDatabase (album text, title text, track text, artist text, genre text, albumartist text, file text, time int, date text);")

        c.execute("drop table if exists mopidyDatabaseWeights;")
        c.execute("drop view if exists mopidyDatabaseWeightsSum;")
        c.execute("create table if not exists mopidyDatabaseWeights (weight int);")
        c.execute("create view mopidyDatabaseWeightsSum as select count(), sum(weight) from mopidyDatabaseWeights;")

        self.db.commit()

        if self.client == 0:
            self.client = self.connect()

        
        rawTrackData = []
        localFolders = ["/"]
        for path in localFolders:
            data = self.client.lsinfo(path)
            for row in data:
                if 'directory' in row:
                    localFolders.append(row['directory'])
                else:
                    rawTrackData.append(row)

        insertArray = []
        for row in rawTrackData:
            if not 'album' in row: row['album'] = ""
            if not 'albumartist' in row: row['albumartist'] = ""
            if not 'title' in row: row['title'] = ""
            if not 'track' in row: row['track'] = ""
            if not 'artist' in row: row['artist'] = ""
            if not 'genre' in row: row['genre'] = ""
            if not 'file' in row: row['file'] = ""
            if not 'time' in row: row['time'] = ""
            if not 'date' in row: row['date'] = ""
            tmp = (row['album'],row['title'],row['track'],row['artist'],row['genre'],row['albumartist'],row['file'],row['time'],row['date'])
            insertArray.append(tmp)

        print("Database has %s items" % len(insertArray))
        x = 0
        for row in insertArray:
            print(row)
            c.execute("insert into mopidyDatabase (album, title, track, artist, genre, albumartist, file, time, date) values (?, ?, ?, ?, ?, ?, ?, ?, ?);",row)
            c.execute("insert into mopidyDatabaseWeights (weight) values (1)"); # default weight
            x = x + 1
        
        self.db.commit()
        self.db.close()
        print("Updated %s items" % x)
    
        return


mopidy = mopidyfront("192.168.100.106", 6600)
