'''
Created on Nov 18, 2011

@author: jbernard
'''

ignoreArticles = False

def cmpSongs(a, b):
	ta = a.getTitle()
	tb = b.getTitle()
	if ta != tb:
		return cmp(ta, tb)
	
	ta = a.getArtistName()
	tb = b.getArtistName()
	if ta != tb:
		return cmp(ta, tb)
	
	ta = a.getAlbumName()
	tb = b.getAlbumName()
	return cmp(ta, tb)

def cmpAlbums(a, b):
	ta = a.getAlbumName()
	tb = b.getAlbumName()
	if ta != tb:
		return cmp(ta, tb)
	
	ta = a.getArtistName()
	tb = b.getArtistName()
	return cmp(ta, tb)

def stripArticle(string):
	if not ignoreArticles:
		return string
	
	lstring = string.lower()
	result = string
	
	for article in [ 'the ', 'an ', 'a ']:
		if lstring.startswith(article):
			result = string[len(article):].lstrip()
			break
		
	return result

def cmpArtists(a, b):
	ta = stripArticle(a.getArtistName())
	tb = stripArticle(b.getArtistName())
	return cmp(ta, tb)
	
def cmpArtistAlbums(a, b):
	ta = a.getAlbumName()
	tb = b.getAlbumName()
	return cmp(ta, tb)

def cmpTracks(a, b):
	ta = a.getTrack()
	tb = b.getTrack()
	if ta != tb:
		return cmp(ta, tb)
	
	ta = a.getTitle()
	tb = b.getTitle()
	return cmp(ta, tb)

ITER_MODE_SONG = 0
ITER_MODE_ALBUMARTIST = 1
ITER_MODE_TRACKARTIST = 2
ITER_MODE_ALBUM = 3

DBIterMode = ITER_MODE_SONG

NextSongID = 1
NextAlbumID = 1
NextArtistID = 1
NextPlaylistID = 1


class Song:
	def __init__(self, title, albumName, artistName, fileName, length, genre, track):
		global NextSongID
		self.id = NextSongID
		NextSongID += 1
		
		self.title = title
		self.albumName = albumName
		self.artistName = artistName
		self.file = fileName
		self.length = length
		self.genre = genre
		self.track = track
		self.album = None
		self.artist = None
	
	def release(self):
		self.artist = None
		self.album = None
		
	def setAlbum(self, album):
		self.album = album
		
	def getAlbum(self):
		return self.album
	
	def setArtist(self, artist):
		self.artist = artist
		
	def getArtist(self):
		return self.artist
		
	def getTitle(self):
		return self.title
	
	def getLength(self):
		return self.length
	
	def getAlbumName(self):
		return self.albumName
	
	def getArtistName(self):
		return self.artistName
	
	def getFile(self):
		return self.file
	
	def getTrack(self):
		return self.track
		
class Album:
	def __init__(self, albumName, artistName, art):
		global NextAlbumID
		self.id = NextAlbumID
		NextAlbumID += 1
		
		self.albumName = albumName
		self.artistName = artistName
		self.songs = []
		self.nSongs = 0
		self.art = art
		self.artist = None
		
	def release(self):
		self.songs = []
		self.nSongs = 0
		self.art = None
		
		self.artist = None
		
	def getAlbumName(self):
		return self.albumName
	
	def getArtistName(self):
		return self.artistName
	
	def setArtist(self, artist):
		self.artist = artist
		
	def getArtist(self):
		return self.artist
		
	def addSong(self, song):
		self.songs.append(song)
		self.nSongs += 1
		
	def getTotalTime(self):
		tot = 0
		for s in self.songs:
			tot += s.getLength()
			
		return tot
			
	def getSong(self, sx):
		if sx < 0 or sx >= self.nSongs:
			return None
		return self.songs[sx]

	def getArt(self):
		return self.art
	
	def sortAll(self):
		s = sorted(self.songs, cmpTracks)
		self.songs = s
		
	def __iter__(self):
		self.__tindex__ = 0
		return self
	
	def next(self):
		if self.__tindex__ < self.__len__():
			i = self.__tindex__
			self.__tindex__ += 1
			return self.songs[i]

		raise StopIteration
	
	def __len__(self):
		return len(self.songs)
	
	def getMenuItem(self, x):
		if x < 0 or x >= self.__len__():
			return None
		
		return self.songs[x].getTitle()
	
	def getFirstSortChar(self, x):
		r = self.getMenuItem(x)
		if r == None:
			return None
		
		return r[0]
	
	def getMenuValue(self, x):
		if x < 0 or x >= self.__len__():
			return None
		
		return self.songs[x]
	
	def getMenuMessage(self, x):
		if x < 0 or x >= self.__len__():
			return None
		
		return "Press SELECT for options, PLAY to play Track, ENTER to add to a Playlist"
	
class Artist:
	def __init__(self, artistName):
		global NextArtistID
		self.id = NextArtistID
		NextArtistID += 1
		
		self.artistName = artistName
		self.albumList = []
		self.nAlbums = 0
		self.songList = []
		self.nSongs = 0
		self.iterMode = ITER_MODE_SONG
		
	def release(self):
		self.albumList = []
		self.nAlbums = 0
		
		self.songList = []
		self.nSongs = 0
		
	def getArtistName(self):
		return self.artistName
	
	def addAlbum(self, album):
		self.albumList.append(album)
		self.nAlbums += 1
		
	def getAlbumByName(self, albumName):
		for album in self.albumList:
			if album.getAlbumName() == albumName:
				return album
		return None
	
	def getAlbum(self, ax):
		if ax < 0 or ax >= self.nAlbums:
			return None
		return self.albumList[ax]
	
	def getSong(self, sx):
		if sx < 0 or sx >= self.nSongs:
			return None
		return self.songList[sx]
	
	def addSong(self, song):
		self.songList.append(song)
		self.nSongs += 1
		
	def sortAll(self):
		
		s = sorted(self.songList, cmpSongs)
		self.songList = s
		
		s = sorted(self.albumList, cmpArtistAlbums)
		self.albumList = s
		
	def __iter__(self):
		self.__aindex__ = 0
		return self
		
	def next(self):
		if self.__aindex__ < self.__len__():
			i = self.__aindex__
			self.__aindex__ += 1
			if DBIterMode == ITER_MODE_ALBUM:
				return self.albumList[i]
			else:
				return self.songList[i]

		raise StopIteration
		
	
	def getMenuItem(self, x):
		if x < 0 or x >= self.__len__():
			return None
		
		if DBIterMode == ITER_MODE_ALBUM:
			return "%s (%d)" % (self.albumList[x].getAlbumName(), len(self.albumList[x]))
		else:
			return self.songList[x].getTitle()
			
	def getFirstSortChar(self, x):
		r = self.getMenuItem(x)
		if r == None:
			return None
		
		return r[0]
	
	def getMenuValue(self, x):
		if x < 0 or x >= self.__len__():
			return None
		
		if DBIterMode == ITER_MODE_ALBUM:
			return self.albumList[x]
		else:
			return self.songList[x]
	
	def getMenuMessage(self, x):
		if x < 0 or x >= self.__len__():
			return None
		
		if DBIterMode == ITER_MODE_ALBUM:
			return "Press PLAY to play Album, ENTER to add to a Playlist"
		else:
			return "Press SELECT for options, PLAY to play Track, ENTER to add to a Playlist"
	
	def __len__(self):
		if DBIterMode == ITER_MODE_ALBUM:
			return len(self.albumList)
		else:
			return len(self.songList)	
		
class AlbumList:
	def __init__(self):
		self.albumIndex = {}
		self.albumList = []
		self.nAlbums = 0
		
	def release(self):
		self.albumIndex = {}
		for a in self.albumList:
			a.release()
		self.albumList = []
		self.nAlbums = 0
		
	def count(self):
		return self.nAlbums
		
	def getAlbum(self, title, artistName):
		if title not in self.albumIndex:
			return None
		
		if artistName not in self.albumIndex[title]:
			return None
		
		return self.albumIndex[title][artistName]
	
	def addAlbum(self, album):
		albumName = album.getAlbumName()
		artistName = album.getArtistName()
		
		if albumName in self.albumIndex:
			if not artistName in self.albumIndex[albumName]:
				self.albumIndex[albumName][artistName] = album
				self.albumList.append(album)
				self.nAlbums += 1
		else:
			self.albumIndex[albumName] = {}
			self.albumIndex[albumName][artistName] = album
			self.albumList.append(album)
			self.nAlbums += 1
			
	def sortAll(self):
		s = sorted(self.albumList, cmpAlbums)
		self.albumList = s
		
		for album in self.albumList:
			album.sortAll()
			
	def __iter__(self):
		self.__aindex__ = 0
		return self
	
	def next(self):
		if self.__aindex__ < self.__len__():
			i = self.__aindex__
			self.__aindex__ += 1
			return self.albumList[i]

		raise StopIteration
	
	def getMenuItem(self, x):
		if x < 0 or x >= self.__len__():
			return None
		
		album = self.albumList[x]
		albumName = album.getAlbumName()
		return "%s (%d)" % (albumName, len(album))
		
	def getFirstSortChar(self, x):
		r = self.getMenuItem(x)
		if r == None:
			return None
		
		return r[0]
	
	def getMenuValue(self, x):
		if x < 0 or x >= self.__len__():
			return None
		return self.albumList[x]
	
	def getMenuMessage(self, x):
		if x < 0 or x >= self.__len__():
			return None
		return "Press PLAY to play Album, ENTER to add to a Playlist"
	
	def __len__(self):
		return len(self.albumList)	
			
class ArtistList:
	def __init__(self):
		self.artistList = []
		self.nArtists = 0
		
	def release(self):
		for a in self.artistList:
			a.release();
		self.artistList = []
		self.nArtists = 0
		
	def count(self):
		return self.nArtists
		
	def getArtist(self, artistName):
		for artist in self.artistList:
			if artistName == artist.getArtistName():
				return artist
		return None
	
	def addArtist(self, artist):
		self.artistList.append(artist)
		self.nArtists += 1
		
	def sortAll(self):
		s = sorted(self.artistList, cmpArtists)
		self.artistList = s
		for artist in self.artistList:
			artist.sortAll()
			
	def __iter__(self):
		self.__aindex__ = 0
		return self
	
	def next(self):
		if self.__aindex__ < self.__len__():
			i = self.__aindex__
			self.__aindex__ += 1
			return self.artistList[i]

		raise StopIteration
	
	def getMenuItem(self, x):
		if x < 0 or x >= self.__len__():
			return None
		return "%s (%d)" % (self.artistList[x].getArtistName(), len(self.artistList[x]))
		
	def getFirstSortChar(self, x):
		r = self.getMenuItem(x)
		if r == None:
			return None
		
		return stripArticle(r)[0]
	
	def getMenuValue(self, x):
		if x < 0 or x >= self.__len__():
			return None
		return self.artistList[x]
	
	def getMenuMessage(self, x):
		if x < 0 or x >= self.__len__():
			return None
		if DBIterMode == ITER_MODE_ALBUM:
			return ""
		else:
			return "Press PLAY to play all Artist Songs, ENTER to add to a Playlist"
	
	def __len__(self):
		return len(self.artistList)
		
class PlayList:
	def __init__(self, name):
		global NextPlaylistID
		self.id = NextPlaylistID
		NextPlaylistID += 1
		
		self.name = name
		self.songList = []
		self.nSongs = 0
		
	def addSong(self, song):
		self.songList.append(song)
		self.nSongs += 1
		
	def delSong(self, sx):
		if sx < 0 or sx >= self.__len__():
			return False
		del self.songList[sx]
		return True
	
	def clear(self):
		self.songList = []
		self.nSongs = 0
		
	def swapSongs(self, a, b):
		if a < 0 or a >= self.__len__:
			return False
		if b < 0 or b >= self.__len__():
			return False
		
		s = self.songList[a]
		self.songList[a] = self.songList[b]
		self.songList[b] = s
		
		return True
		
	def getName(self):
		return self.name
	
	def getMenuItem(self, x):
		if x < 0 or x >= self.__len__():
			return None
		s = self.songList[x]
		return "%s / %s" % (s.getArtist().getArtistName(), s.getTitle())
		
	def getFirstSortChar(self, x):
		r = self.getMenuItem(x)
		if r == None:
			return None
		
		return r[0]
	
	def getMenuValue(self, x):
		if x < 0 or x >= self.__len__():
			return None
		return self.songList[x]
	
	def getMenuMessage(self, x):
		if x < 0 or x >= self.__len__():
			return None
		return ""
	
	def __len__(self):
		return len(self.songList)
		
	def __iter__(self):
		self.__plindex__ = 0
		return self
	
	def next(self):
		if self.__plindex__ < self.__len__():
			i = self.__plindex__
			self.__plindex__ += 1
			return self.songList[i]

		raise StopIteration
				
class SongGraph:
	def __init__(self, opts):
		global ignoreArticles
		if 'ignorearticles' in opts:
			ignoreArticles = opts['ignorearticles']		
			
		self.songList = []
		self.nSongs = 0
		self.albumList = AlbumList()
		self.albumArtistList = ArtistList()
		self.trackArtistList = ArtistList()
		self.iterMode = ITER_MODE_SONG
		self.songIndex = {}
		
	def release(self):
		for s in self.songList:
			s.release()
		self.songList = []
		self.nSongs = 0
		
		self.albumList.release()
		self.albumList = None
		self.albumArtistList.release()
		self.albumArtistList = None
		self.trackArtistList.release()
		self.trackArtistList = None
		
	def count(self):
		return (self.nSongs, self.albumList.count(),
			self.albumArtistList.count(), self.trackArtistList.count())
	
	def addSong(self, song, art, albumArtistName):
		self.songList.append(song)
		self.nSongs += 1
		
		self.songIndex[song.getFile()] = song
		
		albumName = song.getAlbumName()
		trackArtistName = song.getArtistName()
		
		album = self.albumList.getAlbum(albumName, albumArtistName)
		if album == None:
			album = Album(albumName, albumArtistName, art)
			self.albumList.addAlbum(album)
			
		album.addSong(song)
		song.setAlbum(album)
		
		artist = self.albumArtistList.getArtist(albumArtistName)
		if artist == None:
			artist = Artist(albumArtistName)
			self.albumArtistList.addArtist(artist)
			artist.addAlbum(album)
		else:
			if not artist.getAlbumByName(albumName):
				artist.addAlbum(album)
		artist.addSong(song)
		album.setArtist(artist)
				
		artist = self.trackArtistList.getArtist(trackArtistName)
		if artist == None:
			artist = Artist(trackArtistName)
			self.trackArtistList.addArtist(artist)
				
		artist.addSong(song)
		song.setArtist(artist)
		
	def getSongByFile(self, fn):
		if fn not in self.songIndex:
			return None
		
		return self.songIndex[fn]
		
	def sortAll(self):
		s = sorted(self.songList, cmpSongs)
		self.songList = s
		
		self.albumList.sortAll()
		self.albumArtistList.sortAll()
		self.trackArtistList.sortAll()
		
	def getSong(self, sx):
		if sx < 0 or sx >= self.nSongs:
			return None
		return self.songList[sx]
	
	def getAlbum(self, ax):
		if ax < 0 or ax >= self.albumList.count():
			return None
		return self.albumList[ax]
	
	def getAlbumList(self):
		return self.albumList
	
	def getAlbumArtist(self, ax):
		if ax < 0 or ax >= self.albumArtistList.count():
			return None
		return self.albumArtistList[ax]
	
	def getAlbumArtistList(self):
		return self.albumArtistList
	
	def getTrackArtist(self, ax):
		if ax < 0 or ax >= self.trackArtistList.count():
			return None
		return self.trackArtistList[ax]
		
	def getTrackArtistList(self):
		return self.trackArtistList
		
	def setIterMode(self, mode):
		global DBIterMode
		
		DBIterMode = mode

	def getMenuItem(self, x):
		if x < 0 or x >= self.__len__():
			return None
		return self.songList[x].getTitle()
		
	def getFirstSortChar(self, x):
		r = self.getMenuItem(x)
		if r == None:
			return None
		
		return r[0]
	
	def getMenuValue(self, x):
		if x < 0 or x >= self.__len__():
			return None
		return self.songList[x]
	
	def getMenuMessage(self, x):
		if x < 0 or x >= self.__len__():
			return None
		return "Press SELECT for options, PLAY to play Track, ENTER to add to a Playlist"
	
	def __len__(self):
		return len(self.songList)	
	
	def __iter__(self):
		self.__slindex__ = 0
		return self
	
	def next(self):
		if self.__slindex__ < self.__len__():
			i = self.__slindex__
			self.__slindex__ += 1
			return self.songList[i]

		raise StopIteration
