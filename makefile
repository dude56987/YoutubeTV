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
	# remove build directory
	rm -rv plugin.video.youtubetv 
install: build
	# copy the plugin into the current kodi config
	unzip -o YoutubeTV.zip -d ~/.kodi/addons/
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
	rm YoutubeTV.zip || echo "No plugin package to remove."
	rm -rv plugin.video.youtubetv || echo "No build directory to remove."
	# also try to remove reports that exist
	rm -rv report || echo "No Reports to remove."
reset:
	# reset the settings to default
	rm -rv ~/.kodi/userdata/addon_data/plugin.video.youtubetv
	# install the plugin again
	make install
project-report: .git/*
	sudo apt-get install gitstats gource --assume-yes
	rm -vr report/ || echo "No existing report..."
	mkdir -p report
	mkdir -p report/webstats
	# write the index page
	echo "<html style='margin:auto;width:800px;text-align:center;'><body>" > report/index.html
	echo "<a href='webstats/index.html'><h1>WebStats</h1></a>" >> report/index.html
	echo "<a href='log.html'><h1>Log</h1></a>" >> report/index.html
	echo "<video src='video.mp4' width='800' controls>" >> report/index.html
	echo "<a href='video.mp4'><h1>Gource Video Rendering</h1></a>" >> report/index.html
	echo "</video>" >> report/index.html
	echo "</body></html>" >> report/index.html
	# write the log to a webpage
	echo "<html><body>" > report/log.html
	echo "<h1><a href='index.html'>Back</a></h1>" >> report/log.html
	# generate the log into a variable
	git log --stat > report/logInfo
	echo "<code><pre>" >> report/log.html
	cat report/logInfo >> report/log.html
	echo "</pre></code>" >> report/log.html
	rm report/logInfo
	echo "</body></html>" >> report/log.html
	# generate git statistics
	gitstats -c processes='8' . report/webstats
	# generate a video with gource
	gource --max-files 0 -s 1 -c 4 -1280x720 -o - | avconv -y -r 60 -f image2pipe -vcodec ppm -i - -vcodec libx264 -preset ultrafast -pix_fmt yuv420p -crf 1 -threads 8 -bf 0 report/video.mp4
	# open report and clear terminal
	exo-open report/index.html &
	clear
