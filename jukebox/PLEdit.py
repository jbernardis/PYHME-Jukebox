from hme import *
import random

from Config import ( screenWidth, menuYStart, menuItemCount, menuItemHeight )

editNavKeys = [KEY_UP, KEY_DOWN, KEY_CHANNELUP, KEY_CHANNELDOWN, KEY_LEFT, KEY_RIGHT, KEY_REPLAY, KEY_ADVANCE ]

EDIT_MODE_SELECT = 0
EDIT_MODE_UPDN = 1
EDIT_MODE_BROWSE = 2

EDIT_MESSAGE_1 = "Press CLEAR to delete a song, 1 to shuffle list"
EDIT_MESSAGE_2 = "Press CLEAR again to confirm deletion"
EDIT_MESSAGE_3 = "Press up/down to change song order"

class PLEdit:
	def __init__(self, app):
		self.app = app
		self.root = View(self.app, visible=False, parent=self.app.root)
		
		self.imgMap = [
			[ self.app.myimages.EditNormal, self.app.myimages.EditNormalU, self.app.myimages.EditNormalD, self.app.myimages.EditNormalUD ],
			[ self.app.myimages.EditUpDn,   self.app.myimages.EditUpDnU,   self.app.myimages.EditUpDnD,   self.app.myimages.EditUpDnUD ],
			[ self.app.myimages.EditBrowse, self.app.myimages.EditBrowse,  self.app.myimages.EditBrowse,  self.app.myimages.EditBrowse ]
			]

		self.playlist = None
		self.editSelection = 0
		self.editOffset = 0
		self.editItemCount = menuItemCount
		self.editMode = EDIT_MODE_SELECT
		self.title = ""
		
		self.clearCount = 0
		
		self.active = False

		self.vwEditText = []
		self.vwEditBkg = []
		self.vwEditCue = []
		
		editViewWidth = screenWidth

		self.vwEditCue.append(View(self.app, height=32, width=32, ypos=menuYStart-menuItemHeight+3,
								xpos=25, parent=self.root))
		for i in range(self.editItemCount):
			yval = menuYStart + (i*menuItemHeight)
			bkg = View(self.app, height=menuItemHeight, width=editViewWidth, ypos=yval, parent=self.root)
			self.vwEditBkg.append(bkg)
			self.vwEditText.append(View(self.app, height=menuItemHeight, width=editViewWidth-120, ypos=0, xpos=100, parent=bkg))
			self.vwEditCue.append(View(self.app, height=32, width=32, ypos=4, xpos=25, parent=bkg))
		
		self.vwEditCue.append(View(self.app, height=32, width=32, ypos=menuYStart+menuItemHeight*menuItemCount,
								xpos=25, parent=self.root))

	def hide(self):
		self.root.set_visible(False)
		self.active = False
		
	def show(self):
		self.app.setSubTitle(self.title)
		self.root.set_visible(True)
		self.active = True
		if self.editMode == EDIT_MODE_BROWSE:
			self.app.setMessage("")
		else:
			self.app.setMessage(EDIT_MESSAGE_1)
		
	def isActive(self):
		return self.active
		
	def edit(self, pl, done=1):
		self.playlist = pl
		self.title = "Playlist Editor - %s" % self.playlist.getName()
		self.editOffset = 0
		self.editSelection = 0
		self.editMode = EDIT_MODE_SELECT
		self.sendWhenDone = done
		self.PopulateMenu(0)
		self.show()
	
	def browse(self, pl, done=1):
		self.playlist = pl
		self.title = "Playlist Browser - %s" % self.playlist.getName()
		self.editOffset = 0
		self.editSelection = 0
		self.editMode = EDIT_MODE_BROWSE
		self.sendWhenDone = done
		self.PopulateMenu(0)
		self.show()
	
	def PopulateMenu(self, selection=None, on=True):
		for i in range(self.editItemCount):
			sx = i + self.editOffset
			if (sx < len(self.playlist)):
				item = self.playlist.getMenuItem(sx)
				self.vwEditText[i].set_text(item, font=self.app.myfonts.fnt24, colornum=0xffffff, flags=RSRC_HALIGN_LEFT)
			else:
				self.vwEditText[i].clear_resource()
				
		if selection == None:
			selection = self.editSelection
			
		self.Hilite(selection, on)

	def Hilite(self, x, on=True):
		self.vwEditCue[0].clear_resource()
		self.vwEditCue[self.editItemCount+1].clear_resource()
		for i in range(self.editItemCount):
			self.vwEditBkg[i].clear_resource()
			self.vwEditCue[i+1].clear_resource()
			
		if on:
			sx = x - self.editOffset
			xBkg = 0
			if x > 0:
				self.vwEditCue[sx].set_resource(self.app.myimages.CueUp)
				xBkg += 1
			if x < len(self.playlist)-1:
				self.vwEditCue[sx+2].set_resource(self.app.myimages.CueDown)
				xBkg += 2
				
			img = self.imgMap[ self.editMode ][xBkg]
			self.vwEditBkg[sx].set_resource(img)


	def isNavKey(self, keynum, rawcode):
		return keynum in editNavKeys
	
	def handle_key_press(self, keynum, rawcode):
		oldSelection = self.editSelection
		oldOffset = self.editOffset
		
		if self.editMode == EDIT_MODE_SELECT:
			if keynum != KEY_CLEAR and self.clearCount == 1:
				self.clearCount = 0
				self.app.setMessage(EDIT_MESSAGE_1)

		
		snd = 'updown'
		if keynum == KEY_DOWN:
			if self.editMode in [ EDIT_MODE_SELECT, EDIT_MODE_BROWSE ]:
				if not self.CursorForward(1):
					snd = 'bonk'
			else:
				if not self.SwapBelow():
					snd = 'bonk'
				else:
					oldOffset = -1 # force populate call below
					
		elif keynum == KEY_UP:
			if self.editMode in [ EDIT_MODE_SELECT, EDIT_MODE_BROWSE ]:
				if not self.CursorBackward(1):
					snd = 'bonk'
			else:
				if not self.SwapAbove():
					snd = 'bonk'
				else:
					oldOffset = -1
				
		elif keynum == KEY_LEFT:
			if self.editMode == EDIT_MODE_UPDN:
				self.editMode = EDIT_MODE_SELECT
				self.app.setMessage(EDIT_MESSAGE_1)
				self.Hilite(self.editSelection)
			else:
				self.hide()
				self.app.send_key(KEY_TIVO, self.sendWhenDone)
				
		elif keynum == KEY_RIGHT:
			if self.editMode == EDIT_MODE_SELECT:
				self.editMode = EDIT_MODE_UPDN
				self.app.setMessage(EDIT_MESSAGE_3)
				self.Hilite(self.editSelection)
			else:
				snd = 'bonk'
				
		elif keynum == KEY_NUM1:
			if self.editMode != EDIT_MODE_SELECT:
				snd = 'bonk'
			else:
				n = len(self.playlist)
				if n >= 1:
					for i in range(n-1):
						j = i
						while j == i:
							j = random.choice(range(n))
							
						self.playlist.swapSongs(i, j)
						
					oldOffset = -1
			
		elif keynum == KEY_CHANNELUP:
			if self.editMode == EDIT_MODE_UPDN or not self.CursorBackward(self.editItemCount):
				snd = 'bonk'
		
		elif keynum == KEY_CHANNELDOWN:
			if self.editMode == EDIT_MODE_UPDN or not self.CursorForward(self.editItemCount):
				snd = 'bonk'
				
		elif keynum == KEY_REPLAY:
			if self.editMode == EDIT_MODE_UPDN:
				snd = 'bonk'
			else:
				self.editSelection = 0
				self.editOffset = 0
			
		elif keynum == KEY_ADVANCE:
			if self.editMode == EDIT_MODE_UPDN:
				snd = 'bonk'
			else:
				if self.editSelection == len(self.playlist) - 1:
					self.editSelection = 0
					self.editOffset = 0
				else:
					self.editOffset = len(self.playlist) - self.editItemCount
					if self.editOffset < 0:
						self.editOffset = 0
					self.editSelection = len(self.playlist)-1
					
		elif keynum == KEY_CLEAR:
			if self.editMode == EDIT_MODE_SELECT:
				if self.clearCount == 0:
					self.clearCount = 1
					snd = 'alert'
					self.app.setMessage(EDIT_MESSAGE_2)
				else:
					self.clearCount = 0
					self.playlist.delSong(self.editSelection)
					oldOffset = -1
					if len(self.playlist) == 0:
						self.hide()
						self.app.send_key(KEY_TIVO, self.sendWhenDone)
					else:
						if self.editSelection >= len(self.playlist):
							self.CursorBackward(1)
						self.app.setMessage(EDIT_MESSAGE_1)
			else:
				snd = 'bonk'

		if self.editOffset == oldOffset:
			# screen is still the same - just maybe a different hilite line
			if self.editSelection != oldSelection:
				#remove the hilite from the old
				self.Hilite(oldSelection, False)
				# hilite the new
				self.Hilite(self.editSelection)
		else:
			# everything has changed
			self.PopulateMenu(self.editSelection)

		self.app.sound(snd)
		
		return
	
	def SwapAbove(self):
		if self.editSelection == 0:
			return False
		
		if not self.playlist.swapSongs(self.editSelection, self.editSelection - 1):
			return False
		
		self.editSelection -= 1
		
		if self.editSelection < self.editOffset:
			self.editOffset -= 1
			if self.editOffset < 0:
				self.editOffset = 0
			
		return True
	
	def SwapBelow(self):
		if self.editSelection >= len(self.playlist)-1:
			return False
		
		if not self.playlist.swapSongs(self.editSelection, self.editSelection + 1):
			return False
		
		self.editSelection += 1
		
		if self.editSelection - self.editOffset >= self.editItemCount:
			newOffset = self.editOffset + 1
			if newOffset >= len(self.playlist):
				newOffset = len(self.playlist)-1
			self.editOffset = newOffset
			
		return True

	def CursorForward(self, lines):
		newSelection = self.editSelection + lines
		if newSelection >= len(self.playlist):
			newSelection = len(self.playlist)-1
		
		if newSelection == self.editSelection:
			return False
		
		self.editSelection = newSelection
		
		if self.editSelection - self.editOffset >= self.editItemCount:
			newOffset = self.editOffset + lines
			if newOffset >= len(self.playlist):
				newOffset = len(self.playlist)-1
			self.editOffset = newOffset
			
		return True
		
	def CursorBackward(self, lines):
		if self.editSelection == 0:
			return False
		
		self.editSelection -= lines
		if self.editSelection < 0:
			self.editSelection = 0
			
		if self.editSelection < self.editOffset:
			self.editOffset -= lines
			if self.editOffset < 0:
				self.editOffset = 0
			
		return True
		
