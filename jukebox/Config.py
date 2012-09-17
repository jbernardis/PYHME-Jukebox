import os
import ConfigParser
import socket

screenHeight = 720
screenWidth = 1280

titleYPos = 36
subTitleYPos = 84
messageYPos = 642
menuItemCount = 13
menuYStart = 121
menuItemHeight = 40 

detailYStart = 121
detailItemHeight = 40
detailLabelWidth = 180
detailValueWidth = 500

artWidth = 320
artHeight = 320

lyricHeight = 600
lyricWidth = 1160

npArtX = 860
npArtY = 100
npItemHeight = 40
npLabelWidth = 140
npValueWidth = 620
npCounterY = 100
npInfoX = 100
npInfoY = 200
npProgressY = 500
npProgHeight = 80
npCursorWidth = 120

AppPath = os.path.dirname(__file__)

class ConfigError(Exception):
	pass

def parseBoolean(val, defaultVal):
	lval = val.lower();
	
	if lval == 'true' or lval == 't' or lval == 'yes' or lval == 'y':
		return True
	
	if lval == 'false' or lval == 'f' or lval == 'no' or lval == 'n':
		return False
	
	return defaultVal

CFGFILENAME = 'jukebox.ini'
SECTIONNAME = 'jukebox'
CACHEFILE = os.path.join(AppPath, "jukebox.cache")

class Config:
	def __init__(self):
		self.fn = os.path.join(os.path.dirname(__file__), CFGFILENAME)

		self.cfg = ConfigParser.ConfigParser()
		if not self.cfg.read(self.fn):
			raise ConfigError("ERROR: Jukebox configuration file does not exist.")
		
		server_host = socket.gethostbyname(socket.gethostname())
	
		self.opts = {}		
		self.defaults = {
			'preloadcache' : False,
			'cachewatchinterval' : 600,
			'serverip' : server_host,
			'serverport': None,
			'skin' : None,
			'trackshuffle': False,
			'trackloop': False,
			'albumshuffle': False,
			'albumloop': False,
			'playlistshuffle': False,
			'playlistloop': False,
			'artistshuffle': False,
			'artistloop': False,
			'autoswitchnp': 120,
			'screensaver': 600,
			'lyricindent': -1,
			'ignoreidle' : False,
			'ignorearticles' : False,
			'ignorecase' : True,
			'usefolderart' : False,
			'folderartfiles' : [ "folder.jpg" ],
				}

	def getConfigParser(self):
		return self.cfg
	
	def load(self, BuildingCache=False):
		self.opts = {}
		
		pytivo = None
		
		for k in self.defaults:
			self.opts[k] = self.defaults[k]
			
		self.loaded = {}
		if self.cfg.has_section(SECTIONNAME):
			for opt, value in self.cfg.items(SECTIONNAME):
				self.loaded[opt] = value
				# options for metadata on the info screen
				if opt == 'serverip':
					self.opts['serverip'] = value
	
				elif opt == 'serverport':
					self.opts['serverport'] = value
	
				elif opt == 'skin':
					if value == "" or value.lower() == "none":
						self.opts['skin'] = None
					else:
						self.opts['skin'] = value
	
				elif opt == 'pytivo':
					pytivo = value

				elif opt == 'preloadcache': 
					self.opts['preloadcache'] = parseBoolean(value, False)
				
				elif opt == 'cachewatchinterval': 
					try:
						self.opts['cachewatchinterval'] = int(value)
					except:
						print "Invalid cache watch interval (%s) - defaulting to 600" % value
						self.opts['cachewatchinterval'] = 600
					
				elif opt == 'trackshuffle': 
					self.opts['trackshuffle'] = parseBoolean(value, False)
					
				elif opt == 'usefolderart': 
					self.opts['usefolderart'] = parseBoolean(value, False)
					
				elif opt == 'folderartfiles': 
					self.opts['folderartfiles'] = [x.strip() for x in value.split(',')]
					
				elif opt == 'ignoreidle': 
					self.opts['ignoreidle'] = parseBoolean(value, False)
					
				elif opt == 'ignorearticles': 
					self.opts['ignorearticles'] = parseBoolean(value, False)
					
				elif opt == 'ignorecase': 
					self.opts['ignorecase'] = parseBoolean(value, True)
					
				elif opt == 'trackloop': 
					self.opts['trackloop'] = parseBoolean(value, False)
					
				elif opt == 'albumshuffle': 
					self.opts['albumshuffle'] = parseBoolean(value, False)
					
				elif opt == 'albumloop': 
					self.opts['albumloop'] = parseBoolean(value, False)
					
				elif opt == 'playlistshuffle': 
					self.opts['playlistshuffle'] = parseBoolean(value, False)
					
				elif opt == 'playlistloop': 
					self.opts['playlistloop'] = parseBoolean(value, False)
					
				elif opt == 'artistshuffle': 
					self.opts['artistshuffle'] = parseBoolean(value, False)
					
				elif opt == 'artistloop': 
					self.opts['artistloop'] = parseBoolean(value, False)
					
				elif opt == 'autoswitchnp': 
					try:
						self.opts['autoswitchnp'] = int(value)
					except:
						print "Invalid auto switch now playing value (%s) - defaulting to 120" % value
						self.opts['autoswitchnp'] = 120
					
				elif opt == 'screensaver': 
					try:
						self.opts['screensaver'] = int(value)
					except:
						print "Invalid screen saver timeout (%s) - defaulting to 600" % value
						self.opts['screensaver'] = 600
					
				elif opt == 'lyricindent': 
					try:
						self.opts['lyricindent'] = int(value)
					except:
						print "Invalid lyric indent value (%s) - must be > -1 - defaulting to -1" % value
						self.opts['lyricindent'] = -1
					
				else:
					print "Ignoring invalid option (%s) in ini file", opt
					
		else:
			raise ConfigError("[jukebox] section missing in config file")

		if pytivo == None:
			raise ConfigError("Error - PyTivo configuration location not specified in config file")
		
		self.loadPyTivoConfig(pytivo)
		
		if self.opts['serverport'] == None and not BuildingCache:
			raise ConfigError("Error - server port missing in config file")
		
		if len(self.opts['containers']) == 0:
			raise ConfigError("Error - pyTivo is not serving any music shares")
		
		return self.opts

	def loadPyTivoConfig(self, cf):
		pyconfig = ConfigParser.ConfigParser()
		if not pyconfig.read(cf):
			raise ConfigError("ERROR: pyTivo config file " + cf + " does not exist.")

		if self.opts['serverport'] == None:
			if pyconfig.has_option('Server', 'port'):
				self.opts['serverport'] = pyconfig.get('Server', 'port')

		containers = []		
		for section in pyconfig.sections():
			if pyconfig.has_option(section, "type") and pyconfig.get(section, "type") == "music" and pyconfig.has_option(section, 'path'):
				path = pyconfig.get(section, 'path')
				containers.append((section, path))
				
		self.opts['containers'] = containers

	def save(self, opts):
		changes = False
		for k in opts:
			saveOpt = False
			if k not in self.loaded:
				if k in self.defaults and opts[k] != self.defaults[k]:
					# it was not loaded, but has changed value
					saveOpt = True
				
			elif self.loaded[k] != opts[k]:
				# it was loaded and has changed value
				saveOpt = True
				
			if saveOpt:
				if not self.cfg.has_section(SECTIONNAME):
					self.cfg.add_section(SECTIONNAME)
				
				self.cfg.set(SECTIONNAME, k, str(opts[k]))
				self.loaded[k] = opts[k]
				changes = True
			
		if changes:
			cfp = open(self.fn, 'wb')
			self.cfg.write(cfp)
			cfp.close()
