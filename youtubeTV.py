import urllib
import os
import subprocess
import datetime
# session class for youtubeTV session starting
class session():
	def __init__():
		'''This object loads up the youtubeTV session for cache functionality and automated work.'''
		# create the cache for this session
		self.cache={}
		# cache timer
		self.timer={}
		# load the channels config
		loadChannelsConfig('~/.kodi/userdata/addon_data/plugin.video.youtubeTV/channels.cfg')
	def grabCache():
		# return the cache in its current state
		return self.cache
	def loadChannelsConfig(configPath):
		# store the config path
		self.configPath=configPath
		# open the config file
		fileObject=open(configPath,'r')
		# create array for channels to be stored in
		self.channels=[]
		# append each line to an array for all channels
		for line in fileObject:
			# append lines to channels
			self.channels.append(line.strip())
	def addChannel(channelUsername):
		# check if username is already in channels
		if channelUserName not in self.channels:
			# add username to channels
			self.channels.append(channelUserName)
		else:
			# end execution since it would be a dupe
			return
		# open configfile to input updates
		fileObject=open(self.configPath,'w')
		# write all changes back to the file
		for channel in self.channels:
			# write new channel to file
			fileObject.write(channel+'\n')
	def checkTimer(userName):
		if userName in self.timer.keys():
			# update videos if videos were updated more than an hour ago
			if self.timer[userName]<datetime.datetime.now():
				# if the timer is over an hour old everything needs updated
				return True
			else:
				# update datetime for username to be one hour from now
				return False
		else:
			# update all the videos no cache exists
			return True
	def getUserVideos(userName):
		# check the timer on the username
		if checkTimer(userName):
			# reset the timer and refresh the program list
			self.timer[userName]=datetime.datetime.now()+datetime.timedelta(hours=1)
		else:
			# end the program and use the cached version of the video list
			return
		# get the youtube users webpage
		webpageText=urllib.urlopen("https://www.youtube.com/user/"+str(userName)+"/videos")
		temp=''
		for line in webpageText:
			# mash everything into a string because they use code obscification
			# also strip endlines to avoid garbage
			temp+=(line.strip())
		# split page based on parathensis since we are looking for video play strings 
		webpageText=temp.split('"')
		# create an array to hold the video watch strings
		videos=[]
		# run though the split text array looking for watch strings in lines
		for line in webpageText:
			if '/watch?v=' in line:
				# create real youtube url from found strings
				temp='https://youtube.com'+str(line)
				# avoid duplicate entries
				if temp not in videos:
					# add video if it does not exist in the file already
					videos.append(temp)
		# generate the data for drawing videos in kodi menu
		for video in videos:
			temp={}
			# set the video url to the found url
			temp['video']=video
			# if cached version exists for the video shown dont update it
			if video not in self.cache[userName].keys() 
				# find the video title using youtube-dl
				title=subprocess.Popen(['youtube-dl', '--get-title',str(video)],stdout=subprocess.PIPE)
				title=title.communicate()[0].strip()
				# set the title
				temp['name']=title
				# get the thumbnail url
				thumbnail=subprocess.Popen(['youtube-dl', '--get-thumbnail',str(video)],stdout=subprocess.PIPE)
				thumbnail=thumbnail.communicate()[0].strip()
				# set the thumbnail
				temp['thumb']=thumbnail
				# set the genre to youtube
				temp['genre']='youtube'
				# set user data in the cache
				self.cache[userName]=temp
# try reading yogscast videos
listUserVideos('bluexephos')
