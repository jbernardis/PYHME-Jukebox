from hme import *
import os

from DBObjects import PlayList
from MenuMgr import Menu
from Keyboard import Keyboard
from PLEdit import PLEdit

KBD_DONE = 1
KBD_CANCEL = 2

PLE_DONE = 3

DEL_CONFIRM_MESSAGE = "Press CLEAR again to confirm deletion"

class PlaylistError(Exception):
	pass

class PlaylistMgr:
	def __init__(self, app, done=1, skin=None):
		self.app = app
		self.sdb = app.sdb
		self.plmDone = done
		self.kbd = Keyboard(app, done=KBD_DONE, cancel=KBD_CANCEL, skin=skin)
		self.playlists = []
		self.loadPlaylists()
		#self.buildPLMenu()
		self.menu = []
		self.active = False
		self.plIndex = None
		self.clearPending = False
		self.chosenPlaylist = None
		self.albumToAdd = None
		self.artistToAdd = None
		self.songToAdd = None
		self.normalMessage = ""
		self.ple = PLEdit(app)
		
	def loadPlaylists(self):
		path = os.path.join(os.path.dirname(__file__), "playlists")
		if not os.path.isdir(path):
			print "Creating playlists directory"
			os.mkdir(path)
		
		if not os.access(path, os.W_OK):
			raise PlaylistError("Cannot write into playlist directory")	
		
		files = os.listdir(path)
		for name in files:
			if name.startswith("."): continue
			fname, fext = os.path.splitext(name)
			if not fext.lower() in [".jpl", ".m3u"]: continue
			
			pl = PlayList(fname)
			fn = os.path.join(path, name)
			for line in file(fn, 'U'):
				l = line.strip()
				if l.startswith('#') or len(l) == 0:
					continue
				
				so = self.sdb.getSongByFile(l)
				if not so:
					print "Playlist %s, no file with filename %s - skipping" % (name, l)
				else:
					pl.addSong(so)
			
			self.playlists.append(pl)
			
	def delPlaylistFile(self, name):
		path = os.path.join(os.path.dirname(__file__), "playlists", name + ".jpl")

		try:
			print "Attempting to delete (%s)" % path
			os.remove(path)
		except:
			print "delete failed"
					
	def savePlaylists(self):
		for p in self.playlists:
			self.savePlaylist(p)
			
	def savePlaylist(self, pl):
		fn = os.path.join(os.path.dirname(__file__), "playlists", pl.getName() + ".jpl")
		try:
			fp = open(fn, "w")
		except:
			print "Error opening playlist file %s for output" % fn
		else:
			for s in pl:
				fp.write("%s\n" % s.getFile())
			fp.close()
			
		# remove corresponding m3u file if it exists
		fn = os.path.join(os.path.dirname(__file__), "playlists", pl.getName() + ".m3u")
		
		try:
			os.remove(fn)
		except:
			pass
							
	def buildPLMenu(self):
		menu = []
		i = 0
		menu.append(["Add New Playlist", -1, True, ""])
		self.normalMessage = "Press PLAY to play Playlist, CLEAR to delete"
		if self.app.nowPlaying.isActive():
			if not self.selectonly:
				menu.append(['"Now Playing"', -2, True, ""])
				self.normalMessage = 'Press PLAY to play Playlist, CLEAR to delete, ENTER to Add to "Now Playing" Playlist'
			
		for p in self.playlists:
			menu.append(["%s (%d)" % (p.getName(), len(p)), i, True, self.normalMessage])
			i += 1
			
		self.menu = Menu(menu)
		
	def activate(self, selectonly=False, done=None, album=None, artist=None, song=None, playlist=None):
		self.albumToAdd = album
		self.artistToAdd = artist
		self.songToAdd = song
		self.playlistToAdd = playlist
		
		self.selectonly = selectonly
		
		if self.active:
			return
		
		if done:
			self.plmDone = done
			
		self.buildPLMenu()
			
		m, self.plIndex = self.app.mm.Descend(self.menu)
		self.active = True
		
	def deactivate(self):
		if not self.active:
			return
		self.app.mm.Ascend()
		self.active = False
		
	def isActive(self):
		return self.active
	
	def handle_key_press(self, keynum, rawcode):
		if self.kbd.isActive():
			self.kbd.handle_key_press(keynum, rawcode)
			return
		
		if self.ple.isActive():
			self.ple.handle_key_press(keynum, rawcode)
			return
		
		if self.app.mm.isNavKey(keynum, rawcode):
			if self.clearPending:
				self.clearPending = False
				self.app.setMessage(self.normalMessage)
				
			m, self.plIndex = self.app.mm.Navigate(keynum, rawcode)
			return
			
		if keynum != KEY_CLEAR:
			if self.clearPending:
				self.clearPending = False
				self.app.setMessage(self.normalMessage)
			
		if keynum == KEY_CLEAR:
			value = self.menu.getMenuValue(self.plIndex)
			if value in [ -1, -2 ]:
				self.app.sound('bonk')
				
			else:
				if self.clearPending:
					print "value = ", value, ", length pl = ", len(self.playlists)
					print "Index = ", self.plIndex
					if value >= 0 and value < len(self.playlists):
						self.delPlaylistFile(self.playlists[value].getName())
						del self.playlists[value]
						self.buildPLMenu()
						self.app.mm.ReplaceMenu(self.menu)
						
					self.clearPending = False
					self.app.sound('updown')

				else:
					self.clearPending = True
					self.app.sound('alert')
					self.app.setMessage(DEL_CONFIRM_MESSAGE)
				
		elif keynum == KEY_TIVO:
			if rawcode == KBD_DONE:
				s = self.kbd.getResult()
				if s != "":
					pl = PlayList(s)
					self.playlists.append(pl)
					self.buildPLMenu()
					self.app.mm.ReplaceMenu(self.menu)
				#self.app.sound('updown')
				
			elif rawcode == KBD_CANCEL:
				self.app.sound('alert')
				
			elif rawcode == PLE_DONE:
				self.buildPLMenu()
				self.app.mm.ReplaceMenu(self.menu)
				self.app.mm.show()
				if self.chosenPlaylist:
					self.savePlaylist(self.chosenPlaylist)
				self.app.setSubTitle("Choose Playlist")
				self.app.sound('updown')
				
		elif keynum == KEY_LEFT:
			self.app.mm.Ascend()
			self.active = False
			self.app.send_key(KEY_TIVO, self.plmDone)
			self.app.sound('updown')
			
		elif keynum in [ KEY_SELECT, KEY_RIGHT ]:
			value = self.menu.getMenuValue(self.plIndex)
			if value == -1:
				# new playlist
				self.kbd.reset()
				self.kbd.activate()
				
			elif value == -2:
				self.chosenPlaylist = None
				
				changes = False		

				if self.songToAdd:
					self.app.addToNowPlaying(song = self.songToAdd)
					self.songToAdd = None
					changes = True
					
				if self.albumToAdd:
					self.app.addToNowPlaying(album = self.albumToAdd)
					self.albumToAdd = None
					changes = True
					
				if self.playlistToAdd:
					for s in self.playlistToAdd:
						self.chosenPlaylist.addSong(s)
					self.playlistToAdd = None
					changes = True
					
				if self.artistToAdd:
					self.app.addToNowPlaying(artist = self.artistToAdd)
					self.artistToAdd = None
					changes = True
					
				if changes:
					self.buildPLMenu()
					self.app.mm.ReplaceMenu(self.menu)
	
				self.app.mm.hide()	
				self.ple.browse(self.app.NPPlaylist, done=PLE_DONE)
				
			else:
				self.chosenPlaylist = self.playlists[value]
				
				changes = False
				
				if self.songToAdd:
					self.chosenPlaylist.addSong(self.songToAdd)
					self.songToAdd = None
					changes = True
					
				if self.albumToAdd:
					for s in self.albumToAdd:
						self.chosenPlaylist.addSong(s)
					self.albumToAdd = None
					changes = True
					
				if self.playlistToAdd:
					for s in self.playlistToAdd:
						self.chosenPlaylist.addSong(s)
					self.playlistToAdd = None
					changes = True
					
				if self.artistToAdd:
					for s in self.artistToAdd:
						self.chosenPlaylist.addSong(s)
					self.artistToAdd = None
					changes = True
					
				if changes:
					self.buildPLMenu()
					self.app.mm.ReplaceMenu(self.menu)

				if len(self.chosenPlaylist) == 0:
					self.app.sound('bonk')
					return
					
				self.app.mm.hide()			
				self.ple.edit(self.chosenPlaylist, done=PLE_DONE)
				
					
			self.app.sound('updown')
			
		elif keynum == KEY_ENTER:
			if self.selectonly:
				self.app.sound('bonk')
			else:
				value = self.menu.getMenuValue(self.plIndex)
				if value < 0:
					self.app.sound('bonk')
				else:
					self.chosenPlaylist = self.playlists[value]
					self.app.addToNowPlaying(playlist = self.chosenPlaylist)
		
		elif keynum == KEY_PLAY:
			value = self.menu.getMenuValue(self.plIndex)
			if value < 0:
				self.app.sound('bonk')
			else:
				self.chosenPlaylist = self.playlists[value]
				self.app.addToNowPlaying(clear=True, playlist = self.chosenPlaylist)
					
				self.app.nowPlaying.Play(self.app.NPPlaylist,
										shuffle=self.app.opts['playlistshuffle'],
										loop=self.app.opts['playlistloop'])
				
		else:
			self.app.sound('bonk')
