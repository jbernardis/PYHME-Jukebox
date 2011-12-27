from hme import *
import os
import string

cellHeight = 40
cellWidth = 40

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

charMap = [
		['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i'],
		['j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r'],
		['s', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0'],
		['1', '2', '3', '4', '5', '6', '7', '8', '9'],
		['done', 'cancel', 'shift', 'caps', 'space', 'delete', 'clear']
		]

validChars = string.uppercase + string.lowercase + string.digits + ' '

key2digit = { KEY_NUM0: '0',
			KEY_NUM1: '1',
			KEY_NUM2: '2',
			KEY_NUM3: '3',
			KEY_NUM4: '4',
			KEY_NUM5: '5',
			KEY_NUM6: '6',
			KEY_NUM7: '7',
			KEY_NUM8: '8',
			KEY_NUM9: '9'}

adjustDown = [ 0, 1, 2, 2, 3, 4, 4, 5, 6 ]
adjustUp = [ 0, 1, 2, 4, 5, 7, 8 ]
	
class Keyboard:
	def __init__(self, app, scrWidth=1280, scrHeight=720, done=1, cancel=2, skin=None):
		self.app = app
		self.root = View(self.app, visible=False)
		self.active = False
		self.kbdDone = done
		self.kbdCancel = cancel

		h = cellHeight*6 + 20
		w = cellWidth*9 + 20
		y = scrHeight/2 - h/2
		x = scrWidth/2 - w/2
		self.vwKbd = View(self.app, height=h, width=w, ypos=y, xpos=x, parent=self.root)
		self.kbdBkg = loadimage(app,'kbdbackground', skin)
		self.vwKbd.set_resource(self.kbdBkg)
		
		self.kbdSmallCursor = loadimage(app, 'kbdsmallcursor', skin)
		self.kbdLargeCursor = loadimage(app, 'kbdlargecursor', skin)
		
		self.vwKbdData = View(self.app, height=cellHeight, width=cellWidth*8,
							ypos = 10, xpos=30, parent=self.vwKbd)
		
		self.shift = False
		self.caps = False
		self.cancelled = False
		self.data = ""
		self.row = 0
		self.column = 0
		
		self.kbdMapBkg = []
		self.kbdMapTxt = []
		for r in range(4):
			self.kbdMapBkg.append([])
			self.kbdMapTxt.append([])
			for c in range(9):
				x=c*cellWidth+10
				y=r*cellHeight+50
				v = View(self.app, height=cellHeight, width=cellWidth, xpos=x, ypos=y, parent=self.vwKbd)
				t = View(self.app, height=cellHeight, width=cellWidth, xpos=x, ypos=y, parent=self.vwKbd)
				self.kbdMapBkg[r].append(v)
				self.kbdMapTxt[r].append(t)
				t.set_text(self.getText(r, c), font=self.app.myfonts.fnt30,
					colornum=0xffffff, flags=RSRC_VALIGN_CENTER + RSRC_HALIGN_CENTER)

		self.kbdMapBkg.append([])
		self.kbdMapTxt.append([])
		cw = int(9 * cellWidth / 7)
		for c in range(7):
			x=c*cw+10
			y=4*cellHeight+50
			v = View(self.app, height=cellHeight, width=cw, xpos=x, ypos=y, parent=self.vwKbd)
			t = View(self.app, height=cellHeight, width=cw, xpos=x, ypos=y, parent=self.vwKbd)
			self.kbdMapBkg[4].append(v)
			self.kbdMapTxt[4].append(t)
			t.set_text(self.getText(4, c), font=self.app.myfonts.fnt16,
				colornum=0xffffff, flags=RSRC_VALIGN_CENTER + RSRC_HALIGN_CENTER)

		self.reset()

	def reset(self):
		self.shift = False
		self.caps = False
		self.cancelled = False
		self.data = ""
		self.row = 0
		self.column = 0
		for r in range(4):
			for c in range(9):
				self.kbdMapBkg[r][c].clear_resource()
		for c in range(7):
			self.kbdMapBkg[4][c].clear_resource()

		self.setCursor()
		self.vwKbdData.set_text("")
		
	def getResult(self):
		if self.cancelled:
			return None
		return self.data
		
	def changeCase(self):
		for r in range(4):
			for c in range(9):
				self.kbdMapTxt[r][c].set_text(self.getText(r, c), font=self.app.myfonts.fnt30,
					colornum=0xffffff, flags=RSRC_VALIGN_CENTER + RSRC_HALIGN_CENTER)

		
	def setCursor(self, on=True):
		if on:
			if self.row == 4:
				self.kbdMapBkg[self.row][self.column].set_resource(self.kbdLargeCursor)
			else:
				self.kbdMapBkg[self.row][self.column].set_resource(self.kbdSmallCursor)
		else:
			self.kbdMapBkg[self.row][self.column].clear_resource()
			
	def getText(self, row, col):
		if row < 0 or row > 4:
			return ""
		
		if col < 0 or col > 8:
			return ""
		
		if row == 4 and col > 6:
			return ""
		
		v = charMap[row][col]
		
		if v >= 'a' and v <= 'z' and len(v) == 1:
			if self.shift or self.caps:
				v = v.upper()
				
		return v
				
	def activate(self, done=None, cancel=None):
		if done:
			self.kbdDone = done
			
		if cancel:
			self.kbdCancel = cancel
			
		self.root.set_visible(True)
		self.active = True
		
	def deactivate(self):
		self.active = False
		self.root.set_visible(False)
		
	def isActive(self):
		return self.active
	
	def handle_key_press(self, keynum, rawcode):
		snd = 'updown'
		if keynum == KEY_LEFT:
			if self.column == 0:
				snd = 'bonk'
			else:
				self.setCursor(False)
				self.column -= 1
				self.setCursor()
		elif keynum == KEY_RIGHT:
			if self.column == 8:
				snd = 'bonk'
			else:
				self.setCursor(False)
				self.column += 1
				self.setCursor()
				
		elif keynum == KEY_DOWN:
			if self.row == 4:
				snd = 'bonk'
			else:
				self.setCursor(False)
				self.row += 1
				if self.row == 4:
					self.column = adjustDown[self.column]
				self.setCursor()
				
		elif keynum == KEY_UP:
			if self.row == 0:
				snd = 'bonk'
			else:
				self.setCursor(False)
				if self.row == 4:
					self.column = adjustUp[self.column]
				self.row -= 1
				self.setCursor()
		
		elif keynum in [KEY_NUM0, KEY_NUM1, KEY_NUM2, KEY_NUM3, KEY_NUM4, 
					KEY_NUM5, KEY_NUM6, KEY_NUM7, KEY_NUM8, KEY_NUM9]:
			self.data += key2digit[keynum]
			self.vwKbdData.set_text(self.data, font=self.app.myfonts.fnt30,
				colornum=0xffffff, flags=RSRC_VALIGN_CENTER + RSRC_HALIGN_LEFT)
			if self.shift:
				self.shift = False
				self.changeCase()
				
		elif HME_MINOR_VERSION >= 49 and keynum > 0x10000:
			newChar = chr(keynum - 0x10000)
			if newChar in validChars:
				self.data += newChar
				self.vwKbdData.set_text(self.data, font=self.app.myfonts.fnt30,
									colornum=0xffffff, flags=RSRC_VALIGN_CENTER + RSRC_HALIGN_LEFT)
			else:
				snd = 'bonk'
				
		elif keynum == KEY_ENTER:
			self.app.send_key(KEY_TIVO, self.kbdDone)
			self.deactivate()
			
		elif keynum == KEY_CLEAR:
			self.data = ''
			self.vwKbdData.set_text("")
			
		elif HME_MINOR_VERSION >= 49 and keynum == KEY_BACKSPACE:
			if len(self.data) >= 1:
				self.data = self.data[:-1]
				self.vwKbdData.set_text(self.data, font=self.app.myfonts.fnt30,
						colornum=0xffffff, flags=RSRC_VALIGN_CENTER + RSRC_HALIGN_LEFT)
			else:
				snd = 'bonk'
				
		elif keynum == KEY_SELECT:
			if self.row != 4:
				self.data += self.getText(self.row, self.column)
				self.vwKbdData.set_text(self.data, font=self.app.myfonts.fnt30,
					colornum=0xffffff, flags=RSRC_VALIGN_CENTER + RSRC_HALIGN_LEFT)
				if self.shift:
					self.shift = False
					self.changeCase()
			else:
				cmd = self.getText(self.row, self.column).lower()
				if cmd == 'done':
					self.app.send_key(KEY_TIVO, self.kbdDone)
					self.deactivate()
					
				elif cmd == 'cancel':
					self.data = ""
					self.cancelled = True
					self.app.send_key(KEY_TIVO, self.kbdCancel)
					self.deactivate()
					
				elif cmd == 'shift':
					self.shift = not self.shift
					self.changeCase()
					
				elif cmd == 'caps':
					self.caps = not self.caps
					self.changeCase()
					
				elif cmd == 'space':
					self.data += ' '
					self.vwKbdData.set_text(self.data, font=self.app.myfonts.fnt30,
							colornum=0xffffff, flags=RSRC_VALIGN_CENTER + RSRC_HALIGN_LEFT)
				
				elif cmd == 'delete':
					if len(self.data) >= 1:
						self.data = self.data[:-1]
						self.vwKbdData.set_text(self.data, font=self.app.myfonts.fnt30,
								colornum=0xffffff, flags=RSRC_VALIGN_CENTER + RSRC_HALIGN_LEFT)
					else:
						snd = 'bonk'
				
				elif cmd == 'clear':
					self.data = ''
					self.vwKbdData.set_text("")
					
		else:
			snd = 'bonk'
		
		self.app.sound(snd)
		
