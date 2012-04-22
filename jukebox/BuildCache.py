'''
Created on Nov 18, 2011

@author: jbernard
'''

import os
import sys
from mutagen.mp3 import MP3
from time import asctime
import marshal

import Config
from AlbumArt import resizeArt
from Config import artWidth, artHeight, CACHEFILE
from DBObjects import SongGraph, Song

UNKNOWN = "<unknown>"

def parseMP3(fn):
	try:
		md = MP3(fn)
	except:
		print "\nMutagen unable to parse: %s   skipping..." % fn
		return None
	
	mdkeys = md.keys()
	
	title = UNKNOWN
	if 'TIT2' in mdkeys:
		title = unicode(md['TIT2'])
		
	albumName = UNKNOWN
	if 'TALB' in mdkeys:
		albumName = unicode(md['TALB'])
		
	albumArtistName = UNKNOWN
	if 'TPE2' in mdkeys:
		albumArtistName = unicode(md['TPE2'])
		
	trackArtistName = albumArtistName
	if 'TPE1' in mdkeys:
		trackArtistName = unicode(md['TPE1'])

	if albumArtistName == UNKNOWN:
		albumArtistName = trackArtistName
					
#	if albumArtistName != trackArtistName:
#		print "%s\n  album: %s\n  track: %s" % (fn, albumArtistName, trackArtistName)
		
	genre = "<unknown>"
	if 'TCON' in mdkeys:
		genre = unicode(md['TCON'])
		
	track = 0
	if 'TRCK' in mdkeys:
		t = str(md['TRCK'])
		try:
			track=int(t.split('/')[0])
		except:
			track=0
		
	art = None
	if 'APIC:' in mdkeys:
		apic = md['APIC:']
		art = str(apic.data)

	return (title, albumName, trackArtistName, albumArtistName, fn, art, int(md.info.length), genre, track)

######################################################################################################
#
# Start of main routine
#
print asctime(), "starting cache build from MP3 files"
config = Config.Config()
opts = config.load(BuildingCache=True)

songList = []
artIndex = {}
artList = []
ax = 0

sdb = SongGraph(opts)
totalFileCount = 0

for container, root in opts['containers']:
	tree = os.walk(root)
	fileCount = 0
	print "Beginning container: %s (%s)" % (container, root)
	
	for path, dirs, files in tree:
		rpath = path[len(root):]
		if rpath.startswith(os.path.sep): rpath = rpath[1:]
		
		for name in files:
			if os.path.splitext(name)[1].lower() in ['.mp3']:
				fileCount += 1

				fn = os.path.join(path, name)
				if (fileCount % 1000) == 0:
					print "+",
					sys.stdout.flush()
				elif (fileCount % 500) == 0:
					print "|",
					sys.stdout.flush()
				elif (fileCount % 100) == 0:
					print ".",
					sys.stdout.flush()
					
				attr = parseMP3(fn)
				if attr == None:
					continue;
				
				(title, albumName, trackArtistName, albumArtistName, fn, art, length, genre, track) = attr
				artx = None
				if art:
					if albumName not in artIndex:
						artIndex[albumName] = {}
					
					if albumArtistName not in artIndex[albumName]:
						artx = ax
						artIndex[albumName][albumArtistName] = artx
						artRsz = resizeArt(art, artWidth, artHeight)
						if artRsz == None:
							print "Error resizing art for %s/%s" %(albumArtistName, albumName)
							
						artList.append(artRsz)
						ax += 1
					else:
						artx = artIndex[albumName][albumArtistName]
		
				songList.append((title, albumName, trackArtistName, albumArtistName, fn, artx, length, genre, track))			
				song = Song(title, albumName, trackArtistName, fn, length, genre, track)
				sdb.addSong(song, art, albumArtistName)
				
	totalFileCount += fileCount
	print "\n%d music files in container" % fileCount

print "%d total files in ALL containers" % totalFileCount
print "\n", asctime(), "Starting sort"					
sdb.sortAll()
print asctime(), "Saving cache to disk"

try:
	f = open(CACHEFILE, 'wb')
except:
	print "Error opening cache file for write"
else:
	try:
		marshal.dump((songList, artList), f)
	except:
		print "Error saving cache"
	else:
		f.close()
		print asctime(), "Finished - %d music files, %d albums, %d album artists, %d track artists" % sdb.count()