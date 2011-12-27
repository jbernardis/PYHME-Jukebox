from hme import *

from Config import detailYStart, artWidth, artHeight, detailItemHeight, detailLabelWidth, detailValueWidth

class DetailMgr:
	def __init__(self, app):
		self.app = app
		self.root = View(self.app, visible=False)

		self.vwAlbumArt = View(self.app, height=artHeight, width=artWidth, ypos=detailYStart, xpos=100, parent=self.root)
		self.vwItemLabel = []
		self.vwItemValue = []
		for i in range(5):
			yval = detailYStart + i * detailItemHeight
			self.vwItemLabel.append(View(self.app, height=detailItemHeight, width=detailLabelWidth, ypos=yval, xpos=artWidth+150, parent=self.root))
			self.vwItemValue.append(View(self.app, height=detailItemHeight, width=detailValueWidth, ypos=yval, xpos=artWidth+160+detailLabelWidth, parent=self.root))
		
	def show(self):
		self.root.set_visible(True)
		
	def hide(self):
		self.root.set_visible(False)
		
	def setAlbumDetail(self, album):
		art = album.getArt()
		if art:
			self.vwAlbumArt.set_resource(Image(self.app, data=art), flags=RSRC_VALIGN_TOP+RSRC_HALIGN_LEFT)
		else:
			self.vwAlbumArt.set_resource(self.app.myimages.DefaultArt)
			
		self.vwItemLabel[0].set_text("Album:", font=self.app.myfonts.fnt30, colornum=0xffffff, flags=RSRC_HALIGN_RIGHT)
		self.vwItemValue[0].set_text(album.getAlbumName(), font=self.app.myfonts.fnt30, colornum=0xffffff, flags=RSRC_HALIGN_LEFT)
		self.vwItemLabel[1].set_text("Artist:", font=self.app.myfonts.fnt30, colornum=0xffffff, flags=RSRC_HALIGN_RIGHT)
		self.vwItemValue[1].set_text(album.getArtistName(), font=self.app.myfonts.fnt30, colornum=0xffffff, flags=RSRC_HALIGN_LEFT)
		self.vwItemLabel[2].set_text("Tracks:", font=self.app.myfonts.fnt30, colornum=0xffffff, flags=RSRC_HALIGN_RIGHT)
		self.vwItemValue[2].set_text("%d" % len(album), font=self.app.myfonts.fnt30, colornum=0xffffff, flags=RSRC_HALIGN_LEFT)
		self.vwItemLabel[3].set_text("Total Time:", font=self.app.myfonts.fnt30, colornum=0xffffff, flags=RSRC_HALIGN_RIGHT)
		dur = album.getTotalTime()
		if dur >= 3600:
			durStr = "%d:%02d:%02d" % (int(dur/3600), int ((dur % 3600)/60), dur % 60)
		else:
			durStr = "%d:%02d" % (int(dur/60), dur % 60)
		self.vwItemValue[3].set_text(durStr, font=self.app.myfonts.fnt30, colornum=0xffffff, flags=RSRC_HALIGN_LEFT)
		self.vwItemLabel[4].clear_resource()
		self.vwItemValue[4].clear_resource()

	def setTrackDetail(self, track):
		album = track.getAlbum()
		art = album.getArt()
		if art:
			self.vwAlbumArt.set_resource(Image(self.app, data=art), flags=RSRC_VALIGN_TOP+RSRC_HALIGN_LEFT)
		else:
			self.vwAlbumArt.clear_resource()

		self.vwItemLabel[0].set_text("Track Title:", font=self.app.myfonts.fnt30, colornum=0xffffff, flags=RSRC_HALIGN_RIGHT)
		self.vwItemValue[0].set_text(track.getTitle(), font=self.app.myfonts.fnt30, colornum=0xffffff, flags=RSRC_HALIGN_LEFT)
		self.vwItemLabel[1].set_text("Album:", font=self.app.myfonts.fnt30, colornum=0xffffff, flags=RSRC_HALIGN_RIGHT)
		self.vwItemValue[1].set_text(album.getAlbumName(), font=self.app.myfonts.fnt30, colornum=0xffffff, flags=RSRC_HALIGN_LEFT)
		self.vwItemLabel[2].set_text("Artist:", font=self.app.myfonts.fnt30, colornum=0xffffff, flags=RSRC_HALIGN_RIGHT)
		self.vwItemValue[2].set_text(album.getArtistName(), font=self.app.myfonts.fnt30, colornum=0xffffff, flags=RSRC_HALIGN_LEFT)
		self.vwItemLabel[3].set_text("Duration:", font=self.app.myfonts.fnt30, colornum=0xffffff, flags=RSRC_HALIGN_RIGHT)
		dur = track.getLength()
		self.vwItemValue[3].set_text("%d:%02d" % (int(dur/60), dur % 60), font=self.app.myfonts.fnt30, colornum=0xffffff, flags=RSRC_HALIGN_LEFT)
		t = track.getTrack()
		if t == 0:
			self.vwItemLabel[4].clear_resource()
			self.vwItemValue[4].clear_resource()
		else:
			self.vwItemLabel[4].set_text("Track number:", font=self.app.myfonts.fnt30, colornum=0xffffff, flags=RSRC_HALIGN_RIGHT)
			self.vwItemValue[4].set_text("%d" % t, font=self.app.myfonts.fnt30, colornum=0xffffff, flags=RSRC_HALIGN_LEFT)

