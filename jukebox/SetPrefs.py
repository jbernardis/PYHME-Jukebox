from hme import *

from Config import screenWidth, titleYPos, subTitleYPos

POS_SAVE = 100
POS_CANCEL = 101

lefts = [ -1, 0, -1, 2, -1, 4, -1, 6 ]
rights = [ 1, -1, 3, -1, 5, -1, 7, -1 ]
ups = [ -1, -1, 0, 1, 2, 3, 4, 5 ]
downs = [ 2, 3, 4, 5, 6, 7, POS_SAVE, POS_CANCEL ]

xPos = [ 485, 735, 485, 735, 485, 735, 485, 735 ]
yPos = [ 160, 160, 240, 240, 320, 320, 400, 400 ]

yCmd = 560

keys = [ 
	'albumshuffle',	'albumloop',
	'artistshuffle', 'artistloop',
	'playlistshuffle', 'playlistloop',
	'trackshuffle' , 'trackloop' ]

class SetPrefs:
	def __init__(self, app):
		self.app = app
		self.root = View(self.app, visible=False, parent = self.app.root)
		self.root.set_resource(self.app.myimages.Background)
		
		self.isactive = False
		self.position = 0
		
		self.vwTitle = View(self.app, height=30, width=screenWidth, ypos=titleYPos, parent=self.root)
		self.vwTitle.set_text("Set Preferences", font=self.app.myfonts.fnt30, colornum=0xffffff, flags=RSRC_VALIGN_BOTTOM + RSRC_HALIGN_CENTER)
		
		self.vwLabelAlbum = View(self.app, height=30, width=300, ypos=160, parent=self.root)
		self.vwLabelAlbum.set_text("Album:", font=self.app.myfonts.fnt30, colornum=0xffffff, flags=RSRC_VALIGN_CENTER + RSRC_HALIGN_RIGHT)
		self.vwLabelArtist = View(self.app, height=30, width=300, ypos=240, parent=self.root)
		self.vwLabelArtist.set_text("Artist:", font=self.app.myfonts.fnt30, colornum=0xffffff, flags=RSRC_VALIGN_CENTER + RSRC_HALIGN_RIGHT)
		self.vwLabelPlaylist = View(self.app, height=30, width=300, ypos=320, parent=self.root)
		self.vwLabelPlaylist.set_text("Playlist:", font=self.app.myfonts.fnt30, colornum=0xffffff, flags=RSRC_VALIGN_CENTER + RSRC_HALIGN_RIGHT)
		self.vwLabelTrack = View(self.app, height=30, width=300, ypos=400, parent=self.root)
		self.vwLabelTrack.set_text("Track:", font=self.app.myfonts.fnt30, colornum=0xffffff, flags=RSRC_VALIGN_CENTER + RSRC_HALIGN_RIGHT)

		self.vwLabelShuffle = View(self.app, height=30, width=160, ypos=100, xpos=485, parent=self.root)
		self.vwLabelShuffle.set_text("Shuffle", font=self.app.myfonts.fnt30, colornum=0xffffff, flags=RSRC_VALIGN_CENTER + RSRC_HALIGN_CENTER)
		self.vwLabelLoop = View(self.app, height=30, width=160, ypos=100, xpos=735, parent=self.root)
		self.vwLabelLoop.set_text("Loop", font=self.app.myfonts.fnt30, colornum=0xffffff, flags=RSRC_VALIGN_CENTER + RSRC_HALIGN_CENTER)

		self.vwFldBkg = []
		self.vwFldValue = []		
		for i in range(len(xPos)):
			bkg = View(self.app, xpos=xPos[i], ypos=yPos[i], height=40, width=160, parent=self.root)
			bkg.set_resource(self.app.myimages.FldBkg)
			self.vwFldBkg.append(bkg)
			fld = View(self.app, parent=bkg)
			self.vwFldValue.append(fld)
			
		self.vwSaveBkg = View(self.app, xpos=485, ypos=yCmd, height=40, width=160, parent=self.root)
		self.vwSaveBkg.set_resource(self.app.myimages.FldBkg)
		self.vwSaveTxt = View(self.app, parent=self.vwSaveBkg)
		self.vwSaveTxt.set_text("Save",  font=self.app.myfonts.fnt20, colornum=0xffffff, flags=RSRC_VALIGN_CENTER + RSRC_HALIGN_CENTER)
		
		self.vwCancelBkg = View(self.app, xpos=735, ypos=yCmd, height=40, width=160, parent=self.root)
		self.vwCancelBkg.set_resource(self.app.myimages.FldBkg)
		self.vwCancelTxt = View(self.app, parent=self.vwCancelBkg)
		self.vwCancelTxt.set_text("Cancel",  font=self.app.myfonts.fnt20, colornum=0xffffff, flags=RSRC_VALIGN_CENTER + RSRC_HALIGN_CENTER)
			
	def isActive(self):
		return self.isactive
	
	def show(self):
		self.position = 0
		self.lOpts = {}
		for i in range(len(xPos)):
			self.lOpts[keys[i]] = self.app.opts[keys[i]]
			
		self.loadFields()
		self.hilite(True)
		self.root.set_visible(True)
		self.isactive = True
		
	def hide(self):
		self.root.set_visible(False)
		self.hilite(False)
		self.isactive = False
		
	def hilite(self, flag):
		if flag:
			img = self.app.myimages.FldBkgHi
		else:
			img = self.app.myimages.FldBkg
			
		if self.position < len(xPos):
			self.vwFldBkg[self.position].set_resource(img)
			
		elif self.position == POS_SAVE:
			self.vwSaveBkg.set_resource(img)
			
		elif self.position == POS_CANCEL:
			self.vwCancelBkg.set_resource(img)

	def loadFields(self):
		for i in range(len(xPos)):
			self.loadField(i)
			
	def loadField(self, i):
		v = self.lOpts[keys[i]]
		if v:
			value = "On"
		else:
			value = "Off"
				
		self.vwFldValue[i].set_text(value,  font=self.app.myfonts.fnt20, colornum=0xffffff, flags=RSRC_VALIGN_CENTER + RSRC_HALIGN_CENTER)
			
	def handle_key_press(self, keynum, rawcode):
		if keynum in [ KEY_LEFT, KEY_RIGHT, KEY_UP, KEY_DOWN ]:
			np = -1
			if keynum == KEY_LEFT:
				if self.position < len(xPos):
					np = lefts[self.position]
				elif self.position == POS_SAVE:
					np = -1
				elif self.position == POS_CANCEL:
					np = POS_SAVE
					
			elif keynum == KEY_RIGHT:
				if self.position < len(xPos):
					np = rights[self.position]
				elif self.position == POS_SAVE:
					np = POS_CANCEL
				elif self.position == POS_CANCEL:
					np = -1
						
			elif keynum == KEY_UP:
				if self.position < len(xPos):
					np = ups[self.position]
				elif self.position == POS_SAVE:
					np = 6
				elif self.position == POS_CANCEL:
					np = 7
						
			elif keynum == KEY_DOWN:
				if self.position < len(xPos):
					np = downs[self.position]
				elif self.position in [ POS_SAVE, POS_CANCEL ]:
					np = -1
					
			if np == -1:
				self.app.sound('bonk')
			else:
				self.hilite(False)
				self.position = np
				self.hilite(True)
				self.app.sound('updown')
				
		elif keynum == KEY_SELECT:
			if self.position < len(xPos):
				self.lOpts[keys[self.position]] = not self.lOpts[keys[self.position]]
				self.loadField(self.position)
				self.app.sound('updown')
				
			elif self.position == POS_SAVE:
				for i in range(len(xPos)):
					self.app.opts[keys[i]] = self.lOpts[keys[i]]
					
				self.app.config.save(self.app.opts)
				self.app.sound('alert')
				self.hide()
				
			elif self.position == POS_CANCEL:
				self.app.sound('error')
				self.hide()
		
		elif keynum == KEY_TIVO:
			pass
		
		else:
			self.app.sound('bonk')
					

