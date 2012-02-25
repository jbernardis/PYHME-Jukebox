import os
import urllib
from urllib import FancyURLopener
import string
from string import maketrans
from HTMLParser import HTMLParser

class MyOpener(FancyURLopener):
	# let's spoof azlyrics into thinking we're a normal browser
	version = "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)"

if os.path.sep == '/':
	quote = urllib.quote
	unquote = urllib.unquote_plus
else:
	quote = lambda x: urllib.quote(x.replace(os.path.sep, '/'))
	unquote = lambda x: os.path.normpath(urllib.unquote_plus(x))

# a translation table to remove punctioation from artist and song names
transTable = maketrans(string.punctuation, " " * len(string.punctuation))
	
class FindSongParser(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		self.lookingForTable = False
		self.lookingForHref = False
		self.matchURLs = []
		
	def __len__(self):
		return len(self.matchURLs)
	
	def __iter__(self):
		self.__uindex__ = 0
		return self
	
	def next(self):
		if self.__uindex__ < self.__len__():
			i = self.__uindex__
			self.__uindex__ += 1
			return self.matchURLs[i]

		raise StopIteration

	def handle_starttag(self, tag, attrs):
		if tag == 'table' and self.lookingForTable:
			self.lookingForHref = True
					
		if tag == 'a' and self.lookingForHref:
			adict = dict(attrs)
			if 'href' in adict and 'rel' in adict and adict['rel'] == "external":
				self.matchURLs.append(adict['href'])
				
	def handle_data(self, data):
		if data.lower().count('search done') != 0:
			self.lookingForTable = True


def makeASCII(s):
	result = ""
	for i in range(len(s)):
		if ord(s[i]) < 128:
			result += s[i]
	return result

class LyricsParser(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		self.gatherLyrics = False
		self.lyrics = None
		
	def getLyrics(self):
		return self.lyrics
	
	def handle_comment(self, data):
		if data.lower().count('start of lyrics') != 0:
			self.gatherLyrics = True
		elif data.lower().count('end of lyrics') != 0:
			self.gatherLyrics = False
			
	def handle_data(self, data):
		if not self.gatherLyrics:
			return
		if self.lyrics == None:
			self.lyrics = makeASCII(data).strip() + "\n"
		else:
			self.lyrics += makeASCII(data).strip() + "\n"
			
def trivialWord(word):
	w = word.lower()
	return w in ['a', 'the', 'and', 'or']
			
def scoreURL(url, lArtist,lTitle):
	terms = url.lower().split('/')
	if len(terms) != 6:
		return 0
	
	if ((terms[0], terms[1], terms[2], terms[3]) != ('http:', '', 'www.azlyrics.com', 'lyrics')):
		return 0
	
	score = 0
	potential = len(lArtist) + len(lTitle)
	
	for w in lArtist:
		if trivialWord(w):
			potential -= 1
		elif terms[4].count(w) != 0:
			score += 1

	for w in lTitle:
		if trivialWord(w):
			potential -= 1
		elif terms[5].count(w) != 0:
			score += 1
			
	return float(score)/float(potential)

def GetLyrics(artist, title, verbose=False, html=False):

	myopener = MyOpener()
			
	lArtist = makeASCII(artist).lower().translate(transTable).split()
	lTitle = makeASCII(title).lower().translate(transTable).split()
	if verbose: 
		print "Translated artist: ", lArtist
		print "Translated title: ", lTitle
	
	params = urllib.urlencode({'q': '+'.join(lArtist+lTitle)})
	url = 'http://search.azlyrics.com/search.php?%s' % params
	if verbose: 
		print "Starting URL: (%s)" % url

	try:
		f = myopener.open(url)
		fhtml = f.read().replace('scr\' + \'ipt', "script").replace('scr\\\' + \\\'ipt', 'script')
		f.close()
		
	except:
		print "Main URL Failure - unable to retrieve lyrics"
		return None
	
	if verbose and html: 
		print "Search html = (%s)" % fhtml
	
	fparser = FindSongParser()
	fparser.feed(fhtml)

	lyrics = None
	maxScore = 0.51
	
	for url in fparser:
		s = scoreURL(url, lArtist, lTitle)
		if verbose: 
			print "URL: (%s) score %f" % (url, s)
		
		if (s > maxScore) or (s == maxScore and lyrics == None):
			if verbose: 
				print "score warrants a lyric lookup"
			
			try:
				l = myopener.open(url)
				lhtml = l.read().replace('scr\' + \'ipt', "script").replace('scr\\\' + \\\'ipt', 'script')
				l.close()
				
			except:
				print "Exception occurred trying to get lyrics"
				lhtml = None
			
			if lhtml == None:
				if verbose:
					print "Lyric HTML = None"
			else:
				if verbose:
					print "Trying to retrieve lyrics"
					if html:
						print "lyric html = (%s)" % lhtml
				
				lparser = LyricsParser()
				lparser.feed(lhtml)
				nlyrics = lparser.getLyrics()
				if nlyrics:
					if verbose: 
						print "got some lyrics - setting new max to %f" % s
					lyrics = nlyrics
					maxScore = s
				else:
					if verbose:
						print "We had a high-scoring url, but couldn't retrieve lyrics"
						# print the html if we hadn't previously
						if not html:
							print "lyric html = (%s)" % lhtml

	return lyrics