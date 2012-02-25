from hme import *
import os
from Config import screenHeight, screenWidth, lyricHeight, lyricWidth
from GetLyrics import GetLyrics


class LyricView(View):
	def __init__(self, app):
		xpos = (screenWidth-lyricWidth)/2
		ypos = (screenHeight-lyricHeight)/2

		View.__init__(self, app, width=lyricWidth, height=lyricHeight, xpos=xpos, ypos=ypos, visible=False)
		self.set_resource(app.myimages.LyricBG)
		self.linesPerPage = 0
		self.lineCount = 0
		self.displayOffset = 0
		self.app = app
		self.font = app.myfonts.fnt24
		self.lineHeight = 24
		opts = app.opts
		if opts['lyricindent'] == -1:
			self.flags = RSRC_HALIGN_CENTER
			lIndent = 10
		else:
			self.flags = RSRC_HALIGN_LEFT
			lIndent = 50 + opts['lyricindent']

		self.lView = []
		y = 54
		while (y + self.lineHeight <= lyricHeight - 28):
			v = View(self.app, parent=self, width=lyricWidth-lIndent, height=self.lineHeight, xpos=lIndent, ypos=y)
			self.lView.append(v)
			y = y + self.lineHeight
			self.linesPerPage = self.linesPerPage + 1
			
		self.vwSong = View(self.app, parent=self, width=lyricWidth-lIndent-5, height=24, xpos=10, ypos=2)
		self.vwArtist = View(self.app, parent=self, width=lyricWidth-lIndent-5, height=20, xpos=10, ypos=30)
		self.vwCredits = View(self.app, parent=self, width=lyricWidth-lIndent-5, height=20, xpos=10, ypos=lyricHeight-24)
		
		self.vwUp = View(self.app, parent=self, width=32, height=16, xpos=24, ypos=53)
		self.vwUp.set_resource(self.app.myimages.LyricUp)
		self.vwDown = View(self.app, parent=self, width=32, height=16, xpos=24, ypos=lyricHeight-43)
		self.vwDown.set_resource(self.app.myimages.LyricDown)

		self.hide()
		
	def show(self):
		self.clear_resource()
		self.set_resource(self.app.myimages.LyricBG)
		self.isVisible = True
		self.set_visible(True)
		
	def isShowing(self):
		return self.isVisible
		
	def hide(self):
		self.isVisible = False
		self.set_visible(False)
		
	def clear(self):
		self.content = []
		self.lineCount = 0
		self.displayOffset = 0
		
	def loadLyrics(self, song):
		self.song = song
		self.vwSong.set_text(song.getTitle(), font=self.app.myfonts.fnt24, colornum=0xffffff, flags=self.flags)
		self.vwArtist.set_text(song.getArtistName(), font=self.app.myfonts.fnt20, colornum=0xffffff, flags=self.flags)
		
		lyrFile = os.path.splitext(song.getFile())[0] + '.lyr'
		if os.path.exists(lyrFile):
			self.lyrString = file(lyrFile).read()
			self.vwCredits.set_text("Lyrics from local file " + lyrFile + " ", font=self.app.myfonts.fnt20, colornum=0xffffff, flags=RSRC_HALIGN_RIGHT)

		else:
			self.lyrString = GetLyrics(song.getArtistName(), song.getTitle())
		
			if self.lyrString == None:
				self.lyrString = ""
				self.vwCredits.set_text("Unable to retrieve lyrics ", font=self.app.myfonts.fnt20, colornum=0xffffff, flags=RSRC_HALIGN_RIGHT)
			else:
				self.vwCredits.set_text("Lyrics provided by azlyrics.com ", font=self.app.myfonts.fnt20, colornum=0xffffff, flags=RSRC_HALIGN_RIGHT)
		
		lyrics = self.lyrString.split("\n")
			
		self.clear()
		for l in lyrics:
			self.content.append(l)
			self.lineCount += 1
		self.paint()
		self.show()
		
	def paint(self):
		if self.displayOffset == 0:
			self.vwUp.set_visible(False)
		else:
			self.vwUp.set_visible(True)
			
		if self.displayOffset + self.linesPerPage >= self.lineCount:
			self.vwDown.set_visible(False)
		else:
			self.vwDown.set_visible(True)
			
		i = 0
		while i < self.linesPerPage:
			n = self.displayOffset + i
			if n >= self.lineCount:
				self.lView[i].set_text("")
			else:
				self.lView[i].set_text(self.content[n],
					font=self.font,
					colornum=0xffffff,
					flags=self.flags)
			i = i + 1
	
	def pagedown(self):
		if self.displayOffset + self.linesPerPage >= self.lineCount:
			return False
		
		self.displayOffset = self.displayOffset + self.linesPerPage
		if self.displayOffset + self.linesPerPage > self.lineCount:
			self.displayOffset = self.lineCount - self.linesPerPage
		self.paint()
		return True
	
	def pageup(self):
		if self.displayOffset == 0:
			return False;
		
		self.displayOffset = self.displayOffset - self.linesPerPage
		if self.displayOffset < 0:
			self.displayOffset = 0
		self.paint()
		return True
	
	def handle_key_press(self, keynum, rawcode):
		snd = 'updown'
		if keynum in [ KEY_UP, KEY_CHANNELUP ]:
			if not self.pageup():
				snd = 'bonk'
		elif keynum in [ KEY_DOWN, KEY_CHANNELDOWN ]:
			if not self.pagedown():
				snd = 'bonk'
		elif keynum in [ KEY_LEFT, KEY_INFO, KEY_CLEAR ]:
			self.hide()
		elif keynum == KEY_THUMBSUP:
			try:
				lyrFile = os.path.splitext(self.song.getFile())[0] + '.lyr'
				f = open(lyrFile, 'w')
				f.write(self.lyrString)
				f.close()
					
				self.vwCredits.set_text("Lyrics saved to local file " + lyrFile + " ", font=self.app.myfonts.fnt20, colornum=0xffffff, flags=RSRC_HALIGN_RIGHT)
				snd = 'alert'
				
			except:
				snd = 'bonk'

		else:
			snd = 'bonk'
			
		self.app.sound(snd)
		

