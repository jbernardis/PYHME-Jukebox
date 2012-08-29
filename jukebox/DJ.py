import os
import random

from hme import *

import TivoControl
from TivoControl import SELECT_TYPE_V
from Config import screenWidth, titleYPos
from DBObjects import ITER_MODE_SONG, process
from MessageBox import MessageBox

ID_CANCEL = 0
ID_ADD_NP = 1
ID_REPL_NP = 2

MKEY_DJ_COMPLETE = 100

def loadimage(app, name, skin=None):
	path = os.path.dirname(__file__)
	if skin != None:
		fn = os.path.join(path, 'skins', skin, name + ".png")
		if os.path.exists(fn):
			return Image(app, fn)
		
	fn = os.path.join(path, 'skins', name + ".png")
	if os.path.exists(fn):
		return Image(app, fn)
	
	if skin == None:
		print "image '" + name + "' missing for default skin"
	else:
		print "image '" + name + "' missing for skin '" + skin + "'"
	return None

class DJ:
	def __init__(self, app, opts):
		self.app = app
		self.sdb = app.sdb
		self.opts = opts
		self.done = None
		self.root = View(self.app, visible=False, parent = self.app.root)
		self.root.set_resource(self.app.myimages.Background)
		
		self.isactive = False
		
		skin = opts['skin']
		
		ddbkg = loadimage(app,'ddfbkg', skin)
		ddnfbkg = loadimage(app,'ddnfbkg', skin)
		btnbkg  = loadimage(app, 'fieldbkghi', skin)
		btnnfbkg = loadimage(app, 'fieldbkg', skin)
		check = loadimage(app, 'check', skin)

		
		font=self.app.myfonts.fnt30

		self.vwTitle = View(self.app, height=30, width=screenWidth, ypos=titleYPos, parent=self.root)
		self.vwTitle.set_text("Virtual DJ", font=self.app.myfonts.fnt30, colornum=0xffffff, flags=RSRC_VALIGN_BOTTOM + RSRC_HALIGN_CENTER)
		
		self.vwArtist = View(self.app, height=40, width=190, xpos= 50, ypos=60, parent=self.root)
		self.vwArtist.set_text("Choose Artist(s)", font=self.app.myfonts.fnt30, colornum=0xffffff, flags=RSRC_HALIGN_LEFT)
		self.tcArtist = TivoControl.DropDown(self.app, xpos=50, ypos=100, parent=self.root, rows=5, rowHeight=40, width=300,
				 imageFocus=ddbkg, imageNoFocus=ddnfbkg, imageCheck=check, checkWidth=32, leftOffset=20, rightOffset=10, font=font,
				 data=[], flags=RSRC_HALIGN_LEFT, ignorecase=self.opts['ignorecase'])
		self.vwGenre = View(self.app, height=40, width=190, xpos= 650, ypos=60, parent=self.root)
		self.vwGenre.set_text("Choose Genre", font=self.app.myfonts.fnt30, colornum=0xffffff, flags=RSRC_HALIGN_LEFT)
		self.tcGenre = TivoControl.DropDown(self.app, xpos=650, ypos=100, parent=self.root, rows=5, rowHeight=40, width=300,
				 imageFocus=ddbkg, imageNoFocus=ddnfbkg, imageCheck=check, checkWidth=32, leftOffset=20, rightOffset=10, font=font,
				 data=[], flags=RSRC_HALIGN_LEFT, ignorecase=self.opts['ignorecase'])
		
		self.tcIncludeArtist = TivoControl.CheckBox(self.app, xpos=50, ypos=400, parent=self.root, height=40, width=160,
				 imageCheckFocus=btnbkg, imageCheckNoFocus=btnnfbkg,
				 leftOffset=0, rightOffset=0, font=font, text="Exclude", textCheck = "Include", initialState=True,
				 colornum=0xffffff, flags=0)
		self.vwIncludeArtist = View(self.app, height=120, width=350, xpos= 220, ypos=400, parent=self.root)
		
		self.tcIncludeGenre = TivoControl.CheckBox(self.app, xpos=650, ypos=400, parent=self.root, height=40, width=160,
				 imageCheckFocus=btnbkg, imageCheckNoFocus=btnnfbkg,
				 leftOffset=0, rightOffset=0, font=font, text="Exclude", textCheck = "Include", initialState=True,
				 colornum=0xffffff, flags=0)
		self.vwIncludeGenre = View(self.app, height=120, width=350, xpos=820, ypos=400, parent=self.root)

		self.tcCount = TivoControl.Select(self.app, xpos=120, ypos=540, parent=self.root, height=40, width=160, listType=SELECT_TYPE_V,
				 imageFocus=btnbkg, imageNoFocus=btnnfbkg, leftOffset=0, rightOffset=0, font=font,
				 data=["10", "20", "30", "40", "50", "60", "70", "80", "90", "100", "150", "200"])
		self.vwCount = View(self.app, height=40, width=190, xpos= 320, ypos=540, parent=self.root)
		self.vwCount.set_text("number of tracks", font=self.app.myfonts.fnt30, colornum=0xffffff, flags=RSRC_HALIGN_LEFT)

		self.tcAddNP = TivoControl.Button(self.app, self, xpos=520, ypos=540, parent=self.root, height=40, width=160,
				 imageFocus=btnbkg, imageNoFocus=btnnfbkg, leftOffset=0, rightOffset=0, font=font, text="Add",
				 colornum=0xffffff, flags=0, ID=ID_ADD_NP)
		self.vwAdd = View(self.app, height=40, width=350, xpos= 690, ypos=540, parent=self.root)
		self.vwAdd.set_text("to Now Playing list", font=self.app.myfonts.fnt30, colornum=0xffffff, flags=RSRC_HALIGN_LEFT)
		self.tcReplNP = TivoControl.Button(self.app, self, xpos=520, ypos=600, parent=self.root, height=40, width=160,
				 imageFocus=btnbkg, imageNoFocus=btnnfbkg, leftOffset=0, rightOffset=0, font=font, text="Replace",
				 colornum=0xffffff, flags=0, ID=ID_REPL_NP)
		self.vwRepl = View(self.app, height=40, width=350, xpos= 690, ypos=600, parent=self.root)
		self.vwRepl.set_text("Now Playing list", font=self.app.myfonts.fnt30, colornum=0xffffff, flags=RSRC_HALIGN_LEFT)

		self.tcCancel = TivoControl.Button(self.app, self, xpos=520, ypos=690, parent=self.root, height=40, width=160,
				 imageFocus=btnbkg, imageNoFocus=btnnfbkg, leftOffset=0, rightOffset=0, font=font, text="Cancel",
				 colornum=0xffffff, flags=0, ID=ID_CANCEL)

		self.cc = TivoControl.ControlContext(self.app)
		self.cc.addControl(self.tcArtist, tabUp=None, tabDown=self.tcIncludeArtist, tabLeft=None, tabRight=self.tcGenre)
		self.cc.addControl(self.tcGenre, tabUp=None, tabDown=self.tcIncludeGenre, tabLeft=self.tcArtist, tabRight=self.tcIncludeArtist)
		
		self.cc.addControl(self.tcIncludeArtist, tabUp=self.tcArtist, tabDown=self.tcCount, tabLeft=self.tcGenre, tabRight=self.tcIncludeGenre)
		self.cc.addControl(self.tcIncludeGenre, tabUp=self.tcGenre, tabDown=self.tcCount, tabLeft=self.tcIncludeArtist, tabRight=self.tcCount)
		
		self.cc.addControl(self.tcCount, tabUp=self.tcIncludeArtist, tabDown=self.tcCancel, tabLeft=self.tcIncludeGenre, tabRight=self.tcAddNP)
		self.cc.addControl(self.tcAddNP, tabUp=self.tcIncludeArtist, tabDown=self.tcReplNP, tabLeft=self.tcCount, tabRight=self.tcReplNP)
		self.cc.addControl(self.tcReplNP, tabUp=self.tcAddNP, tabDown=self.tcCancel, tabLeft=self.tcAddNP, tabRight=self.tcCancel)

		self.cc.addControl(self.tcCancel, tabUp=self.tcReplNP, tabDown=None, tabLeft=self.tcReplNP, tabRight=None)
		
	def isActive(self):
		return self.isactive
	
	def show(self, done=None):
		self.done = done
		self.artistNames = []
		self.sArtistNames = []
		self.artistHandles = []	
		genreMap = {}
		self.sdb.setIterMode(ITER_MODE_SONG)	
		tal = self.sdb.getTrackArtistList()
		for a in tal:
			self.artistNames.append(a.getArtistName())
			self.sArtistNames.append(process(a.getArtistName()))
			self.artistHandles.append(a)
			for s in a:
				genreMap[s.getGenre()] = 1

		self.genreNames = sorted(genreMap.keys())
		
		self.tcArtist.setData(self.artistNames, self.sArtistNames)
		self.tcGenre.setData(self.genreNames, None)
		
		self.tcArtist.reset()
		self.tcGenre.reset()
		self.tcCount.reset()
		self.tcIncludeArtist.reset()
		self.tcIncludeGenre.reset()
		
		self.updateText()
		
		self.root.set_visible(True)
		self.isactive = True
		self.cc.startSession()
		
	def updateText(self):
		incArt = self.tcIncludeArtist.getState();
		xArt = self.tcArtist.getSelection()
		nArt = len(xArt)
		if nArt > 0:
			text = ""
			for i in range(nArt):
				if text != "":
					text += ", "
				text += self.artistNames[xArt[i]]
			font = self.app.myfonts.fnt20
		else:
			if incArt:
				text = "ALL artists"
			else:
				text = "NO artists"
			font = self.app.myfonts.fnt30
			
		self.vwIncludeArtist.set_text(text, font=font, colornum=0xffffff, flags=RSRC_HALIGN_LEFT + RSRC_VALIGN_TOP + RSRC_TEXT_WRAP)
			
		incGen = self.tcIncludeGenre.getState();
		xGen = self.tcGenre.getSelection()
		nGen = len(xGen)
		if nGen > 0:
			text = ""
			for i in range(nGen):
				if text != "":
					text += ", "
				text += self.genreNames[xGen[i]]
			font = self.app.myfonts.fnt20
		else:
			if incGen:
				text = "ALL genre"
			else:
				text = "NO genre"
			font = self.app.myfonts.fnt30
		self.vwIncludeGenre.set_text(text, font=font, colornum=0xffffff, flags=RSRC_HALIGN_LEFT + RSRC_VALIGN_TOP + RSRC_TEXT_WRAP)
		pass
		
	def hide(self):
		self.root.set_visible(False)
		self.isactive = False
		self.cc.endSession()
		if self.done:
			self.app.send_key(KEY_TIVO, self.done)
			
	def handle_key_press(self, keynum, rawcode):
		if not self.isactive:
			return False

		if keynum == KEY_TIVO and rawcode == MKEY_DJ_COMPLETE:
			self.hide()
			return True
		
		if keynum == KEY_CLEAR:
			self.hide();
			return True
			
		if self.cc.handle_key_press(keynum, rawcode):
			self.updateText()
			return True
			
		return False
	
	def buttonPress(self, id):
		def cmpRandom(a, b):
			return cmp(a.randkey, b.randkey)
		
		if id in [ ID_ADD_NP, ID_REPL_NP ]:
			
			incArt = self.tcIncludeArtist.getState()
			lArt = self.tcArtist.getSelection()
			incGen = self.tcIncludeGenre.getState()
			lGenx = self.tcGenre.getSelection()
			lGen = []
			for i in lGenx:
				lGen.append(self.genreNames[i])
			
			matchSongs = []
			index = 0
			
			self.sdb.setIterMode(ITER_MODE_SONG)	
			for a in self.artistHandles:
				useArtist = False
				if index in lArt and incArt:
					useArtist = True
				elif index not in lArt and not incArt:
					useArtist = True
				elif len(lArt) == 0:
					useArtist = True
					
				index += 1
					
				if useArtist:
					for s in a:
						if incGen and (s.getGenre() in lGen):
							matchSongs.append(s)
						elif not incGen and (s.getGenre() not in lGen):
							matchSongs.append(s)
						elif len(lGen) == 0:
							matchSongs.append(s)
			try:
				ct = int(self.tcCount.getSelection()[1])
			except:
				ct = 0
			text = ""
			if ct > len(matchSongs):
				text = "Requested songs (%d) greater than matching songs (%d)\n" % (ct, len(matchSongs))
				ct = len(matchSongs)
				
			if ct != 0 and len(matchSongs) != 0:
				for s in matchSongs:
					s.randkey = random.randint(0, 10000)
					
				s = sorted(matchSongs, cmpRandom)
					
				matchSongs = s[:ct]
				
				clearNP = False
			
				if id == ID_REPL_NP:
					clearNP = True
					self.app.nowPlaying.deactivate()
					text += "Replaced Now Playing list with %d random tracks" % ct
				else:
					text += "Added %d random tracks to Now Playing list" % ct
					
				text += "\n\nPress any key to continue"
					
				for s in matchSongs:
					self.app.addToNowPlaying(clear=clearNP, song=s)
					clearNP = False
				
				if not self.app.nowPlaying.isActive():
					self.app.nowPlaying.Play(self.app.NPPlaylist,
								shuffle=self.opts['playlistshuffle'],
								loop=self.opts['playlistloop'])
					
				MessageBox(self.app, "Virtual DJ", text, None,
									[[[], MKEY_DJ_COMPLETE]])


			else:
				MessageBox(self.app, "Virtual DJ", "There were no matching songs", None,
									[[[], MKEY_DJ_COMPLETE]])
				
		else:
			self.hide()