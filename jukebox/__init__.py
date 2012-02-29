from hme import *
import os
from time import asctime, time, sleep
import thread
import random

import Config
from Config import ( screenWidth, screenHeight, titleYPos, subTitleYPos, messageYPos, artWidth, artHeight, CACHEFILE )
from SongDB import SongDB
from DBObjects import  PlayList, ITER_MODE_ALBUM, ITER_MODE_SONG
from MenuMgr import MenuMgr, Menu
from DetailMgr import DetailMgr
from PlaylistMgr import PlaylistMgr
from NowPlaying import NowPlaying
from LyricView import LyricView
from SetPrefs import SetPrefs

TITLE = 'JukeBox'
VERSION = '1.0f'

MODE_MAIN_MENU = 0
MODE_PLAYLIST = 10
MODE_ALBUM_ARTIST = 20
MODE_ALBUM_ARTIST_ALBUM = 21
MODE_ALBUM_ARTIST_ALBUM_TRACK = 22
MODE_ALBUM_ARTIST_ALBUM_TRACK_CHOICES = 23
MODE_ALBUM = 30
MODE_ALBUM_TRACK = 31
MODE_ALBUM_TRACK_CHOICES = 32
MODE_TRACK_ARTIST = 40
MODE_TRACK_ARTIST_TRACK = 41
MODE_TRACK_ARTIST_TRACK_CHOICES = 42
MODE_TRACK = 50
MODE_TRACK_CHOICES = 51
MODE_PREFS = 90

print asctime(), TITLE + " version " + VERSION + " module initializing"
config = Config.Config()
opts = config.load()

sdb = None
if opts['preloadcache']:
	sdb = SongDB(CACHEFILE).getDBHandler()
	cachestamp = os.stat(CACHEFILE).st_mtime
	
	def cacheloader(interval):
		global cachestamp, sdb
		
		print "Cache watcher thread starting - watch interval = %d" % interval
		while True:
			sleep(interval)
			newcachestamp = os.stat(CACHEFILE).st_mtime
			if newcachestamp > cachestamp:
				print "Changed cache detected - reloading..."
				sdb = SongDB(CACHEFILE).getDBHandler()
				cachestamp = newcachestamp
				
	thread.start_new_thread(cacheloader, (opts['cachewatchinterval'], ))

AppPath = os.path.dirname(__file__)

CHOICE_NOWPLAYING = 1
CHOICE_PLAYLIST = 2
CHOICE_ALBUM_ARTIST = 4
CHOICE_ALBUM = 5
CHOICE_TRACK_ARTIST = 6
CHOICE_TRACK = 7
CHOICE_PREFS = 8
CHOICE_PLAY_TRACK = 9
CHOICE_PLAY_ALBUM = 10
CHOICE_PLAY_ALBUM_TRACK = 11
CHOICE_PLAY_ARTIST = 12
CHOICE_PLAY_ARTIST_TRACK = 13
CHOICE_SONG_PLAYLIST = 14
CHOICE_ALBUM_PLAYLIST = 15
CHOICE_ARTIST_PLAYLIST = 16

PLM_DONE = 1
TIMER = 999

TICKER_INTERVAL = 30

mainMenu = Menu([
			["Now Playing", CHOICE_NOWPLAYING, False, 'Press ENTER to save "Now Playing" as a playlist'],
			["Browse Playlists", CHOICE_PLAYLIST, True, ""],
			["Browse Album Artists", CHOICE_ALBUM_ARTIST, True, ""],
			["Browse Albums", CHOICE_ALBUM, True, ""],
			["Browse Track Artists", CHOICE_TRACK_ARTIST, True, ""],
			["Browse Tracks", CHOICE_TRACK, True, "Press PLAY to play all tracks"],
			["Set Preferences", CHOICE_PREFS, True, ""]
			])

albumTrackMenu = Menu([
			["Play Track", CHOICE_PLAY_TRACK, True, ""],
			["Play Album", CHOICE_PLAY_ALBUM, True, ""],
			["Play Album Starting with this Track", CHOICE_PLAY_ALBUM_TRACK, True, ""],
			["Add Track to a Playlist", CHOICE_SONG_PLAYLIST, True, ""],
			["Add Album to a Playlist", CHOICE_ALBUM_PLAYLIST, True, ""],
			])

artistTrackMenu = Menu([
			["Play Track", CHOICE_PLAY_TRACK, True, ""],
			["Play all Artist Tracks", CHOICE_PLAY_ARTIST, True, ""],
			["Play all Artist Tracks Starting with this Track", CHOICE_PLAY_ARTIST_TRACK, True, ""],
			["Add Track to a Playlist", CHOICE_SONG_PLAYLIST, True, ""],
			["Add All Artist Tracks to a Playlist", CHOICE_ARTIST_PLAYLIST, True, ""],
			["Add Album to a Playlist", CHOICE_ALBUM_PLAYLIST, True, ""],
			["Add Track to a Playlist", CHOICE_SONG_PLAYLIST, True, ""],
			])

trackMenu = Menu([
			["Play Track", CHOICE_PLAY_TRACK, True, ""],
			["Add Track to a Playlist", CHOICE_SONG_PLAYLIST, True, ""],
			["Add All Track Artist Tracks to a Playlist", CHOICE_ARTIST_PLAYLIST, True, ""],
			["Add Album to a Playlist", CHOICE_ALBUM_PLAYLIST, True, ""],
			])

class Images:
	def __init__(self, app):
		self.Background    = self.loadimage(app, 'background')
		self.NPBackground  = self.loadimage(app, 'npbackground')
		self.LyricBG       = self.loadimage(app, 'lyricbackground')
		self.LyricUp       = self.loadimage(app, 'lyricup')
		self.LyricDown     = self.loadimage(app, 'lyricdown')
		self.CueUp         = self.loadimage(app, 'cueup')
		self.CueDown       = self.loadimage(app, 'cuedown')
		self.CueLeft       = self.loadimage(app, 'cueleft')
		self.HiLite        = self.loadimage(app, 'hilite')
		self.EditBrowse    = self.loadimage(app, 'editbrowse')
		self.EditNormal    = self.loadimage(app, 'editnormal')
		self.EditNormalU   = self.loadimage(app, 'editnormalu')
		self.EditNormalD   = self.loadimage(app, 'editnormald')
		self.EditNormalUD  = self.loadimage(app, 'editnormalud')
		self.EditUpDn      = self.loadimage(app, 'editupdn')
		self.EditUpDnU     = self.loadimage(app, 'editupdnu')
		self.EditUpDnD     = self.loadimage(app, 'editupdnd')
		self.EditUpDnUD    = self.loadimage(app, 'editupdnud')
		self.NPCursor      = self.loadimage(app, 'npcursor')
		self.Play          = self.loadimage(app, 'play')
		self.Pause         = self.loadimage(app, 'pause')
		self.FF1           = self.loadimage(app, 'ff1')
		self.FF2           = self.loadimage(app, 'ff2')
		self.FF3           = self.loadimage(app, 'ff3')
		self.RW1           = self.loadimage(app, 'rw1')
		self.RW2           = self.loadimage(app, 'rw2')
		self.RW3           = self.loadimage(app, 'rw3')
		self.ProgressBkg   = self.loadimage(app, 'progressbkg')
		self.ProgressBar   = self.loadimage(app, 'progressbar')
		self.DefaultArt    = self.loadimage(app, 'defaultalbumart')
		self.FldBkg        = self.loadimage(app, 'fieldbkg')
		self.FldBkgHi      = self.loadimage(app, 'fieldbkghi')
		fn = os.path.join(AppPath, "icon.png")
		if os.path.exists(fn):
			self.Icon = Image(app, fn)
		else:
			print "Icon file missing for jukebox"
			self.Icon = None
	
	def loadimage(self, app, name):
		skin = app.opts['skin']
		if skin != None:
			fn = os.path.join(AppPath, 'skins', skin, name + ".png")
			if os.path.exists(fn):
				return Image(app, fn)
			
		fn = os.path.join(AppPath, 'skins', name + ".png")
		if os.path.exists(fn):
			return Image(app, fn)
		
		if skin == None:
			print "image '" + name + "' missing for default skin"
		else:
			print "image '" + name + "' missing for skin '" + skin + "'"
		return None
			

class Fonts:
	def __init__(self, app):
		self.fnt16 = Font(app, size=16)
		self.fnt20 = Font(app, size=20)
		self.fnt24 = Font(app, size=24)
		self.fnt30 = Font(app, size=30)

class Jukebox(Application):
	def handle_resolution(self):
		for (hres, vres, x, y) in self.resolutions:
			if (hres == 1280):
				return (hres, vres, x, y)
			
		print "NO HD resolutions found!!!"
		self.active = False
		return self.resolutions[0]
	
	def handle_error(self, code, text):
		print "Got an error event, text = (%s)" % text
		print "Error code = ", code

	def startup(self):
		print "Jukebox thread entering startup"
		self.opts = opts
		if opts['preloadcache']:
			self.sdb = sdb
		else:
			self.sdb = SongDB(CACHEFILE).getDBHandler()
		
	def ticker(self):
		while self.active:
			self.sleep(TICKER_INTERVAL)
			self.send_key(KEY_TIVO, TIMER)
			
	def cleanup(self):
		if not self.opts['preloadcache']:
			self.sdb.release()
			self.sdb = None
			
		if self.nowPlaying.isActive():
			self.nowPlaying.cleanup()
			
	def handle_idle(self, flag):
		if self.nowPlaying.isActive():
			return True
		else:
			return False;
		
	def handle_active(self):
		print "Jukebox thread activating"
		thread.start_new_thread(self.ticker, ())
		self.lastKeyTime = time()
		self.confirmExit = False
		self.isScreenSaverActive = False
		
		self.myimages = Images(self)
		self.myfonts = Fonts(self)
		
		self.stack = []

		self.root.set_resource(self.myimages.Background)
		self.TitleView = View(self, height=30, width=screenWidth, ypos=titleYPos, parent=self.root)
		self.SubTitleView= View(self, height=20, width=screenWidth, ypos=subTitleYPos, parent=self.root)
		self.MessageView= View(self, height=40, width=screenWidth, ypos=messageYPos, parent=self.root)
		
		self.menuTitle = "Main Menu"

		self.TitleView.set_text(TITLE, font=self.myfonts.fnt30, colornum=0xffffff, flags=RSRC_VALIGN_BOTTOM)
		self.setSubTitle(self.menuTitle)

		self.menuMode = MODE_MAIN_MENU
		self.mm = MenuMgr(self)
		self.detMgr = DetailMgr(self)
		self.NPPlaylist = PlayList("Now Playing")

		self.plMgr = PlaylistMgr(self, skin=opts['skin'])
		self.iterMode = ITER_MODE_ALBUM
		
		self.setPrefs = SetPrefs(self)
		
		self.nowPlaying = NowPlaying(self)
		
		self.lyricView = LyricView(self)

		nSong, nAlbum, nAlbumArtist, nTrackArtist = self.sdb.count()
		mainMenu.setCount(CHOICE_ALBUM_ARTIST, nAlbumArtist)		
		mainMenu.setCount(CHOICE_TRACK_ARTIST, nTrackArtist)		
		mainMenu.setCount(CHOICE_ALBUM, nAlbum)		
		mainMenu.setCount(CHOICE_TRACK, nSong)	
		
		self.updateMenus(False)	
		
		self.currentArtist = None
		self.currentAlbum = None
		self.currentTrack = None
		
		self.currentMenu, self.currentItem = self.mm.Descend(mainMenu)
		
		# screen saver needs to be last so it is on top
		self.vwScreenSaver = View(self, visible=True, transparency=1, colornum=0, parent=self.root)
		self.vwScreenSaverArt = View(self.app, height=artHeight, width=artWidth, ypos=0, xpos=0, parent=self.vwScreenSaver)
		self.setScreenSaverArt(None)
		
	def setScreenSaverArt(self, art):
		if art == None:
			self.vwScreenSaverArt.set_resource(self.myimages.Icon)
		else:
			self.vwScreenSaverArt.set_resource(art, flags=RSRC_VALIGN_TOP+RSRC_HALIGN_LEFT)
		
	def activateScreenSaver(self, flag):
		if flag:
			if self.isScreenSaverActive: return
			self.isScreenSaverActive = True
			self.vwScreenSaverArt.set_bounds(xpos = 0, ypos = 0)
			self.ssDirection = 1
			self.vwScreenSaver.set_transparency(0, animation=Animation(self, 0.75))
			y = int(random.choice(range(screenHeight-artHeight)))
			self.vwScreenSaverArt.set_bounds(xpos = (screenWidth - artWidth), ypos = y, animtime = TICKER_INTERVAL)
			
		else:
			if not self.isScreenSaverActive: return
			self.isScreenSaverActive = False
			self.vwScreenSaver.set_transparency(1, animation=Animation(self, 0.75))
			

	def setSubTitle(self, text):
		self.SubTitleView.set_text(text, font=self.myfonts.fnt20, colornum=0xffffff, flags=RSRC_VALIGN_BOTTOM)
		
	def setMessage(self, text):
		self.MessageView.set_text(text, font=self.myfonts.fnt20, colornum=0xffffff, flags=RSRC_VALIGN_BOTTOM + RSRC_HALIGN_CENTER)
		
	def updateMenus(self, flag):
		# nowplaying status has changed - update the menus accordingly
		mainMenu.setActive(CHOICE_NOWPLAYING, flag)
		self.mm.RefreshMenu(mainMenu)
		
	def addToNowPlaying(self, clear=False, album=None, artist=None, song=None, playlist=None):
		if clear:
			self.NPPlaylist.clear()
			
		if song:
			self.NPPlaylist.addSong(song)
			
		if album:
			for s in album:
				self.NPPlaylist.addSong(s)
			
		if playlist:
			for s in playlist:
				self.NPPlaylist.addSong(s)
				
		if artist:
			for s in artist:
				self.NPPlaylist.addSong(s)
		
		self.nowPlaying.addToNowPlaying(album=album, artist=artist, song=song, playlist=playlist)
		
	def showLyrics(self, song):
		self.lyricView.loadLyrics(song)
			
	def handle_key_press(self, keynum, rawcode):
		if keynum != KEY_TIVO:
			self.lastKeyTime = time()
			
		if keynum != KEY_THUMBSUP and self.confirmExit:
			self.setMessage('')
			self.confirmExit = False
			
		if keynum == KEY_TIVO and rawcode == TIMER:
			if self.isScreenSaverActive:
				y = int(random.choice(range(screenHeight-artHeight)))
				if self.ssDirection == -1:
					self.ssDirection = 1
					self.vwScreenSaverArt.set_bounds(xpos = (screenWidth - artWidth), ypos = y, animtime = TICKER_INTERVAL)
				else:
					self.ssDirection = -1
					self.vwScreenSaverArt.set_bounds(xpos = 0, ypos = y, animtime = TICKER_INTERVAL)

			now = time()
			idleTime = now - self.lastKeyTime
			
			if opts['autoswitchnp'] != 0 and idleTime > opts['autoswitchnp']:
				if self.nowPlaying.isActive() and not self.nowPlaying.isShowing():
					self.nowPlaying.show()
					
			if opts['screensaver'] != 0 and idleTime > opts['screensaver']:
				if not self.isScreenSaverActive:
					self.activateScreenSaver(True)
				
			return
				
		if keynum != KEY_TIVO and self.isScreenSaverActive:
			self.activateScreenSaver(False)
			return
		
		if self.lyricView.isShowing():
			self.lyricView.handle_key_press(keynum, rawcode)
			
		elif self.nowPlaying.isShowing():
			self.nowPlaying.handle_key_press(keynum, rawcode)
			
		elif self.plMgr.isActive():
			self.plMgr.handle_key_press(keynum, rawcode)
		
		elif self.setPrefs.isActive():
			self.setPrefs.handle_key_press(keynum, rawcode)
		
		elif self.mm.isNavKey(keynum, rawcode):
			self.currentMenu, self.currentItem = self.mm.Navigate(keynum, rawcode)
			
		elif keynum == KEY_TIVO:
			if rawcode == PLM_DONE:
				self.setSubTitle(self.menuTitle)
				self.mm.RefreshMenu(None)
				self.sdb.setIterMode(self.iterMode)
			
		elif keynum in [ KEY_LEFT, KEY_THUMBSUP ]:
			if keynum == KEY_LEFT and self.mm.atRoot() and self.nowPlaying.isActive():
				self.setMessage('Press THUMBS-UP to confirm exit while music is playing')
				self.sound('alert')
				self.confirmExit = True
				return
			
			if keynum == KEY_THUMBSUP and not self.confirmExit:
				self.sound('bonk')
				return
			
			self.currentMenu, self.currentItem = self.mm.Ascend()
			if self.currentMenu == None:
				self.active = False
				return
			self.menuMode, self.menuTitle, self.iterMode = self.stack.pop()
			self.setSubTitle(self.menuTitle)
			self.sdb.setIterMode(self.iterMode)
			self.sound('updown')
			
		else:
			if self.menuMode == MODE_MAIN_MENU:
				self.handleKeyMainMenu(keynum, rawcode)
			
			elif self.menuMode == MODE_ALBUM_ARTIST:
				self.handleKeyAlbumArtist(keynum, rawcode)
				
			elif self.menuMode == MODE_ALBUM_ARTIST_ALBUM:
				self.handleKeyAlbumArtistAlbum(keynum, rawcode)
				
			elif self.menuMode == MODE_ALBUM_ARTIST_ALBUM_TRACK:
				self.handleKeyAlbumArtistAlbumTrack(keynum, rawcode)
				
			elif self.menuMode == MODE_ALBUM_ARTIST_ALBUM_TRACK_CHOICES:
				self.handleKeyAlbumArtistAlbumTrackChoices(keynum, rawcode)
				
			elif self.menuMode == MODE_ALBUM:
				self.handleKeyAlbum(keynum, rawcode)
			
			elif self.menuMode == MODE_ALBUM_TRACK:
				self.handleKeyAlbumTrack(keynum, rawcode)
				
			elif self.menuMode == MODE_ALBUM_TRACK_CHOICES:
				self.handleKeyAlbumTrackChoices(keynum, rawcode)
				
			elif self.menuMode == MODE_TRACK_ARTIST:
				self.handleKeyTrackArtist(keynum, rawcode)
				
			elif self.menuMode == MODE_TRACK_ARTIST_TRACK:
				self.handleKeyTrackArtistTrack(keynum, rawcode)
				
			elif self.menuMode == MODE_TRACK_ARTIST_TRACK_CHOICES:
				self.handleKeyTrackArtistTrackChoices(keynum, rawcode)
				
			elif self.menuMode == MODE_TRACK:
				self.handleKeyTrack(keynum, rawcode)
				
			elif self.menuMode == MODE_TRACK_CHOICES:
				self.handleKeyTrackChoices(keynum, rawcode)
				
			else:
				self.sound('bonk')
				return
			
		self.setCurrentInfo()
		self.showDetails()
			
	def handleKeyMainMenu(self, keynum, rawcode):
		value = self.currentMenu.getMenuValue(self.currentItem)
		if keynum in [KEY_RIGHT, KEY_SELECT]:
			if value == CHOICE_ALBUM_ARTIST:
				self.stack.append([self.menuMode, self.menuTitle, self.iterMode])
				menu = self.sdb.getAlbumArtistList()
				self.menuMode = MODE_ALBUM_ARTIST
				self.iterMode = ITER_MODE_ALBUM
				self.sdb.setIterMode(self.iterMode)
				self.menuTitle = "Album Artists"
				self.setSubTitle(self.menuTitle)
				self.currentMenu, self.currentItem = self.mm.Descend(menu)
	
			elif value == CHOICE_ALBUM:
				self.stack.append([self.menuMode, self.menuTitle, self.iterMode])
				menu = self.sdb.getAlbumList()
				self.menuMode = MODE_ALBUM
				self.iterMode = ITER_MODE_ALBUM
				self.sdb.setIterMode(self.iterMode)
				self.menuTitle = "All Albums"
				self.setSubTitle(self.menuTitle)
				self.currentMenu, self.currentItem = self.mm.Descend(menu, offset=8)
	
			elif value == CHOICE_TRACK_ARTIST:
				self.stack.append([self.menuMode, self.menuTitle, self.iterMode])
				menu = self.sdb.getTrackArtistList()
				self.menuMode = MODE_TRACK_ARTIST
				self.iterMode = ITER_MODE_SONG
				self.sdb.setIterMode(self.iterMode)
				self.menuTitle = "Track Artists"
				self.setSubTitle(self.menuTitle)
				self.currentMenu, self.currentItem = self.mm.Descend(menu)
	
			elif value == CHOICE_TRACK:
				self.stack.append([self.menuMode, self.menuTitle, self.iterMode])
				menu = self.sdb
				self.menuMode = MODE_TRACK
				self.iterMode = ITER_MODE_SONG
				self.sdb.setIterMode(self.iterMode)
				self.menuTitle = "Tracks"
				self.setSubTitle(self.menuTitle)
				self.currentMenu, self.currentItem = self.mm.Descend(menu, offset=8)
	
			elif value == CHOICE_PLAYLIST:
				self.setSubTitle("Choose Playlist")
				self.plMgr.activate(done = PLM_DONE)
				
			elif value == CHOICE_PREFS:
				self.setPrefs.show()
			
			elif value == CHOICE_NOWPLAYING:
				if self.nowPlaying.isActive():
					self.nowPlaying.show()
			
			else:
				print "Received an unknown menu choice:", value
				self.sound('bonk')
				return
			self.sound('updown')
		
		elif keynum == KEY_ENTER:
			if value == CHOICE_NOWPLAYING:
				t = "Choose Playlist - adding %d Tracks from Now Playing list" % len(self.NPPlaylist)
				self.setSubTitle(t)	
				self.plMgr.activate(done = PLM_DONE, selectonly = True, playlist = self.NPPlaylist)
				self.sound('updown')
			
			else:
				self.sound('bonk')
				
		elif keynum == KEY_PLAY:
			if value != CHOICE_TRACK:
				self.sound('bonk')
			else:
				self.NPPlaylist.clear()
				for s in self.sdb:
					self.NPPlaylist.addSong(s)
					
				self.nowPlaying.Play(self.NPPlaylist,
									shuffle=opts['trackshuffle'],
									loop=opts['trackloop'])
				
		else:
			self.sound('bonk')
			
	def handleKeyAlbumArtist(self, keynum, rawcode):
		if keynum in [KEY_RIGHT, KEY_SELECT]:
			self.currentArtist = self.currentMenu.getMenuValue(self.currentItem)
			if self.currentArtist == None:
				self.sound('bonk')
			else:
				self.stack.append([self.menuMode, self.menuTitle, self.iterMode])
				self.menuMode = MODE_ALBUM_ARTIST_ALBUM
				self.menuTitle = "Albums by " + self.currentArtist.getArtistName()
				self.setSubTitle(self.menuTitle)
				self.iterMode = ITER_MODE_ALBUM
				self.sdb.setIterMode(self.iterMode)
				self.currentMenu, self.currentItem = self.mm.Descend(self.currentArtist, offset=8)
				self.sound('updown')
			
		else:
			self.sound('bonk')
			
	def handleKeyAlbumArtistAlbum(self, keynum, rawcode):
		if keynum in [KEY_RIGHT, KEY_SELECT]:
			self.currentAlbum = self.currentMenu.getMenuValue(self.currentItem)
			if self.currentAlbum == None:
				self.sound('bonk')
			else:
				self.stack.append([self.menuMode, self.menuTitle, self.iterMode])
				self.menuMode = MODE_ALBUM_ARTIST_ALBUM_TRACK
				self.menuTitle = ("Tracks on " + self.currentAlbum.getArtist().getArtistName() +
							" / " + self.currentAlbum.getAlbumName())
				self.setSubTitle(self.menuTitle)
				self.iterMode = ITER_MODE_ALBUM
				self.sdb.setIterMode(self.iterMode)
				self.currentMenu, self.currentItem = self.mm.Descend(self.currentAlbum, offset=8)
				self.sound('updown')
			
		elif keynum == KEY_ENTER:
			self.currentAlbum = self.currentMenu.getMenuValue(self.currentItem)
			if self.currentAlbum == None:
				self.sound('bonk')
			else:	
				t = "Choose Playlist - adding %d Tracks on from %s / %s" % (len(self.currentAlbum),
					self.currentAlbum.getArtist().getArtistName(),
					self.currentAlbum.getAlbumName())
				self.setSubTitle(t)	
				self.plMgr.activate(done = PLM_DONE, album = self.currentAlbum)
				self.sound('updown')
			
		elif keynum == KEY_PLAY:
			self.currentAlbum = self.currentMenu.getMenuValue(self.currentItem)
			if self.currentAlbum == None:
				self.sound('bonk')
			else:
				self.NPPlaylist.clear()
				for s in self.currentAlbum:
					self.NPPlaylist.addSong(s)
					
				self.nowPlaying.Play(self.NPPlaylist,
									shuffle=opts['albumshuffle'],
									loop=opts['albumloop'])
			
		else:
			self.sound('bonk')
	
	def handleKeyAlbumArtistAlbumTrack(self, keynum, rawcode):
		if keynum in [KEY_RIGHT, KEY_SELECT]:
			self.currentTrack = self.currentMenu.getMenuValue(self.currentItem)
			if self.currentTrack == None:
				self.sound('bonk')
			else:
				self.stack.append([self.menuMode, self.menuTitle, self.iterMode])
				self.menuMode = MODE_ALBUM_ARTIST_ALBUM_TRACK_CHOICES
				self.menuTitle = ""
				self.setSubTitle(self.menuTitle)
				self.iterMode = ITER_MODE_ALBUM
				self.sdb.setIterMode(self.iterMode)
				self.currentMenu, self.currentItem = self.mm.Descend(albumTrackMenu, offset=8)
				self.sound('updown')
			
		elif keynum == KEY_INFO:
			self.currentTrack = self.currentMenu.getMenuValue(self.currentItem)
			if self.currentTrack == None:
				self.app.sound('bonk')
			else:
				self.app.showLyrics(self.currentTrack)
				self.app.sound('updown')
				
		elif keynum == KEY_PLAY:
			self.currentTrack = self.currentMenu.getMenuValue(self.currentItem)
			if self.currentTrack == None:
				self.sound('bonk')
			else:
				self.NPPlaylist.clear()
				self.NPPlaylist.addSong(self.currentTrack)
				self.nowPlaying.Play(self.NPPlaylist)

				self.sound('updown')
			
		elif keynum == KEY_ENTER:
			self.currentTrack = self.currentMenu.getMenuValue(self.currentItem)
			if self.currentArtist == None or self.currentTrack == None:
				self.sound('bonk')
			else:
				t = ("Choose Playlist - adding Track %s / %s" 
					% (self.currentArtist.getArtistName(), self.currentTrack.getTitle()))
				self.setSubTitle(t)	
				self.plMgr.activate(done = PLM_DONE, song = self.currentTrack)
				self.sound('updown')
			
		else:
			self.sound('bonk')
							
	def handleKeyAlbumArtistAlbumTrackChoices(self, keynum, rawcode):
		value = self.currentMenu.getMenuValue(self.currentItem)
		if keynum in [KEY_RIGHT, KEY_SELECT]:
			if value == CHOICE_PLAY_TRACK:
				if self.currentTrack == None:
					self.sound('bonk')
				else:
					self.NPPlaylist.clear()
					self.NPPlaylist.addSong(self.currentTrack)
					self.nowPlaying.Play(self.NPPlaylist)

					self.sound('updown')
					
			elif value == CHOICE_PLAY_ALBUM:
				if self.currentAlbum == None:
					self.sound('bonk')
				else:
					self.NPPlaylist.clear()
					for s in self.currentAlbum:
						self.NPPlaylist.addSong(s)
						
					self.nowPlaying.Play(self.NPPlaylist,
										shuffle=opts['albumshuffle'],
										loop=opts['albumloop'])

					self.sound('updown')

			elif value == CHOICE_PLAY_ALBUM_TRACK:
				if self.currentAlbum == None or self.currentTrack == None:
					self.sound('bonk')
				else:
					self.NPPlaylist.clear()
					for s in self.currentAlbum:
						self.NPPlaylist.addSong(s)
						
					self.nowPlaying.Play(self.NPPlaylist, first=self.currentTrack,
										shuffle=opts['albumshuffle'],
										loop=opts['albumloop'])

					self.sound('updown')
				
			elif value == CHOICE_SONG_PLAYLIST:
				if self.currentArtist == None or self.currentTrack == None:
					self.sound('bonk')
				else:
					t = ("Choose Playlist - adding Track %s / %s" 
						% (self.currentArtist.getArtistName(), self.currentTrack.getTitle()))
					self.setSubTitle(t)	
					self.plMgr.activate(done = PLM_DONE, song = self.currentTrack)
					self.sound('updown')
					
			elif value == CHOICE_ALBUM_PLAYLIST:
				if self.currentAlbum == None or self.currentArtist == None:
					self.sound('bonk')
				else:
					t = ("Choose Playlist - adding Album %s / %s" 
						% (self.currentArtist.getArtistName(), self.currentAlbum.getAlbumName()))
					self.setSubTitle(t)	
					self.plMgr.activate(done = PLM_DONE, album = self.currentAlbum)
					self.sound('updown')
					
					
		elif keynum == KEY_INFO:
			if self.currentTrack == None:
				self.app.sound('bonk')
			else:
				self.app.showLyrics(self.currentTrack)
				self.app.sound('updown')
				
		else:
			self.sound('bonk')
					
	def handleKeyAlbum(self, keynum, rawcode):
		if keynum in [KEY_RIGHT, KEY_SELECT]:
			self.currentAlbum = self.currentMenu.getMenuValue(self.currentItem)
			if self.currentAlbum == None:
				self.sound('bonk')
			else:
				self.stack.append([self.menuMode, self.menuTitle, self.iterMode])
				self.menuMode = MODE_ALBUM_TRACK
				self.menuTitle = ("Tracks on " + self.currentAlbum.getArtist().getArtistName() +
							" / " + self.currentAlbum.getAlbumName())
				self.setSubTitle(self.menuTitle)
				self.iterMode = ITER_MODE_ALBUM
				self.sdb.setIterMode(self.iterMode)
				self.currentMenu, self.currentItem = self.mm.Descend(self.currentAlbum, offset=8)
				self.sound('updown')
			
		elif keynum == KEY_ENTER:
			self.currentAlbum = self.currentMenu.getMenuValue(self.currentItem)
			if self.currentAlbum == None:
				self.sound('bonk')
			else:	
				t = "Choose Playlist - adding %d Tracks on from %s / %s" % (len(self.currentAlbum),
					self.currentAlbum.getArtist().getArtistName(),
					self.currentAlbum.getAlbumName())
				self.setSubTitle(t)	
				self.plMgr.activate(done = PLM_DONE, album = self.currentAlbum)
				self.sound('updown')
			
		elif keynum == KEY_PLAY:
			self.currentAlbum = self.currentMenu.getMenuValue(self.currentItem)
			if self.currentAlbum == None:
				self.sound('bonk')
			else:
				self.NPPlaylist.clear()
				for s in self.currentAlbum:
					self.NPPlaylist.addSong(s)
					
				self.nowPlaying.Play(self.NPPlaylist,
										shuffle=opts['albumshuffle'],
										loop=opts['albumloop'])
			
		else:
			self.sound('bonk')

	def handleKeyAlbumTrack(self, keynum, rawcode):
		if keynum in [KEY_RIGHT, KEY_SELECT]:
			self.currentTrack = self.currentMenu.getMenuValue(self.currentItem)
			if self.currentTrack == None:
				self.sound('bonk')
			else:
				self.stack.append([self.menuMode, self.menuTitle, self.iterMode])
				self.menuMode = MODE_ALBUM_TRACK_CHOICES
				self.menuTitle = ""
				self.setSubTitle(self.menuTitle)
				self.iterMode = ITER_MODE_ALBUM
				self.sdb.setIterMode(self.iterMode)
				self.currentMenu, self.currentItem = self.mm.Descend(albumTrackMenu, offset=8)
				self.sound('updown')
			
		elif keynum == KEY_PLAY:
			self.currentTrack = self.currentMenu.getMenuValue(self.currentItem)
			if self.currentTrack == None:
				self.sound('bonk')
			else:
				self.NPPlaylist.clear()
				self.NPPlaylist.addSong(self.currentTrack)
				self.nowPlaying.Play(self.NPPlaylist)

				self.sound('updown')
					
		elif keynum == KEY_INFO:
			self.currentTrack = self.currentMenu.getMenuValue(self.currentItem)
			if self.currentTrack == None:
				self.app.sound('bonk')
			else:
				self.app.showLyrics(self.currentTrack)
				self.app.sound('updown')

		elif keynum == KEY_ENTER:
			self.currentTrack = self.currentMenu.getMenuValue(self.currentItem)
			self.currentArtist = self.currentTrack.getArtist()
			if self.currentArtist == None or self.currentTrack == None:
				self.sound('bonk')
			else:
				t = ("Choose Playlist - adding Track %s / %s" 
					% (self.currentArtist.getArtistName(), self.currentTrack.getTitle()))
				self.setSubTitle(t)	
				self.plMgr.activate(done = PLM_DONE, song = self.currentTrack)
				self.sound('updown')
			
		else:
			self.sound('bonk')
			
	def handleKeyAlbumTrackChoices(self, keynum, rawcode):
		value = self.currentMenu.getMenuValue(self.currentItem)
		if keynum in [KEY_RIGHT, KEY_SELECT]:
			if value == CHOICE_PLAY_TRACK:
				if self.currentTrack == None:
					self.sound('bonk')
				else:
					self.NPPlaylist.clear()
					self.NPPlaylist.addSong(self.currentTrack)
					self.nowPlaying.Play(self.NPPlaylist)

					self.sound('updown')

			elif value == CHOICE_PLAY_ALBUM:
				if self.currentAlbum == None:
					self.sound('bonk')
				else:
					self.NPPlaylist.clear()
					for s in self.currentAlbum:
						self.NPPlaylist.addSong(s)
						
					self.nowPlaying.Play(self.NPPlaylist,
										shuffle=opts['albumshuffle'],
										loop=opts['albumloop'])

					self.sound('updown')

			elif value == CHOICE_PLAY_ALBUM_TRACK:
				if self.currentAlbum == None or self.currentTrack == None:
					self.sound('bonk')
				else:
					self.NPPlaylist.clear()
					for s in self.currentAlbum:
						self.NPPlaylist.addSong(s)
						
					self.nowPlaying.Play(self.NPPlaylist, first=self.currentTrack,
										shuffle=opts['albumshuffle'],
										loop=opts['albumloop'])

					self.sound('updown')
				
			elif value == CHOICE_SONG_PLAYLIST:
				self.currentArtist = self.currentTrack.getArtist()
				if self.currentArtist == None or self.currentTrack == None:
					self.sound('bonk')
				else:
					t = ("Choose Playlist - adding Track %s / %s" 
						% (self.currentArtist.getArtistName(), self.currentTrack.getTitle()))
					self.setSubTitle(t)	
					self.plMgr.activate(done = PLM_DONE, song = self.currentTrack)
					self.sound('updown')
					
			elif value == CHOICE_ALBUM_PLAYLIST:
				if self.currentAlbum == None or self.currentArtist == None:
					self.sound('bonk')
				else:
					t = ("Choose Playlist - adding Album %s / %s" 
						% (self.currentArtist.getArtistName(), self.currentAlbum.getAlbumName()))
					self.setSubTitle(t)	
					self.plMgr.activate(done = PLM_DONE, album = self.currentAlbum)
					self.sound('updown')
			
		elif keynum == KEY_INFO:
			if self.currentTrack == None:
				self.app.sound('bonk')
			else:
				self.app.showLyrics(self.currentTrack)
				self.app.sound('updown')

		else:
			self.sound('bonk')
		
	def handleKeyTrackArtist(self, keynum, rawcode):
		if keynum in [KEY_RIGHT, KEY_SELECT]:
			self.currentArtist = self.currentMenu.getMenuValue(self.currentItem)
			if self.currentArtist == None:
				self.sound('bonk')
			else:
				self.stack.append([self.menuMode, self.menuTitle, self.iterMode])
				self.menuMode = MODE_TRACK_ARTIST_TRACK
				self.menuTitle = "Individual Songs by " + self.currentArtist.getArtistName()
				self.setSubTitle(self.menuTitle)
				self.iterMode = ITER_MODE_SONG
				self.sdb.setIterMode(self.iterMode)
				self.currentMenu, self.currentItem = self.mm.Descend(self.currentArtist, offset=8)
				self.sound('updown')
			
		elif keynum == KEY_ENTER:
			self.currentArtist = self.currentMenu.getMenuValue(self.currentItem)
			if self.currentArtist == None:
				self.sound('bonk')
			else:
				t = "Choose Playlist - adding %d songs by %s" %(len(self.currentArtist),
						self.currentArtist.getArtistName())				
				self.setSubTitle(t)	
				self.plMgr.activate(done = PLM_DONE, artist = self.currentArtist)
				self.sound('updown')
			
		elif keynum == KEY_PLAY:
			self.currentArtist = self.currentMenu.getMenuValue(self.currentItem)
			if self.currentArtist == None:
				self.sound('bonk')
			else:
				self.NPPlaylist.clear()
				for s in self.currentArtist:
					self.NPPlaylist.addSong(s)
				self.nowPlaying.Play(self.NPPlaylist,
										shuffle=opts['artistshuffle'],
										loop=opts['artistloop'])
			
		else:
			self.sound('bonk')
			
	def handleKeyTrackArtistTrack(self, keynum, rawcode):
		if keynum in [KEY_RIGHT, KEY_SELECT]:
			self.currentTrack = self.currentMenu.getMenuValue(self.currentItem)
			if self.currentTrack == None:
				self.sound('bonk')
			else:
				self.stack.append([self.menuMode, self.menuTitle, self.iterMode])
				self.menuMode = MODE_TRACK_ARTIST_TRACK_CHOICES
				self.menuTitle = ""
				self.setSubTitle(self.menuTitle)
				self.iterMode = ITER_MODE_SONG
				self.sdb.setIterMode(self.iterMode)
				self.currentMenu, self.currentItem = self.mm.Descend(artistTrackMenu, offset=8)
				self.sound('updown')
			
		elif keynum == KEY_PLAY:
			self.currentTrack = self.currentMenu.getMenuValue(self.currentItem)
			if self.currentTrack == None:
				self.sound('bonk')
			else:
				self.NPPlaylist.clear()
				self.NPPlaylist.addSong(self.currentTrack)
				self.nowPlaying.Play(self.NPPlaylist)
			
		elif keynum == KEY_INFO:
			self.currentTrack = self.currentMenu.getMenuValue(self.currentItem)
			if self.currentTrack == None:
				self.app.sound('bonk')
			else:
				self.app.showLyrics(self.currentTrack)
				self.app.sound('updown')

		elif keynum == KEY_ENTER:
			if self.currentArtist == None or self.currentTrack == None:
				self.sound('bonk')
			else:
				t = ("Choose Playlist - adding Track %s / %s" 
					% (self.currentArtist.getArtistName(), self.currentTrack.getTitle()))
				self.setSubTitle(t)	
				self.plMgr.activate(done = PLM_DONE, song = self.currentTrack)
				self.sound('updown')
		
		else:
			self.sound('bonk')
		
	def handleKeyTrackArtistTrackChoices(self, keynum, rawcode):
		value = self.currentMenu.getMenuValue(self.currentItem)
		if keynum in [KEY_RIGHT, KEY_SELECT]:
			if value == CHOICE_PLAY_TRACK:
				if self.currentTrack == None:
					self.sound('bonk')
				else:
					self.NPPlaylist.clear()
					self.NPPlaylist.addSong(self.currentTrack)
					self.nowPlaying.Play(self.NPPlaylist)

					self.sound('updown')
					
			elif value == CHOICE_PLAY_ARTIST:
				if self.currentArtist == None:
					self.sound('bonk')
				else:
					self.NPPlaylist.clear()
					for s in self.currentArtist:
						self.NPPlaylist.addSong(s)
					self.nowPlaying.Play(self.NPPlaylist,
										shuffle=opts['artistshuffle'],
										loop=opts['artistloop'])

					self.sound('updown')

			elif value == CHOICE_PLAY_ARTIST_TRACK:
				if self.currentArtist == None or self.currentTrack == None:
					self.sound('bonk')
				else:
					self.NPPlaylist.clear()
					for s in self.currentArtist:
						self.NPPlaylist.addSong(s)
					self.nowPlaying.Play(self.NPPlaylist, first=self.currentTrack,
										shuffle=opts['artistshuffle'],
										loop=opts['artistloop'])
					self.sound('updown')

			elif value == CHOICE_SONG_PLAYLIST:
				if self.currentArtist == None or self.currentTrack == None:
					self.sound('bonk')
				else:
					t = ("Choose Playlist - adding Track %s / %s" 
						% (self.currentArtist.getArtistName(), self.currentTrack.getTitle()))
					self.setSubTitle(t)	
					self.plMgr.activate(done = PLM_DONE, song = self.currentTrack)
					self.sound('updown')
					
			elif value == CHOICE_ARTIST_PLAYLIST:
				if self.currentArtist == None:
					self.sound('bonk')
				else:
					t = ("Choose Playlist - adding Track Artist %s" 
						% self.currentArtist.getArtistName())
					self.setSubTitle(t)	
					self.plMgr.activate(done = PLM_DONE, artist = self.currentArtist)
					self.sound('updown')
			
		elif keynum == KEY_INFO:
			if self.currentTrack == None:
				self.app.sound('bonk')
			else:
				self.app.showLyrics(self.currentTrack)
				self.app.sound('updown')
					
		else:
			self.sound('bonk')
			
	def handleKeyTrack(self, keynum, rawcode):
		if keynum in [KEY_RIGHT, KEY_SELECT]:
			self.currentTrack = self.currentMenu.getMenuValue(self.currentItem)
			if self.currentTrack == None:
				self.sound('bonk')
			else:
				self.stack.append([self.menuMode, self.menuTitle, self.iterMode])
				self.menuMode = MODE_TRACK_CHOICES
				self.menuTitle = ""
				self.setSubTitle(self.menuTitle)
				self.iterMode = ITER_MODE_SONG
				self.sdb.setIterMode(self.iterMode)
				self.currentMenu, self.currentItem = self.mm.Descend(trackMenu, offset=8)
				self.sound('updown')
				
		elif keynum in [KEY_ENTER]:
			self.currentTrack = self.currentMenu.getMenuValue(self.currentItem)
			if self.currentTrack == None:
				self.sound('bonk')
			else:
				self.currentArtist = self.currentTrack.getArtist()
				t = ("Choose Playlist - adding Track %s / %s" 
					% (self.currentArtist.getArtistName(), self.currentTrack.getTitle()))
				self.setSubTitle(t)	
				self.plMgr.activate(done = PLM_DONE, song = self.currentTrack)
				self.sound('updown')
			
		elif keynum == KEY_INFO:
			self.currentTrack = self.currentMenu.getMenuValue(self.currentItem)
			if self.currentTrack == None:
				self.app.sound('bonk')
			else:
				self.app.showLyrics(self.currentTrack)
				self.app.sound('updown')
			
		elif keynum == KEY_PLAY:
			self.currentTrack = self.currentMenu.getMenuValue(self.currentItem)
			if self.currentTrack == None:
				self.sound('bonk')
			
			self.NPPlaylist.clear()
			self.NPPlaylist.addSong(self.currentTrack)
			self.nowPlaying.Play(self.NPPlaylist)
		
		else:
			self.sound('bonk')
			
	def handleKeyTrackChoices(self, keynum, rawcode):
		value = self.currentMenu.getMenuValue(self.currentItem)
		if keynum in [KEY_RIGHT, KEY_SELECT]:
			if value == CHOICE_PLAY_TRACK:
				if self.currentTrack == None:
					self.sound('bonk')
				else:
					self.NPPlaylist.clear()
					self.NPPlaylist.addSong(self.currentTrack)
					self.nowPlaying.Play(self.NPPlaylist)

					self.sound('updown')
					
			elif value == CHOICE_SONG_PLAYLIST:
				if self.currentArtist == None or self.currentTrack == None:
					self.sound('bonk')
				else:
					t = ("Choose Playlist - adding Track %s / %s" 
						% (self.currentArtist.getArtistName(), self.currentTrack.getTitle()))
					self.setSubTitle(t)	
					self.plMgr.activate(done = PLM_DONE, song = self.currentTrack)
					self.sound('updown')
					
			elif value == CHOICE_ARTIST_PLAYLIST:
				if self.currentArtist == None:
					self.sound('bonk')
				else:
					t = ("Choose Playlist - adding Track Artist %s" 
						% self.currentArtist.getArtistName())
					self.setSubTitle(t)	
					self.plMgr.activate(done = PLM_DONE, artist = self.currentArtist)
					self.sound('updown')
					
			elif value == CHOICE_ALBUM_PLAYLIST:
				if self.currentAlbum == None or self.currentArtist == None:
					self.sound('bonk')
				else:
					t = ("Choose Playlist - adding Album %s / %s" 
						% (self.currentArtist.getArtistName(), self.currentAlbum.getAlbumName()))
					self.setSubTitle(t)	
					self.plMgr.activate(done = PLM_DONE, album = self.currentAlbum)
					self.sound('updown')

		elif keynum == KEY_INFO:
			if self.currentTrack == None:
				self.app.sound('bonk')
			else:
				self.app.showLyrics(self.currentTrack)
				self.app.sound('updown')
					
		else:
			self.sound('bonk')
			
	def setCurrentInfo(self):
		if self.menuMode in [ MODE_ALBUM_ARTIST, MODE_TRACK_ARTIST ]:
			self.currentArtist = self.currentMenu.getMenuValue(self.currentItem)
			
		elif self.menuMode in [ MODE_ALBUM, MODE_ALBUM_ARTIST_ALBUM ]:
			self.currentAlbum = self.currentMenu.getMenuValue(self.currentItem)
			
		elif self.menuMode in [ MODE_ALBUM_ARTIST_ALBUM_TRACK, MODE_ALBUM_TRACK, MODE_TRACK_ARTIST_TRACK, MODE_TRACK ]:
			self.currentTrack = self.currentMenu.getMenuValue(self.currentItem)
			
	def showDetails(self):
		if self.plMgr.isActive():
			self.detMgr.hide()
			
		elif self.menuMode in [ MODE_MAIN_MENU, MODE_ALBUM_ARTIST, MODE_TRACK_ARTIST, MODE_PREFS ]:
			self.detMgr.hide()
			return
		elif self.menuMode in [ MODE_ALBUM, MODE_ALBUM_ARTIST_ALBUM ]:
			self.detMgr.setAlbumDetail(self.currentAlbum)
			self.detMgr.show()
			return
		elif self.menuMode in [ MODE_PLAYLIST, MODE_ALBUM_ARTIST_ALBUM_TRACK, MODE_ALBUM_TRACK, MODE_TRACK_ARTIST_TRACK,
							MODE_ALBUM_ARTIST_ALBUM_TRACK_CHOICES, MODE_ALBUM_TRACK_CHOICES, MODE_TRACK_ARTIST_TRACK_CHOICES, MODE_TRACK, MODE_TRACK_CHOICES ]:
			self.detMgr.setTrackDetail(self.currentTrack)
			self.detMgr.show()
			return
		else:
			# this should never happen
			self.detMgr.hide()
			
	def handle_resource_info(self, resource, status, info):
		if self.nowPlaying.isActive():
			self.nowPlaying.handle_resource(resource, status, info)
