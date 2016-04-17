build: *.py *.md *.xml *.png resources/
	# copy over plugin structure into a folder
	mkdir -p plugin.video.youtubetv
	cp *.py plugin.video.youtubetv
	cp *.md plugin.video.youtubetv
	cp *.xml plugin.video.youtubetv
	cp -r resources/ plugin.video.youtubetv
	# output the addon into a zipfile so it can be installed
	zip -r -9 YoutubeTV.zip plugin.video.youtubetv/ 
install: build
	cp -rv plugin.video.youtubetv ~/.kodi/addons/
log:
	less ~/.kodi/temp/kodi.log
clean:
	# clean up build directories
	rm YoutubeTV.zip
	rm -rv plugin.video.youtubetv
