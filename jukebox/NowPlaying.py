from hme import *
import os
import urllib
import random

from Config import (artHeight, artWidth, npArtY, npArtX, npInfoX, npInfoY, npCursorWidth, messageYPos,
				npItemHeight, npLabelWidth, npValueWidth, npCounterY, npProgHeight, npProgressY)

if os.path.sep == '/':
	quote = urllib.quote
	unquote = urllib.unquote_plus
else:
	quote = lambda x: urllib.quote(x.replace(os.path.sep, '/'))
	unquote = lambda x: os.path.normpath(urllib.unquote_plus(x))
	
		
	
class NowPlaying:
	def __init__(self, app):
		self.app = app
		self.sdb = app.sdb
		self.playlist = []
		self.containers = self.app.opts['containers']
		self.active = False
		self.showing = False
		self.originalPlaylist = None
		self.root = View(self.app, visible=False, parent=self.app.root)
		self.root.set_resource(self.app.myimages.NPBackground)
		
		self.images = [ self.app.myimages.RW3, self.app.myimages.RW2, self.app.myimages.RW1, self.app.myimages.Play,
				self.app.myimages.FF1, self.app.myimages.FF2, self.app.myimages.FF3 ]
		self.speeds = [ -12.0, -6.0, -3.0, 1.0, 3.0, 6.0, 12.0 ]
		self.sounds = [ 'speedup3', 'speedup2', 'speedup1', 'updown', 'speedup1', 'speedup2', 'speedup3' ]
		
		self.server_host = self.app.opts['serverip']
		self.server_port = self.app.opts['serverport']
		print "Server address = %s:%s" % (self.server_host, self.server_port)
		self.NPStream = None
		
		self.paused = False
		self.seeking = False
		self.speed = 0.0
		self.speedindex = 3
		self.position = 0
		self.playingSong = None
		
		self.vwAlbumArt = View(self.app, height=artHeight, width=artWidth, ypos=npArtY, xpos=npArtX, parent=self.root)

		y = npInfoY
		xv = npInfoX+npLabelWidth+10
		self.vwTrackLabel = View(self.app, height=npItemHeight, width=npLabelWidth, ypos=y, xpos=npInfoX, parent=self.root)
		self.vwTrackValue = View(self.app, height=npItemHeight, width=npValueWidth, ypos=y, xpos=xv, parent=self.root)
		y += npItemHeight + 10
		self.vwAlbumLabel = View(self.app, height=npItemHeight, width=npLabelWidth, ypos=y, xpos=npInfoX, parent=self.root)
		self.vwAlbumValue = View(self.app, height=npItemHeight, width=npValueWidth, ypos=y, xpos=xv, parent=self.root)
		y += npItemHeight + 10
		self.vwArtistLabel = View(self.app, height=npItemHeight, width=npLabelWidth, ypos=y, xpos=npInfoX, parent=self.root)
		self.vwArtistValue = View(self.app, height=npItemHeight, width=npValueWidth, ypos=y, xpos=xv, parent=self.root)
		y += npItemHeight + 10
		self.vwNextLabel = View(self.app, height=npItemHeight, width=npLabelWidth, ypos=y, xpos=npInfoX, parent=self.root)
		self.vwNextValue = View(self.app, height=npItemHeight, width=npValueWidth, ypos=y, xpos=xv, parent=self.root)

		w = npLabelWidth * 2
		self.vwCounter = View(self.app, height=2*npItemHeight, width=w, ypos=npCounterY, xpos=npInfoX, parent=self.root)

		self.vwProgress = View(self.app, height=npProgHeight, ypos=npProgressY, xpos=0, parent=self.root)
		self.vwProgress.set_resource(self.app.myimages.ProgressBkg)
		
		self.vwCursor = View(self.app, height=npProgHeight, ypos=0, xpos=0, width=npCursorWidth, parent=self.vwProgress)
		self.vwCursor.set_resource(self.app.myimages.NPCursor)
		self.vwCurrent = View(self.app, height=int(npProgHeight/2), ypos=2, xpos=0, width=70, parent=self.vwCursor)
		self.vwMotion  = View(self.app, height=22, ypos=10, xpos=80, width=28, parent=self.vwCursor)
		
		self.vwProgFrame = View(self.app, parent=self.vwProgress)
		self.vwProgFrame.set_resource(self.app.myimages.ProgressBar)
		self.vwProgZero = View(self.app, height=npProgHeight-7, ypos=0, xpos=40, width=100, parent=self.vwProgFrame)
		self.vwProgZero.set_text("0:00   ", font=self.app.myfonts.fnt20, colornum=0xffffff, flags=RSRC_HALIGN_RIGHT + RSRC_VALIGN_BOTTOM)
		self.vwProgDur = View(self.app, height=npProgHeight-7, ypos=0, xpos=1160, width=100, parent=self.vwProgFrame)
		
		self.vwMessage= View(self.app, height=40, ypos=messageYPos, parent=self.root)
		
	def show(self):
		self.root.set_visible(True)
		self.showing = True
		
	def hide(self):
		self.root.set_visible(False)
		self.showing = False
		
	def isShowing(self):
		return self.showing
	
	def activate(self):
		if not self.active:
			self.active = True
			self.app.updateMenus(True)
		
	def deactivate(self):
		if self.active:
			self.active = False
			self.app.updateMenus(False)
			
	def cleanup(self):
		if self.NPStream:
			self.NPStream.__del__()
			self.NPStream = None

	def isActive(self):
		return self.active
	
	def Play(self, pl, shuffle=False, repeat=False, loop=False, first=None):
		self.originalPlaylist = pl
			
		self.shuffle = shuffle
		self.repeat = repeat
		self.loop = loop

		self.buildPlayList(first=first)			
				
		self.vwMotion.set_resource(self.app.myimages.Play)
		self.PlaySong()
		self.activate()
		self.show()
	
	def buildPlayList(self, first=None):
		def cmpShuffle(a, b):
			return random.choice([-1, 1])
	
		self.playlist = []
		for s in self.originalPlaylist:
			self.playlist.append(s)
			
		if self.shuffle:
			s = sorted(self.playlist, cmpShuffle)
			self.playlist = s

		self.index = 0
		if first:
			while self.index < len(self.playlist) and self.playlist[self.index].id != first.id:
				self.index += 1
				
			if self.index >= len(self.playlist):
				self.index = 0
		
	def PlaySong(self):
		self.cleanup()
			
		self.playingSong = self.playlist[self.index]
		# zero out time display
		# create the stream resource
		fn = self.playingSong.getFile()
		
		# figure out which container it's in
		for c, d in self.containers:
			if fn.startswith(d):
				f = fn[len(d):]
				if f.startswith(os.sep):
					f = f[1:]
				fn = os.path.join(c, f)
				break

		if fn.startswith(os.sep):
			fn = fn[1:]
			
		url = "http://%s:%s/%s" % (self.server_host, self.server_port, quote(fn))

		self.speedindex = 3
		self.position = 0
		self.speed = 1.0
		self.paused = False
		self.duration = self.playingSong.getLength()
	
		self.determineNext()	
		
		self.showTrackDetails(self.playingSong)
		self.NPStream = Stream(self.app, url, mime='audio/mpeg', play=True)
		
	def showTrackDetails(self, track):
		album = track.getAlbum()
		art = album.getArt()
		if art:
			self.vwAlbumArt.set_resource(Image(self.app, data=art), flags=RSRC_VALIGN_TOP+RSRC_HALIGN_LEFT)
		else:
			self.vwAlbumArt.set_resource(self.app.myimages.DefaultArt)

		self.vwTrackLabel.set_text("Track Title:", font=self.app.myfonts.fnt30, colornum=0xffffff, flags=RSRC_HALIGN_RIGHT)
		self.vwTrackValue.set_text(track.getTitle(), font=self.app.myfonts.fnt30, colornum=0xffffff, flags=RSRC_HALIGN_LEFT)

		self.vwAlbumLabel.set_text("Album:", font=self.app.myfonts.fnt30, colornum=0xffffff, flags=RSRC_HALIGN_RIGHT)
		self.vwAlbumValue.set_text(album.getAlbumName(), font=self.app.myfonts.fnt30, colornum=0xffffff, flags=RSRC_HALIGN_LEFT)

		self.vwArtistLabel.set_text("Artist:", font=self.app.myfonts.fnt30, colornum=0xffffff, flags=RSRC_HALIGN_RIGHT)
		self.vwArtistValue.set_text(album.getArtistName(), font=self.app.myfonts.fnt30, colornum=0xffffff, flags=RSRC_HALIGN_LEFT)
			
		s = "%d:%02d" % (int(self.duration/60), self.duration % 60)
		self.vwProgDur.set_text(s, font=self.app.myfonts.fnt20, colornum=0xffffff, flags=RSRC_HALIGN_LEFT + RSRC_VALIGN_BOTTOM)
		
		self.showCurrentTrackTime()

		self.showOptionStatus()

	def showCurrentTrackTime(self):
		pos = int(self.position / 1000)
		s = "%d:%02d" % (int(pos/60), pos % 60)
		self.vwCurrent.set_text(s, font=self.app.myfonts.fnt20, colornum=0xffffff, flags=RSRC_HALIGN_RIGHT)
		
		cpos = int((float(self.position) / (float(self.duration) * 1000.0)) * 1000.0) + 140 - int(npCursorWidth/2)
		self.vwCursor.set_bounds(xpos=cpos)
		
	def showOptionStatus(self):
		s = "%d/%d" % (self.index+1, len(self.playlist))
		self.vwCounter.set_text(s, font=self.app.myfonts.fnt30, colornum=0xffffff, flags=RSRC_HALIGN_CENTER)
		
		if self.next:
			nextAlbum = self.next.getAlbum()
			s = "%s / %s" % (nextAlbum.getArtistName(), self.next.getTitle())
			self.vwNextLabel.set_text("Next:", font=self.app.myfonts.fnt30, colornum=0xffffff, flags=RSRC_HALIGN_RIGHT)
			self.vwNextValue.set_text(s, font=self.app.myfonts.fnt30, colornum=0xffffff, flags=RSRC_HALIGN_LEFT)
		else:
			self.vwNextLabel.set_text("", font=self.app.myfonts.fnt30, colornum=0xffffff, flags=RSRC_HALIGN_RIGHT)
			self.vwNextValue.set_text("", font=self.app.myfonts.fnt30, colornum=0xffffff, flags=RSRC_HALIGN_LEFT)
			
		def onOrOff(flag):
			if flag:
				return "on"
			else:
				return "off"
			
		s = "Shuffle(1): %s     Repeat(2): %s     Loop(3): %s" %(
						onOrOff(self.shuffle), onOrOff(self.repeat), onOrOff(self.loop))
		
		self.vwMessage.set_text(s, font=self.app.myfonts.fnt30, colornum=0xffffff, flags=RSRC_HALIGN_CENTER)

	def addToNowPlaying(self, album=None, artist=None, song=None, playlist=None):
		changes = False
		
		if song:
			self.playlist.append(song)
			changes = True
			
		if album:
			for s in album:
				self.playlist.append(s)
			changes = True
			
		if playlist:
			for s in playlist:
				self.playlist.append(s)
			changes = True
			
		if artist:
			for s in artist:
				self.playlist.append(s)
			changes = True
	
		if changes and self.playingSong:
			self.determineNext()
			self.showTrackDetails(self.playingSong)

	def handle_resource(self, resource, status, info):
		if self.NPStream == None:
			return
		
		if self.NPStream.id != resource:
			return
		
		if status == RSRC_STATUS_PLAYING:
			if 'position' in info:
				self.position = int(info['position'])
				if self.seeking:
					self.seeking = False
				self.showCurrentTrackTime()
		
		if status == RSRC_STATUS_SEEKING:
			if 'position' in info:
				self.seeking = True
				self.position = int(info['position'])
				if self.position > (self.duration * 1000.0):
					self.goToNext()
				else:
					self.showCurrentTrackTime()
		
		elif status == RSRC_STATUS_PAUSED:
			# update image on screen
			pass
		
		elif status in [ RSRC_STATUS_CLOSED, RSRC_STATUS_COMPLETE ]:
			self.goToNext()
			
	def goToNext(self):
		self.NPStream.__del__()
		self.NPStream = None
		
		if not self.repeat:
			self.index += 1
			if self.index >= len(self.playlist):
				if self.loop:
					self.index = 0
				else:
					# we are done with the playlist
					self.playingSong = None
					self.deactivate()
					self.hide()
					return
				
		self.PlaySong()

	def determineNext(self):
		if self.repeat:
			self.next = None
		else:			
			if self.index == len(self.playlist)-1:
				if self.loop:
					self.next = self.playlist[0]
				else:
					self.next = None
			else:
				self.next = self.playlist[self.index+1]

			
	def handle_key_press(self, keynum, rawcode):
		if keynum == KEY_LEFT:
			self.hide()
			
		elif keynum == KEY_PAUSE:
			if self.NPStream:
				if self.paused:
					self.vwMotion.set_resource(self.app.myimages.Play)
					self.speed = 1.0
					self.speedindex = 3
					self.paused = False
				else:
					self.vwMotion.set_resource(self.app.myimages.Pause)
					self.speed = 0.0
					self.speedindex = 3
					self.paused = True
					
				self.NPStream.set_speed(self.speed)
				
		elif keynum == KEY_PLAY:
			if self.NPStream:
				self.vwMotion.set_resource(self.app.myimages.Play)
				self.speed = 1.0
				self.paused = False
				self.speedindex = 3
				self.NPStream.set_speed(self.speed)
				self.app.sound('updown')
				
		elif keynum == KEY_NUM1:
			self.shuffle = not self.shuffle
			self.buildPlayList(first=self.playingSong)
			self.determineNext()
			self.showOptionStatus()
			self.app.sound('updown')
		
		elif keynum == KEY_NUM2:
			self.repeat = not self.repeat
			self.determineNext()
			self.showOptionStatus()
			self.app.sound('updown')
			
		elif keynum == KEY_NUM3:
			self.loop = not self.loop
			self.determineNext()
			self.showOptionStatus()
			self.app.sound('updown')
		
		elif keynum in [ KEY_CHANNELUP, KEY_ADVANCE ]:
			self.NPStream.__del__()
			self.NPStream = None
			
			self.index += 1
			if self.index >= len(self.playlist):
				self.index = 0
					
			self.PlaySong()
			self.app.sound('updown')
			
		elif keynum in [ KEY_CHANNELDOWN, KEY_REPLAY ]:
			self.NPStream.__del__()
			self.NPStream = None
			if self.position < 5000:
				self.index -= 1
				if self.index < 0:
					self.index = len(self.playlist)-1
					
			self.PlaySong()
			self.app.sound('updown')
			
		elif keynum == KEY_FORWARD:
			self.speedindex += 1
			if self.speedindex >= len(self.speeds):
				self.speedindex = 3
				
			self.speed = self.speeds[self.speedindex]
			self.NPStream.set_speed(self.speed)
			self.app.sound(self.sounds[self.speedindex])
			self.vwMotion.set_resource(self.images[self.speedindex])
		
		elif keynum == KEY_REVERSE:
			self.speedindex -= 1
			if self.speedindex < 0:
				self.speedindex = 3
				
			self.speed = self.speeds[self.speedindex]
			self.NPStream.set_speed(self.speed)
			self.app.sound(self.sounds[self.speedindex])
			self.vwMotion.set_resource(self.images[self.speedindex])

