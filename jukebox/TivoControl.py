'''
Created on Feb 15, 2012

@author: jbernard
'''
from hme import (View, Image, Font, HME_MINOR_VERSION,
				 KEY_ENTER, KEY_CLEAR, KEY_BACKSPACE,
				 KEY_LEFT, KEY_RIGHT, KEY_SELECT, KEY_UP, KEY_DOWN,
				 KEY_CHANNELUP, KEY_CHANNELDOWN, KEY_REPLAY, KEY_ADVANCE,
				 KEY_REVERSE, KEY_FORWARD,
				 KEY_NUM0, KEY_NUM1, KEY_NUM2, KEY_NUM3, KEY_NUM4,
				 KEY_NUM5, KEY_NUM6, KEY_NUM7, KEY_NUM8, KEY_NUM9,
				 ID_BONK_SOUND, ID_UPDOWN_SOUND, ID_SELECT_SOUND,
				 RSRC_HALIGN_CENTER, RSRC_VALIGN_CENTER, RSRC_HALIGN_LEFT)
	
import string
import os

SELECT_TYPE_H = 0
SELECT_TYPE_V = 1

LibPath = os.path.dirname(__file__)

keymap = { KEY_NUM1: 10.0, KEY_NUM2: 20.0, KEY_NUM3: 30.0, KEY_NUM4: 40.0, KEY_NUM5: 50.0,
		KEY_NUM6: 60.0, KEY_NUM7: 70.0, KEY_NUM8: 80.0, KEY_NUM9: 90.0 }
validChars = string.uppercase + string.lowercase

class TivoControl(View):
	def __init__(self, app, xpos=0, ypos=0, parent=None, height=10, width=100, imageFocus=None, imageNoFocus=None):
		View.__init__(self, app, xpos=xpos, ypos=ypos, width=width, height=height, parent=parent)
		self.imageFocus = imageFocus
		self.imageNoFocus = imageNoFocus
		
	def setFocus(self, focus):
		self.focus = focus
		if focus:
			img = self.imageFocus
		else:
			img = self.imageNoFocus
			
		if img != None:
			self.set_resource(img)
			
	def setImage(self, imageFocus=None, imageNoFocus=None):
		if imageFocus != None:
			self.imageFocus = imageFocus
			if self.hasFocus():
				self.set_resource(self.imageFocus)
		if imageNoFocus != None:
			self.imageNoFocus = imageNoFocus
			if not self.hasFocus():
				self.set_resource(self.imageNoFocus)

	def hasFocus(self):
		return self.focus
	
	def reset(self):
		return
	
class ControlContext:
	def __init__(self, app):
		self.app = app
		self.controlList = []
		self.controlCount = 0
		self.currentControl = None
		
	def addControl(self, control, tabUp=None, tabDown=None, tabLeft=None, tabRight=None):
		self.controlList.append(control)
		self.controlCount += 1
		self.setTabOrder(control, tabUp=tabUp, tabDown=tabDown, tabLeft=tabLeft, tabRight=tabRight)
		
	def setTabOrder(self, control, tabUp=None, tabDown=None, tabLeft=None, tabRight=None):
		c = self.findControl(control)
		if c != None:
			control.tabUp = tabUp
			control.tabDown = tabDown
			control.tabLeft = tabLeft
			control.tabRight = tabRight
			
	def findControl(self, control):
		i = 0
		for c in self.controlList:
			if c == control:
				return i
			i += 1
			
		return None
		
	def startSession(self, start=None):
		if len(self.controlList) == 0:
			return
		
		if self.currentControl != None:
			self.currentControl.setFocus(False)
			
		self.currentControl = None
		if start != None:
			self.currentControl = start
					
		if self.currentControl == None:
			self.currentControl = self.controlList[0]
			
		self.currentControl.setFocus(True)
			
	def endSession(self):
		if self.currentControl != None:
			self.currentControl.setFocus(False)
			self.currentControl = None
			
	def handle_key_press(self, keynum, rawcode):
		if self.currentControl == None:
			return False
		
		if self.currentControl.handle_key_press(keynum, rawcode):
			return True
		
		if keynum in [ KEY_RIGHT, KEY_LEFT, KEY_UP, KEY_DOWN ]:
			if keynum == KEY_RIGHT:			
				c = self.currentControl.tabRight
			elif keynum == KEY_LEFT:			
				c = self.currentControl.tabLeft
			elif keynum == KEY_UP:			
				c = self.currentControl.tabUp
			else:			
				c = self.currentControl.tabDown
				
			if c == None:
				self.app.sound(ID_BONK_SOUND)
			else:
				self.currentControl.setFocus(False)
				c.setFocus(True)
				self.currentControl = c
				self.app.sound(ID_UPDOWN_SOUND)
			return True
		
		return False
			
class Select(TivoControl):
	def __init__(self, app, xpos=0, ypos=0, parent=None, height=10, width=100, listType=SELECT_TYPE_H,
				 imageFocus=None, imageNoFocus=None, leftOffset=0, rightOffset=0, font=None, data=[""], selected=0,
				 colornum=0xffffff, flags=0):
		TivoControl.__init__(self, app, xpos=xpos, ypos=ypos, width=width, height=height, parent=parent,
				  imageFocus=imageFocus, imageNoFocus=imageNoFocus)
		self.leftOffset = leftOffset
		self.rightOffset = rightOffset
		self.parent = parent
		self.font=font
		self.colornum=colornum
		self.flags=flags
		self.data = data
		self.listType = listType
		self.origselected = selected
		
		self.vwText = View(app, xpos=leftOffset, ypos=0,
				width=width-leftOffset-rightOffset, height=height, parent=self)
		self.setFocus(False)
		
		self.reset()
		
	def reset(self):
		self.selected = self.origselected
		if self.selected < 0 or self.selected >= len(self.data):
			self.selected = 0
			
		self.vwText.set_text(self.data[self.selected], font=self.font, colornum=self.colornum, flags=self.flags)
		
	def setData(self, data):
		self.data = data
		if self.selected < 0 or self.selected >= len(self.data):
			self.selected = 0
			
		self.vwText.set_text(self.data[self.selected], font=self.font, colornum=self.colornum, flags=self.flags)
		
	def getSelection(self):
		return (self.selected, self.data[self.selected])
		
	def handle_key_press(self, keynum, rawcode):
		if not self.hasFocus():
			return False
		
		processedkey = False
		if ((keynum == KEY_RIGHT and self.listType == SELECT_TYPE_H) or
			(keynum == KEY_DOWN and self.listType == SELECT_TYPE_V)):
			s = self.selected + 1
			if s < len(self.data):
				self.vwText.set_text(self.data[s], font=self.font, colornum=self.colornum, flags=self.flags)
				self.selected = s
				self.app.sound(ID_UPDOWN_SOUND)
			else:
				self.app.sound(ID_BONK_SOUND)
			processedkey = True
				
		elif ((keynum == KEY_LEFT and self.listType == SELECT_TYPE_H) or
			(keynum == KEY_UP and self.listType == SELECT_TYPE_V)):
			s = self.selected - 1
			if s >= 0:
				self.vwText.set_text(self.data[s], font=self.font, colornum=self.colornum, flags=self.flags)
				self.selected = s
				self.app.sound(ID_UPDOWN_SOUND)
			else:
				self.app.sound(ID_BONK_SOUND)
			processedkey = True

		return processedkey
			
class DropDown(TivoControl):
	def __init__(self, app, ignorecase=True, xpos=0, ypos=0, parent=None, rows=3, rowHeight=10, width=100,
				 imageFocus=None, imageNoFocus=None, imageCheck=None, checkWidth=10, leftOffset=0, rightOffset=0,
				 font=None, data=[""], sortdata=None, selected=0, colornum=0xffffff, flags=0, multi=True):
		TivoControl.__init__(self, app, xpos=xpos, ypos=ypos, width=width, height=rows*rowHeight, parent=parent,
				  imageFocus=imageFocus, imageNoFocus=imageNoFocus)
		self.rowData=[]
		self.rowCheck=[]
		self.rows = rows
		self.ignorecase = ignorecase
		for i in range(rows):
			self.rowCheck.append(View(app, xpos=leftOffset, ypos=i*rowHeight, width=checkWidth, height=rowHeight, parent=self))
			self.rowData.append(View(app, xpos=leftOffset+checkWidth, ypos=i*rowHeight, width=width-leftOffset-rightOffset-checkWidth,
									height=rowHeight, parent=self))
		self.leftOffset = leftOffset
		self.rightOffset = rightOffset
		self.imageCheck = imageCheck
		self.parent = parent
		self.font=font
		self.colornum=colornum
		self.flags=flags
		self.multi=multi
		self.data = data
		if sortdata == None:
			self.sortdata = data
		else:
			self.sortdata = sortdata
		self.origselected = selected
		self.setFocus(False)
		
		self.reset()
		
	def reset(self):
		self.selected = self.origselected
		self.chosen = []
		for i in range(len(self.data)):
			self.chosen.append(False)
		
		if self.selected < 0 or self.selected >= len(self.data):
			self.selected = 0
			
		self.adjustDisplay(self.selected)
		
	def setData(self, data, sdata):
		self.data = data
		if sdata == None:
			self.sortdata = data
		else:
			self.sortdata = sdata
		self.reset()
		
	def adjustDisplay(self, nsel):
		if nsel < 0 or nsel >= len(self.data):
			return False
		
		self.selected = nsel			
		for i in range(len(self.rowData)):
			j = nsel+i
			if j >= len(self.data):
				self.rowCheck[i].clear_resource()
				self.rowData[i].set_text("", font=self.font, colornum=self.colornum, flags=self.flags)
			else:
				if self.chosen[j]:
					if self.imageCheck == None:
						self.rowCheck[i].clear_resource()
					else:
						self.rowCheck[i].set_resource(self.imageCheck)
				else:
					self.rowCheck[i].clear_resource()
				self.rowData[i].set_text(self.data[j], font=self.font, colornum=self.colornum, flags=self.flags)
				
		return True
		
	def getSelection(self):
		ret = []
		for i in range(len(self.chosen)):
			if self.chosen[i]:
				ret.append(i)
		return (ret)
		
	def handle_key_press(self, keynum, rawcode):
		if not self.hasFocus():
			return False
		
		processedkey = False
		if (keynum == KEY_DOWN):
			if self.adjustDisplay(self.selected+1):
				self.app.sound(ID_UPDOWN_SOUND)
			else:
				self.app.sound(ID_BONK_SOUND)
			processedkey = True
				
		elif (keynum == KEY_UP):
			if self.adjustDisplay(self.selected-1):
				self.app.sound(ID_UPDOWN_SOUND)
			else:
				self.app.sound(ID_BONK_SOUND)
			processedkey = True
			
		elif (keynum == KEY_CHANNELDOWN):
			self.selected += self.rows
			if self.selected >= len(self.data):
				self.selected = len(self.data) - 1
			if self.adjustDisplay(self.selected):
				self.app.sound(ID_UPDOWN_SOUND)
			else:
				self.app.sound(ID_BONK_SOUND)
			processedkey = True
				
		elif (keynum == KEY_CHANNELUP):
			self.selected -= self.rows
			if self.selected < 0:
				self.selected = 0
			if self.adjustDisplay(self.selected):
				self.app.sound(ID_UPDOWN_SOUND)
			else:
				self.app.sound(ID_BONK_SOUND)
			processedkey = True
			
		elif (keynum == KEY_REPLAY):
			self.selected = 0
			if self.adjustDisplay(self.selected):
				self.app.sound(ID_UPDOWN_SOUND)
			else:
				self.app.sound(ID_BONK_SOUND)
			processedkey = True
				
		elif (keynum in [ KEY_ADVANCE, KEY_NUM0 ]):
			if self.selected == len(self.data)-1:
				self.selected = 0
			else:
				self.selected = len(self.data) - 1

			if self.adjustDisplay(self.selected):
				self.app.sound(ID_UPDOWN_SOUND)
			else:
				self.app.sound(ID_BONK_SOUND)
			processedkey = True
			
		elif (keynum == KEY_SELECT):
			if not self.multi:
				for i in range(len(self.data)):
					self.chosen[i] = False
			self.chosen[self.selected] = not self.chosen[self.selected]
			self.adjustDisplay(self.selected)
			self.app.sound(ID_SELECT_SOUND)
			processedkey = True
			
		elif keynum == KEY_FORWARD:
			if self.selected < len(self.data):
				curChar = self.sortdata[self.selected][0]
				
				i = self.selected+1
				while(i < len(self.data)):
					if curChar != self.sortdata[i][0]:
						break
					i += 1
	
				if (i >= len(self.data)):
					self.selected = len(self.data)-1
				else:
					self.selected = i
					
				self.adjustDisplay(self.selected)
				self.app.sound(ID_UPDOWN_SOUND)
			else:
				self.app.sound(ID_BONK_SOUND) 
				
			processedkey = True

		elif keynum == KEY_REVERSE:
			if self.selected != 0:
				i = self.selected-1
				prevChar = self.menu.getFirstSortChar(i)
				
				i -= 1
				while(i >= 0):
					if prevChar != self.sortdata[i][0]:
						i += 1
						break
					i -= 1
	
				if (i < 0):
					self.selected = 0
				else:
					self.selected = i
					
				self.adjustDisplay(self.selected)
				self.app.sound(ID_UPDOWN_SOUND)
			else:
				self.app.sound(ID_BONK_SOUND) 
				
			processedkey = True
			
		elif keynum in keymap:
			pct = keymap[keynum]
			self.selected = int(pct * len(self.data) / 100.0)
			self.adjustDisplay(self.selected)
			self.app.sound(ID_UPDOWN_SOUND)
			processedkey = True
			
		elif HME_MINOR_VERSION >= 49 and keynum > 0x10000:
			newChar = chr(keynum - 0x10000)
			if newChar in validChars:
				if self.ignorecase:
					newChar = newChar.lower()
					
				i = 0
				while(i < len(self.data)):
					if newChar <= self.sortdata[i][0]:
						break
					i += 1

				if (i >= len(self.data)):
					self.app.sound(ID_BONK_SOUND)
				else:
					self.selected = i
					self.adjustDisplay(self.selected)
					self.app.sound(ID_UPDOWN_SOUND)

			else:
				self.app.sound(ID_BONK_SOUND)


		return processedkey
	
class Button(TivoControl):
	def __init__(self, app, context, xpos=0, ypos=0, parent=None, height=10, width=100,
				 imageFocus=None, imageNoFocus=None, leftOffset=0, rightOffset=0, font=None, text="",
				 colornum=0xffffff, flags=0, ID=None):
		TivoControl.__init__(self, app, xpos=xpos, ypos=ypos, width=width, height=height, parent=parent,
				  imageFocus=imageFocus, imageNoFocus=imageNoFocus)
		self.leftOffset = leftOffset
		self.rightOffset = rightOffset
		self.parent = parent
		self.context = context
		self.font=font
		self.colornum=colornum
		self.flags=flags
		self.text = text
		self.ID = ID
		
		self.vwText = View(app, xpos=leftOffset, ypos=0,
				width=width-leftOffset-rightOffset, height=height, parent=self)
		self.setFocus(False)
		
		self.vwText.set_text(self.text, font=self.font, colornum=self.colornum, flags=self.flags)
		
	def handle_key_press(self, keynum, rawcode):
		if not self.hasFocus():
			return False
		
		processedkey = False
		if keynum == KEY_SELECT:
			self.app.sound(ID_SELECT_SOUND)
			if self.context != None:
				self.context.buttonPress(self.ID)
			processedkey = True
				
		return processedkey
	
class CheckBox(TivoControl):
	def __init__(self, app, xpos=0, ypos=0, parent=None, height=10, width=100,
				 imageCheckFocus=None, imageCheckNoFocus=None, imageNoCheckFocus = None, imageNoCheckNoFocus = None,
				 leftOffset=0, rightOffset=0, font=None, text="", textCheck = None, initialState=False,
				 colornum=0xffffff, flags=0):
		self.initialState = initialState
		self.parent = parent
		self.imageCheckFocus = imageCheckFocus
		self.imageCheckNoFocus = imageCheckNoFocus
		
		if imageNoCheckFocus == None:
			self.imageNoCheckFocus = imageCheckFocus
		else:
			self.imageNoCheckFocus = imageNoCheckFocus
			
		if imageNoCheckNoFocus == None:
			self.imageNoCheckNoFocus = imageCheckNoFocus
		else:
			self.imageNoCheckNoFocus = imageNoCheckNoFocus

		TivoControl.__init__(self, app, xpos=xpos, ypos=ypos, width=width, height=height, parent=parent,
				  imageFocus=None, imageNoFocus=None)
		self.leftOffset = leftOffset
		self.rightOffset = rightOffset
		self.font=font
		self.colornum=colornum
		self.flags=flags
		self.text = text
		if textCheck == None:
			self.textCheck = text
		else:
			self.textCheck = textCheck
		
		self.vwText = View(app, xpos=leftOffset, ypos=0,
				width=width-leftOffset-rightOffset, height=height, parent=self)
		self.setFocus(False)
		
		self.reset()
		
	def reset(self):
		self.state = self.initialState
		if self.state:		
			self.setImage(imageFocus=self.imageCheckFocus, imageNoFocus=self.imageCheckNoFocus)
			self.vwText.set_text(self.textCheck, font=self.font, colornum=self.colornum, flags=self.flags)
		else:
			self.setImage(imageFocus=self.imageNoCheckFocus, imageNoFocus=self.imageNoCheckNoFocus)
			self.vwText.set_text(self.text, font=self.font, colornum=self.colornum, flags=self.flags)

	def getState(self):
		return self.state
			
	def handle_key_press(self, keynum, rawcode):
		if not self.hasFocus():
			return False
		
		processedkey = False
		if keynum == KEY_SELECT:
			self.state = not self.state
			if self.state:
				self.setImage(imageFocus=self.imageCheckFocus, imageNoFocus=self.imageCheckNoFocus)
				self.vwText.set_text(self.textCheck, font=self.font, colornum=self.colornum, flags=self.flags)
			else:
				self.setImage(imageFocus=self.imageNoCheckFocus, imageNoFocus=self.imageNoCheckNoFocus)
				self.vwText.set_text(self.text, font=self.font, colornum=self.colornum, flags=self.flags)

			self.app.sound(ID_SELECT_SOUND)
			processedkey = True
				
		return processedkey
	
class RadioGroup:
	def __init__(self, app,
				imageSetFocus=None, imageSetNoFocus=None, imageNoSetFocus = None, imageNoSetNoFocus = None):
		self.imageSetFocus = imageSetFocus
		self.imageSetNoFocus = imageSetNoFocus
		if imageNoSetFocus == None:
			self.imageNoSetFocus = imageSetFocus
		else:
			self.imageNoSetFocus = imageNoSetFocus
		if imageNoSetNoFocus == None:
			self.imageNoSetNoFocus = imageNoSetNoFocus
		else:
			self.imageNoSetNoFocus = imageNoSetNoFocus

		self.buttonList = []
		self.nButtons = 0
		self.app = app
		
	def getImageFocus(self, button):
		if button.isSet():
			return self.imageSetFocus
		else:
			return self.imageNoSetFocus
		
	def getImageNoFocus(self, button):
		if button.isSet():
			return self.imageSetNoFocus
		else:
			return self.imageNoSetNoFocus
		
	def addButton(self, button, state):
		self.buttonList.append(button)
		self.nButtons += 1
		if self.nButtons == 1:
			button.set(True)
		else:
			button.set(state)
		
	def set(self, button):
		found = False
		# make sure button is in group
		for b in self.buttonList:
			if b == button:
				found = True
				if b.isSet():
					# if its already set, no action is needed
					return
				break
			
		if not found:
			return
		
		for b in self.buttonList:
			if b == button:
				b.set(True)
			else:
				b.set(False)

class RadioButton(TivoControl):
	def __init__(self, app, buttonGroup, xpos=0, ypos=0, parent=None, height=10, width=100,
				 leftOffset=0, rightOffset=0, font=None, text="", textSet = None, initialState=False,
				 colornum=0xffffff, flags=0):
		self.state = initialState
		self.parent = parent
		self.buttonGroup = buttonGroup

		TivoControl.__init__(self, app, xpos=xpos, ypos=ypos, width=width, height=height, parent=parent,
				  imageFocus=buttonGroup.getImageFocus(self), imageNoFocus=buttonGroup.getImageNoFocus(self))
		self.leftOffset = leftOffset
		self.rightOffset = rightOffset
		self.font=font
		self.colornum=colornum
		self.flags=flags
		self.text = text
		if textSet == None:
			self.textSet = text
		else:
			self.textSet = textSet
		
		self.vwText = View(app, xpos=xpos+leftOffset, ypos=ypos,
				width=width-leftOffset-rightOffset, height=height, parent=self)
		self.setFocus(False)
		buttonGroup.addButton(self, self.state)

	def getState(self):
		return self.state
	
	def set(self, setVal):
		if self.state != setVal:
			self.state = setVal
			self.setImage(imageFocus=self.buttonGroup.getImageFocus(self),
						imageNoFocus=self.buttonGroup.getImageNoFocus(self))
			if self.state:
				self.vwText.set_text(self.textSet, font=self.font, colornum=self.colornum, flags=self.flags)
			else:
				self.vwText.set_text(self.text, font=self.font, colornum=self.colornum, flags=self.flags)
			
	def handle_key_press(self, keynum, rawcode):
		if not self.hasFocus():
			return False
		
		processedkey = False
		if keynum == KEY_SELECT:
			self.buttonGroup.set(self)

			self.app.sound(ID_SELECT_SOUND)
			processedkey = True
				
		return processedkey
