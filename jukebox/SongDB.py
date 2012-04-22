'''
Created on Nov 18, 2011

@author: jbernard
'''

import os
from time import asctime
import marshal


from DBObjects import SongGraph, Song

class SongDB:
	def __init__(self, cachefile, opts):
		self.cacheFileName = cachefile
		
		print asctime(), "Starting cache file load"
		if not os.path.exists(self.cacheFileName):
			print "Cache file does not exist"
			self.sdb = None
			
		try:
			f = open(self.cacheFileName, 'rb')
		except:
			print "Error opening cache file"
			self.sdb = None

		try:
			(songList, artList) = marshal.load(f)
		except:
			print "Error loading cache"
			self.sdb = None
		
		self.sdb = SongGraph(opts)
		for s in songList:
			(title, albumName, trackArtistName, albumArtistName, fn, artx, length, genre, track) = s
			if artx:
				art = artList[artx]
			else:
				art = None			
			self.sdb.addSong(Song(title, albumName, trackArtistName, fn, length, genre, track),
					art, albumArtistName)

		songList = []
		artList = []
		
		print asctime(), "Starting sort"					
		self.sdb.sortAll()
		print asctime(), "Finished - %d music files, %d albums, %d album artists, %d track artists" % self.sdb.count()
			
	def getDBHandler(self):
		return self.sdb
	
	

