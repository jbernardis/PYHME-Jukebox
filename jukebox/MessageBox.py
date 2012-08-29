from hme import *

from Config import screenHeight, screenWidth

msgboxheight = 200
msgboxwidth = 400

class MessageBox(View):
	def __init__(self, app, title, body, snd, keymaps):
		xpos = (screenWidth-msgboxwidth)/2
		ypos = (screenHeight-msgboxheight)/2
		View.__init__(self, app, width=msgboxwidth, height=msgboxheight, xpos=xpos, ypos=ypos, visible=False)
		self.set_resource(app.myimages.MsgBox)
		
		self.app = app
		app.msgbox = self
		self.keymaps = keymaps

		self.vwTitle = View(self.app, parent=self, width=msgboxwidth-20, height=30, xpos=10, ypos=4)
		self.vwTitle.set_text(title, font=self.app.myfonts.fnt24, colornum=0xffffff, flags=RSRC_HALIGN_CENTER)
		
		self.vwBody = View(self.app, parent=self, width=msgboxwidth-20, height=msgboxheight-40, xpos=10, ypos=38)
		self.vwBody.set_text(body, font=self.app.myfonts.fnt20, colornum=0xffffff,
							flags=RSRC_TEXT_WRAP + RSRC_HALIGN_CENTER + RSRC_VALIGN_CENTER)
		
		if snd:
			self.app.sound(snd)
			
		self.set_visible(True)
	
	def close(self):
		self.set_visible(False);
		self.app.msgbox = None

	def handle_key_press(self, keynum, rawcode):
		self.app.sound('updown')
		for km in self.keymaps:
			if keynum in km[0] or len(km[0]) == 0:
				self.app.send_key(KEY_TIVO, km[1])
				self.set_visible(False)
				self.app.msgbox = None
				return
