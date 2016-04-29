build: *.py *.md *.xml *.png resources/
	# copy over plugin structure into a folder
	mkdir -p plugin.video.youtubetv
	cp *.py plugin.video.youtubetv
	cp *.png plugin.video.youtubetv
	cp *.md plugin.video.youtubetv
	cp *.xml plugin.video.youtubetv
	cp -r resources/ plugin.video.youtubetv
	# make build directory read only
	#chmod go-w -R plugin.video.youtubetv
	#chmod go+xr -R plugin.video.youtubetv
	#chmod u+rwx -R plugin.video.youtubetv
	# output the addon into a zipfile so it can be installed
	zip -r -9 YoutubeTV.zip plugin.video.youtubetv/ 
install: build
	# copy the plugin into the current kodi config
	cp -rv plugin.video.youtubetv ~/.kodi/addons/
uninstall: reset
	# remove the addon and the addon data
	rm -rv ~/.kodi/addons/plugin.video.youtubetv
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
reset:
	# reset the settings to default
	rm -rv ~/.kodi/userdata/addon_data/plugin.video.youtubetv
