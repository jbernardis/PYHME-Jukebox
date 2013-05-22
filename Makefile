SRC = *.py icon.png
SKN = skins/*.png

all: install 

install : .installpy .installskin

.installpy : $(SRC)
	mkdir -p /usr/local/pyhme/jukebox
	cp $? /usr/local/pyhme/jukebox
	touch .installpy

.installskin : $(SKN)
	mkdir -p /usr/local/pyhme/jukebox/skins
	cp $? /usr/local/pyhme/jukebox/skins
	touch .installskin

