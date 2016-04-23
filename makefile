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
	# copy the test chanels into the plugin
	mkdir -p ~/.kodi/userdata/addon_data/plugin.video.youtubetv/
	cp channels ~/.kodi/userdata/addon_data/plugin.video.youtubetv/
log:
	less ~/.kodi/temp/kodi.log
debug:
	#cat ~/.kodi/temp/kodi.log | grep 'NOTE:*End of Python script error report'
	tail -f ~/.kodi/temp/kodi.log | grep "NOTICE:"
	#less ~/.kodi/userdata/addon_data/plugin.video.youtubetv/debug
clean:
	# clean up build directories
	rm YoutubeTV.zip
	rm -rv plugin.video.youtubetv
