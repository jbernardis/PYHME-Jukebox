'''
Created on Nov 23, 2011

@author: Jeff
'''
import Image as img
from cStringIO import StringIO

def resizeArt(data, width, height):
	try:
		pic = img.open(StringIO(data))
		pic.draft('RGB', (width, height))
		if pic.mode == 'P':
			pic = pic.convert()
		filew, fileh = pic.size
	
		if ((filew > width) or (fileh >height)):
			# determine horizontal and vertical ratios of pic to view
			ratiow = filew / float(width)
			ratioh = fileh / float(height)
			# choose the larger of the 2 ratios
			ratio = ratiow
			if ratioh > ratiow:
				ratio = ratioh
			# and scale accordingly
			nheight = int(fileh / ratio)
			nwidth = int(filew / ratio)
			pic = pic.resize((nwidth, nheight), img.ANTIALIAS)
			
		out = StringIO()
		pic.save(out, 'JPEG')
		encoded = out.getvalue()
		out.close()
			
		return encoded
	
	except:
		return None
