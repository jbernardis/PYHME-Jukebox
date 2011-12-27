from hme import *

from Config import ( screenWidth, menuYStart, menuItemCount, menuItemHeight )

menuNavKeys = [KEY_UP, KEY_DOWN, KEY_CHANNELUP, KEY_CHANNELDOWN, KEY_REPLAY, KEY_ADVANCE, KEY_FORWARD, KEY_REVERSE ]

class Menu:
	def __init__(self, items):
		self.items = items
		self.mx = 0
		self.counts = []
		for i in items: self.counts.append(None)
		
	def __iter__(self):
		self.mx = 0
		
	def setCount(self, choice, value):
		i = 0
		while i < self.__len__():
			if self.items[i][1] == choice:
				self.counts[i] = value
				break
			i += 1
			
	def next(self):
		x = self.translateIndex(self.mx)
		if x == None:
			raise StopIteration
		
		self.mx += 1
		return self.item[x]
	
	def setActive(self, x, flag):
		for i in self.items:
			if i[1] == x:
				i[2] = flag
				return
	
	def translateIndex(self, xIn):
		i = 0
		xOut = 0
		while i < len(self.items):
			i += 1
			if not self.items[i-1][2]: continue
			
			if xOut != xIn:
				xOut += 1
				continue
	
			return i-1
		
		return xOut-1
	
	def __len__(self):
		c = 0
		for i in self.items:
			if i[2]: c += 1
			
		return c
	
	def getMenuItem(self, xIn):
		xOut = self.translateIndex(xIn)
		if xOut == None:
			return None
		
		if self.counts[xOut]:
			return "%s (%d)" % (self.items[xOut][0], self.counts[xOut])
		else:
			return self.items[xOut][0]
	
	def getMenuValue(self, xIn):
		xOut = self.translateIndex(xIn)
		if xOut == None:
			return None

		return self.items[xOut][1]

	def getMenuMessage(self, xIn):
		xOut = self.translateIndex(xIn)
		if xOut == None:
			return None

		return self.items[xOut][3]


class MenuMgr:
	def __init__(self, app):
		self.app = app
		self.root = View(self.app, visible=True, parent=self.app.root)

		self.menu = None
		self.listOffset = 0
		self.listSelection = 0
		self.menuOffset = 0
		self.menuItemCount = menuItemCount
		self.stack = []

		self.vwMenuText = []
		self.vwMenuBkg = []
		self.vwMenuCue = []
		
		menuViewWidth = screenWidth

		self.vwMenuCue.append(View(self.app, height=32, width=32, ypos=menuYStart-menuItemHeight+3,
								xpos=25, parent=self.root))
		for i in range(menuItemCount):
			yval = menuYStart + (i*menuItemHeight)
			bkg = View(self.app, height=menuItemHeight, width=menuViewWidth, ypos=yval, parent=self.root)
			self.vwMenuBkg.append(bkg)
			self.vwMenuText.append(View(self.app, height=menuItemHeight, width=menuViewWidth-120, ypos=0, xpos=100, parent=bkg))
			self.vwMenuCue.append(View(self.app, height=32, width=32, ypos=4, xpos=25, parent=bkg))
		
		self.vwMenuCue.append(View(self.app, height=32, width=32, ypos=menuYStart+menuItemHeight*menuItemCount,
								xpos=25, parent=self.root))

	def hide(self):
		self.root.set_visible(False)
		
	def show(self):
		self.root.set_visible(True)
		
	def Descend(self, menu, offset=0):
		self.stack.append([self.menu, self.listOffset, self.listSelection, self.menuOffset, self.menuItemCount])
		self.menu = menu
		self.listOffset = 0
		self.listSelection = 0
		self.menuOffset = offset
		self.menuItemCount = menuItemCount - offset
		self.PopulateMenu(0)
		return self.menu, self.listSelection
	
	def ReplaceMenu(self, menu):
		self.menu = menu
		while(self.listSelection >= len(self.menu) and len(self.menu) != 0):
			self.CursorBackward(1)
			
		self.PopulateMenu(self.listSelection)
		
	def RefreshMenu(self, menu):
		if self.menu == menu or menu == None:
			self.PopulateMenu(self.listSelection)
	
	def Ascend(self):
		if len(self.stack) == 0:
			return None, None
		
		self.menu, self.listOffset, self.listSelection, self.menuOffset, self.menuItemCount = self.stack.pop()
		if self.menu == None:
			return None, None
		self.PopulateMenu(self.listSelection)
		return self.menu, self.listSelection
		

	def PopulateMenu(self, selection=None, on=True):
		if self.menuOffset > 0:
			for i in range(self.menuOffset):
				self.vwMenuText[i].clear_resource()
				
		for i in range(self.menuItemCount):
			sx = i + self.listOffset
			if (sx < len(self.menu)):
				item = self.menu.getMenuItem(sx)
				self.vwMenuText[i+self.menuOffset].set_text(item, font=self.app.myfonts.fnt24, colornum=0xffffff, flags=RSRC_HALIGN_LEFT)
			else:
				self.vwMenuText[i+self.menuOffset].clear_resource()
		if selection == None:
			selection = self.listSelection
			
		self.Hilite(selection, on)

	def Hilite(self, x, on=True):
		self.vwMenuCue[0].clear_resource()
		self.vwMenuCue[menuItemCount+1].clear_resource()
		for i in range(menuItemCount):
			self.vwMenuBkg[i].clear_resource()
			self.vwMenuCue[i+1].clear_resource()
			
		if on:
			self.app.setMessage(self.menu.getMenuMessage(x))
			sx = x - self.listOffset
			self.vwMenuBkg[sx+self.menuOffset].set_resource(self.app.myimages.HiLite)
			self.vwMenuCue[sx+1+self.menuOffset].set_resource(self.app.myimages.CueLeft)
			if x > 0:
				self.vwMenuCue[sx+self.menuOffset].set_resource(self.app.myimages.CueUp)
			if x < len(self.menu)-1:
				self.vwMenuCue[sx+2+self.menuOffset].set_resource(self.app.myimages.CueDown)


	def isNavKey(self, keynum, rawcode):
		return keynum in menuNavKeys
	
	def Navigate(self, keynum, rawcode):
		oldSelection = self.listSelection
		oldOffset = self.listOffset
		
		snd = 'updown'
		if keynum == KEY_DOWN:
			if not self.CursorForward(1):
				snd = 'bonk'
					
		elif keynum == KEY_UP:
			if not self.CursorBackward(1):
				snd = 'bonk'
				
		elif keynum == KEY_CHANNELUP:
			if not self.CursorBackward(self.menuItemCount):
				snd = 'bonk'
		
		elif keynum == KEY_CHANNELDOWN:
			if not self.CursorForward(self.menuItemCount):
				snd = 'bonk'
				
		elif keynum == KEY_REPLAY:
			self.listSelection = 0
			self.listOffset = 0
			
		elif keynum in [ KEY_ADVANCE ]:
			if self.listSelection == len(self.menu) - 1:
				self.listSelection = 0
				self.listOffset = 0
			else:
				self.listOffset = len(self.menu) - self.menuItemCount
				if self.listOffset < 0:
					self.listOffset = 0
				self.listSelection = len(self.menu)-1
				
		elif keynum == KEY_FORWARD:
			if self.listSelection >= len(self.menu)-1:
				snd = 'bonk'
			else:
				curChar = self.menu.getMenuItem(self.listSelection)[0]
				
				i = self.listSelection+1
				while(i < len(self.menu)):
					if curChar != self.menu.getMenuItem(i)[0]:
						break
					i += 1
	
				if (i >= len(self.menu)):
					self.listOffset = len(self.menu) - self.menuItemCount
					if self.listOffset < 0:
						self.listOffset = 0
					self.listSelection = len(self.menu)-1
				else:
					self.listSelection = i
					if i >= self.listOffset + self.menuItemCount:
						self.listOffset = i - self.menuItemCount + 1
						if self.listOffset < 0:
							self.listOffset = 0

		elif keynum == KEY_REVERSE:
			if self.listSelection == 0:
				snd = 'bonk'
			else:
				i = self.listSelection-1
				prevChar = self.menu.getMenuItem(i)[0]
				
				i -= 1
				while(i >= 0):
					if prevChar != self.menu.getMenuItem(i)[0]:
						i += 1
						break
					i -= 1
	
				if (i < 0):
					self.listOffset = 0
					self.listSelection = 0
				else:
					self.listSelection = i
					if i < self.listOffset:
						self.listOffset = i
		
		if self.listOffset == oldOffset:
			# screen is still the same - just maybe a different hilite line
			if self.listSelection != oldSelection:
				#remove the hilite from the old
				self.Hilite(oldSelection, False)
				# hilite the new
				self.Hilite(self.listSelection)
		else:
			# everything has changed
			self.PopulateMenu(self.listSelection)

		self.app.sound(snd)
		
		return self.menu, self.listSelection

	def CursorForward(self, lines):
		newSelection = self.listSelection + lines
		if newSelection >= len(self.menu):
			newSelection = len(self.menu)-1
		
		if newSelection == self.listSelection:
			return False
		
		self.listSelection = newSelection
		
		if self.listSelection - self.listOffset >= self.menuItemCount:
			newOffset = self.listOffset + lines
			if newOffset >= len(self.menu):
				newOffset = len(self.menu)-1
			self.listOffset = newOffset
			
		return True
		
	def CursorBackward(self, lines):
		if self.listSelection == 0:
			return False
		
		self.listSelection -= lines
		if self.listSelection < 0:
			self.listSelection = 0
			
		if self.listSelection < self.listOffset:
			self.listOffset -= lines
			if self.listOffset < 0:
				self.listOffset = 0
			
		return True
		
