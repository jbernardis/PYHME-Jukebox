Jukebox 1.0

Jukebox is a TiVo HME based MP3 player written in python and designed to be run under wmcbrine's pyhme framework.  Although
pyhme also provides an HTTP server, it is a very simple one, and does not support trickplay. Because of this
(and at wmcbrine's suggestion) I have chosen to use the pyTivo server to actually serve the mp3 files to the tivo.  Thus,
jukebox only works if you are running pyTivo.

Many of the design cues for Jukebox came directly from Harmonium, and I want to acknowledge that product and it authors.  
I have used harmonium for several years, but I wasn't happy about running it on my PC.  I wanted it to run on my Netgear
ReadyNAS where I already run pyTivo as well as pyhme/vidmgr.  However, my NAS doesn't have a Java Runtime Environment,
and I was reluctant to install one.  So instead I decided to write my own in python under pyhme.

One up front note - Jukebox is only as good as the quality of the metadata that you have in your MP3 files.  It uses the
following fields:
	title - the name of the song
	album name - the name of the album
	album artist - the name of the artist for the album
	track artist - the name of the artist for the track
	track number - only used to determine play order for albums
	genre - loaded into database, but not presently used
	artwork - at present, jukebox only supports jpg artwork.  If missing a default image is used
	
About the artist names: the album artist name and the track artist name can indeed be
different.  The logic for loading these values is as follows: 1) assign the album
artist a value of UNKNOWN.  2) If the album artist is present in the mp3 file use that value instead.  3) assign
the value of the album artist to the track artist. 4) if the track artist is present in the MP3 file, 
use that value instead. 5) if the album artist is UNKNOWN, assign the current value of the track artist to the
album artist.

About the artwork: in order to save space, artwork is only stored within the jukebox cache associated with the album.
This differs from the fact that each MP3 file has its own artwork (potentially).  The way jukebox handles this is
that it saves the artwork for the FIRST file that it processes for each album.

The bottom line of all of this is - Make sure you have clean metadata.  The usefulness of the
various indices within Jukebox will be diminished if all of the songs show up under
one album named UNKNOWN.


INSTALLATION
===========================================================================

To install jukebox, do the following:

1) in your pyhme directory, create a subdirectory named jukebox.  You must also configure pyhme to run this app, 
   either by adding "jukebox" to the "apps" line in config.ini, or by removing this line altogether from the config.ini
   file.  See the instructions that come with pyhme

2) in the jukebox subdirectory, unload the zip file.  You should have a bunch of .py files and icon.png.  You should 
   also have a directory named skins that contains a bunch of .png files.

3) the BuildCache.py program needs two third party python packages: The python Image library(PIL), and mutagen.  Both 
   of these are available on the web (URLs).  Download and install them.  Alternatively for mutagen, this is distributed
   with pyTivo, and is installed into a directory below pyTivo.  If you do not install this package from the web, you
   will need to link/copy the directory that exists under pyTivo into the jukebox directory (i.e. the jukebox directory
   should have a mutagen directory, and all of the mutagen files should be in that directory)

4) in the jukebox subdirectory create a directory named "playlists".  Make sure it is writeable by the user ID you
   will be using to run pyhme/jukebox

5) configure jukebox by editing/creating the jukebox.ini file.  Look at jukebox.ini.dist for instructions/examples

6) Manually create the cache - in the jukebox subdirectory, run "python BuildCache.py".  This will take a while.
   It prints out a '.' every 100 mp3 files it processes.  My collection of just under 3300 files takes about 6
   minutes to process.  You might want to schedule a periodic job to rebuild the cache, or you can decide to rebuild
   it only when you make changes to your music collection.

7) start/restart pyhme.  Jukebox should now appear on your Tivo


USAGE
================================================================================================================

Jukebox allows you to step through your music collection in a hierarchical fashion.  At the top level are 6 main menu choices:

1) Browse playlists allows you to browse through your playlists.  You can delete songs from a playlist, reorder your songs
within a playlist, or shuffle the songs within a playlist.  You can also play a playlist or add it to the end of the
"Now Playing" playlist.

2) Browse Album Artists.  This breaks down your albums by album artist.  First choose an artist, and then choose an album
by that artist.  For albums, you can play them, add them to a playlist, or open them up to examine the songs.  For songs,
you can play them, add them to a playlist, play their album starting at the first track, play their album starting with
that song, or add their album to a playlist.

3) Browse Albums.  This is an alphabetical listing of albums, irrespective of the album artist.  Same options as above for
albums and songs.

4) Browse Track Artists.  Although in most cases the album artist is the same as the track artist, this allows for
situations where this is not the case.  This shows a list of track artists, and once one is chosen, an alphabetical
listing of their songs - irrespective of which album they are on.  For a specific artist, you can play all of their songs,
add all of their songs to a playlist, or open up a list of their songs to choose songs individually.  For individual songs,
you can either play them, add them to a playlist, add their artist to a playlist, or add their album to a playlist

5) Browse Tracks.  This is simply an alphabetical listing of ALL songs in your collection, irrespective ot the artist or
album.  At the main menu level, you can choose to play your entire collection.  For an individual song, you can either play
it, add it to a playlist, add its artist to a playlist, or add its album to a playlist.

6) Set Preferences allows you to set your preferences for shuffle and loop for albums, artists, tracks, and playlists.

If music is currently playing, a 7th menu item will be presented: Now Playing.  You can either switch back to the Now Playing
screen, or save the Now Playing list as a normal playlist.  Note that other than adding to the now playing list, you cannot
really edit it.  This was a simplifying decision I made, and I don't think it too onerous.  If you really want to make
changes to the Now Playing list, save it as a normal playlist and then edit that.  Once you make your edits, you can then
play it.


While browsing through the various track/album/artist lists, you can use the normal up/down/page up/page down
to do your navigation.  Also, fast forward moves forward until a new first character is
found (i.e. from the 'A' titles to the 'B' titles).  rewind does the same backwards.  Any other possible actions
are shown on the bottom of the screen.  In general, play will start playing the current
song/album/artist, and enter will add it to a playlist.  There may be other choices depending on the context;
these are shown on screen.   


NOW PLAYING SCREEN
=========================================================================================================

When music is playing, you are normally presented with the Now Playing screen.  This screen shows information on the current
track, what track is next, a slider showing play progress, and the status of the playback options.  There are three playback
options under your control:

shuffle - mixes up the current playlist.  If you turn shuffle off you may actually miss songs because they actually
occur BEFORE the current song in the normal play sequence.

repeat - repeats the currently playing track.

loop - replays the now playing list after it is completed.

These options can be controlled by pressing 1, 2, and 3 respectively (as stated on the screen)

You can leave the Now Playing screen to browse your collection and add songs to the now playing list by pressing left.

Channel Up or the advance button moves you forward a track.

Channel Down or the replay button moves you to the beginning of the current track or, if you are less than 5 seconds into the
current track, to the previous track.

The FF and RW buttons allow you to move quickly through the song being played at 3 different speeds.  There is no audio
while this is happening.

Pause alternatively pauses/resumes a song; play will also resume playing.


Jukebox also has certain idle behavior.  

-If music is playing and you are browsing the music collection, and there is no user input for 2 minutes, the program will
automatically switch back to the Now Playing screen.

-Regardless of which screen is showing, if there is no user input for 10 minutes, the screen will be blanked.

These time periods can be changed via options in the jukebox.ini file.  

Note: these time periods are not exact.  Jukebox only checks once every minute for these conditions.  Thus is could be up
to 1 full minute beyond these conditions occurring before the action takes place.

