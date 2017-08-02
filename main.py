#########################################################################
# YoutubeTV Kodi addon for viewing Youtube channels
# Copyright (C) 2016  Carl J Smith
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
########################################################################
# ATTRIBUTIONS
########################################################################
# - Initial code base adapted from template by Roman V. M.
# - Icons are from Bromix's Kodi addon for Youtube
########################################################################
import sys
from urlparse import parse_qsl
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
###################
import urllib2
import os
import subprocess
import datetime
import pickle
import HTMLParser
################################################################################
def findText(start,end,searchString):
	'''
	Grab text between start and end strings within the
	searchString.

	return string
	'''
	# find the start index of the startstring
	start=searchString.find(start)+len(start)
	# middle cut
	firstCut=searchString[start:]
	# find then end string index
	end=firstCut.find(end)
	# cut the end off
	temp=firstCut[:end]
	# return the middle
	return temp
################################################################################
def saveFile(fileName,content):
	'''
	Save a file with the path fileName containing the content content.

	:return None
	'''
	# create the basepath using special protocol
	basePath=('special://userdata/addon_data/'+_id+'/')
	basePath=xbmc.translatePath(basePath)
	# if the base config directory does not exist
	if os.path.exists(basePath) is False:
		# create the base config path
		thumbnail=subprocess.Popen(['mkdir', '-p',basePath])
	# open the file to write
	fileObject=open((basePath+fileName),'w')
	# write file content
	fileObject.write(content)
	# close the file
	fileObject.close()
################################################################################
def loadFile(fileName):
	'''
	Load a file with the path fileName.

	Returns the loaded file as a string or if the
	file fails to load return False.

	:return bool/string
	'''
	# this is where all files related to the plugin will be stored
	basePath=('special://userdata/addon_data/'+_id+'/')
	basePath=xbmc.translatePath(basePath)
	# concat the basepath and file fileName for the file to load
	path=(basePath+fileName)
	# check if the config file exists already
	if os.path.exists(path):
		# open the file to write
		fileObject=open(path,'r')
		# temp string to hold file content
		temp=''
		# read each line into a string
		for line in fileObject:
			temp+=line
		# return the contents of the file as a string
		return temp
		# return the string text of the file
		#return fileObject.read()
	else:
		# return false if the file is not found
		return False
def popup(header,content):
	'''
	Display a toaster style popup with the header of header and
	the content of content.
	'''
	dialog=xbmcgui.Dialog()
	dialog.notification(header,content,_basedir+'icon.png')
################################################################################
# session class for youtubeTV session starting
class YoutubeTV():
	def __init__(self):
		'''
		This object loads up the youtubeTV session for
		cache functionality and automated work.
		'''
		# create the cache for this session
		self.cache=tables.table(_datadir+'cache/')
		# cache timer
		self.timer=tables.table(_datadir+'timer/')
		# load the channels cache
		self.channelCache=tables.table(_datadir+'channelCache/')
		# playlist cache
		self.playlistCache=tables.table(_datadir+'playlistCache/')
		# webpage cache
		self.webCache=tables.table(_datadir+'webCache/')
	def saveConfig(self,config,newValue):
		'''
		Convert objects into strings and save in xbmc settings
		for the addon.

		:return None
		'''
		# convert the new value into a string for storage
		temp=pickle.dumps(newValue)
		# write new config back to the addon settings
		#self.saveFile(config,temp)
		addonObject.setSetting(config,temp)
		#xbmcplugin.setSettings(_handle,config,temp)
	def loadConfig(self,config,blankType):
		'''
		Used for loading objects from xbmc settings that were
		stored using pythons pickle functionality.

		:return array/dict
		'''
		# open the pickled settings using xbmcs settings api
		configObject=addonObject.getSetting(config)
		#configObject=xbmcplugin.getSettings(_handle,config)
		#configObject=self.loadFile(config)
		if bool(configObject):
			# if config exists load up the config into channels
			return pickle.loads(configObject)
		else:
			if blankType=='array':
				# otherwise create a blank array
				return []
			elif blankType=='dict':
				# return a blank dict
				return {}
			else:
				# default to return an array
				return []
	def addChannel(self,channelUsername):
		'''
		Add a channel with channelUsername to the cache.

		return None
		'''
		# check if username is already in channels
		if channelUsername not in self.cache.names:
			# add username to channel cache as a empty list
			self.cache.saveValue(channelUsername,list())
		else:
			# end execution since it would be a dupe
			return
	def resetChannel(self,channelUsername):
		'''
		Delete channel cache information, and redownload
		all channel videos.

		:return None
		'''
		# remove the cached channel information
		self.removeChannel(channelUsername)
		# add the channel back
		self.addChannel(channelUsername)
		popup('YoutubeTV','Channel '+channelUsername+' reset')
	def removeChannel(self,channelUsername):
		'''
		Remove channel with username channelUsername.

		:return None
		'''
		# check if channel exists in channels
		if channelUsername in self.cache.names:
			# remove the channel from the cache
			self.cache.deleteValue(channelUsername)
			# if channel has playlists in cache
			if channelUsername in self.playlistCache.names:
				# delete the playlists for the channel
				self.playlistCache.deleteValue(channelUsername)
			# delte the channel timer
			#del self.timer[channelUsername]
			self.timer.deleteValue(channelUsername)
			# delete the channel playlist timers
			#for timer in self.timer.keys():
			killArray=[]
			for timer in self.timer.names:
				if channelUsername+':' in timer:
					killArray.append(timer)
					#del self.timer[timer]
			for item in killArray:
				self.timer.deleteValue(item)
		# save the changes to the data
		xbmc.executebuiltin('container.Update('+_url+',replace)')
		popup('YoutubeTV','Channel '+channelUsername+' removed')
	def checkTimer(self,userName,delay):
		'''
		Checks timer on username to see if videos in that channel have been
		refreshed within the past hour.
		True means the timer says the video needs refreshed.

		:param delay:string
		:param userName:string

		:return bool
		'''
		# grab the timer value, and cast the value to a int
		refreshDelay=addonObject.getSetting(delay)
		refreshDelay=int(refreshDelay)
		#if userName in self.timer.keys():
		if userName in self.timer.names:
			# update videos if videos were updated more than an hour ago
			#if self.timer[userName]<datetime.datetime.now():
			if self.timer.loadValue(userName)<datetime.datetime.now():
				# if the timer is over an hour old everything needs updated
				#############
				# update the timer to only update one hour from now
				#self.timer[userName]=datetime.datetime.now()+datetime.timedelta(hours=refreshDelay)
				tempTime=datetime.datetime.now()+datetime.timedelta(hours=refreshDelay)
				self.timer.saveValue(userName,tempTime)
				# save timer changes
				#self.saveConfig('timer',self.timer)
				return True
			else:
				# the timer has been reset within the last hour
				return False
		else:
			# the username has not time logged for last update
			# this means no cache exists, and all videos need updated
			#############
			# update the timer to only update one hour from now
			#self.timer[userName]=datetime.datetime.now()+datetime.timedelta(hours=1)
			tempTime=datetime.datetime.now()+datetime.timedelta(hours=1)
			self.timer.saveValue(userName,tempTime)
			# save timer changes
			#self.saveConfig('timer',self.timer)
			return True
	def cleanText(self,inputText):
		'''
		Takes inputText and clean up the html special charcters.

		:return string
		'''
		# decode the inputText
		inputText=inputText.decode('utf8')
		okList='abcdefghijklmnopqrstuvwxyz'
		okList+='ABCDEFGHIJKLMNOPQRSTUVWXYZ'
		okList+="1234567890!@#$%^&*()-_+=[]{}/' "
		okList+=':;"?.,><`~|'
		tempString=''
		# ignore all characters not in the ok list
		for character in inputText:
			if character in okList:
				tempString+=character
		# convert all html entities in the title to unicode charcters
		tempString=HTMLParser.HTMLParser().unescape(tempString)
		return tempString
	def refreshCache(self):
		'''
		Refresh all channels stored in the plugin cache.

		:return None
		'''
		# get list of channels to update cache
		for channel in self.cache.names:
			# refresh all videos in channel
			self.getUserVideos(channel)
	def channelPlaylists(self,channelName,display=True):
		'''
		Grab the playlists for a channel with the username channelName.

		Returns a dict with keys that are the playlist ids.

		:param channelName:string
		:param display:bool

		:return dict
		'''
		# the cache stores channels as the identifyer for an
		# dict that uses all the playlists as identifyers
		# The playlist identifer holds a dict containing
		# a title, thumbnail and array. The array holds a list
		# of videos that can be played
		# check timer for the channelPlaylists
		if self.checkTimer(channelName+':playlists','channelPlaylistDelay') is True:
			# timer has rang, entry needs updated

			# if no playlist entries exist for this channel
			# create a blank entry
			if channelName not in self.playlistCache.names:
				#self.playlistCache[channelName]={}
				self.playlistCache.saveValue(channelName,dict())
			# grab a list of all the playlists for this channel
			results=self.cacheWebpage("https://www.youtube.com"+channelName+"/playlists")
			results=results.split('"')
			paths=[]
			# create an array of all the playlist ids
			for line in results:
				if '/playlist?list=' in line:
					paths.append(line.replace('/playlist?list=',''))
			# create the progress bar
			progressDialog=xbmcgui.DialogProgress()
			progressDialog.create(('Reading playlists for '+channelName),'Processing...')
			progressTotal=float(len(paths))
			progressCurrent=0.0
			# for each playlist id
			for playlistId in paths:
				# check if the cancel button was pressed
				if progressDialog.iscanceled():
					# cancel execution and delete timer value to pervent
					# partially loaded list
					self.timer.deleteValue(channelName+':playlists')
					return
				# if the playlist does not exist yet
				if playlistId not in self.playlistCache.loadValue(channelName).keys():
					# create a entry in the playlist cache
					temp=self.playlistCache.loadValue(channelName)
					# create the playlist id dict
					temp[playlistId]={}
					# add a blank array value
					temp[playlistId]['array']=[]
					self.playlistCache.saveValue(channelName,temp)
					# update the playlist title and grab all videos in the
					# playlist to store them in the cache
					self.grabPlaylist(playlistId,channelName,display=None,firstOnly=True)
				# grab the title of the playlist last being worked on
				title=self.playlistCache.loadValue(channelName)[playlistId]['name']
				# draw the progress onscreen
				progressDialog.update(int(100*(progressCurrent/progressTotal)),title)
				# increment the progress
				progressCurrent+=1
		# if the function should display items onscreen
		if display==True:
			# create a list for all the buttons to be stored in before
			# drawing them onscreen
			listing=[]
			# for each playlist in the playlist cache create a button
			for key in self.playlistCache.loadValue(channelName).keys():
				# grab the playlist id
				playlistId=key
				# set the title to the cached playlist title
				title=self.playlistCache.loadValue(channelName)[key]['name']
				# set the thumbnail to the first entry in the playlist
				thumb=self.playlistCache.loadValue(channelName)[key]['array'][0]['thumb']
				# create a button for each playlist to display that playlist
				action=('viewPlaylist&channel='+channelName+'&playlist='+playlistId)
				temp=createButton(action=action,\
						title=title,\
						thumb=thumb,\
						icon=thumb,\
						fanart=thumb)
				listing.append(temp)
			# save the playlists into the playlist cache
			#self.saveConfig('playlistCache',self.playlistCache)
			xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
			# change the default view to thumbnails
			xbmc.executebuiltin('Container.SetViewMode(%d)' % 500)
			# Finish creating a virtual folder.
			xbmcplugin.endOfDirectory(_handle)
	def grabPlaylist(self,playlistId,channelName,display=True,firstOnly=False):
		'''
		Grab the playlist items for a playlist "playlistId" that is a
		playlist of the "channelName"

		Returns an array of all the videos in a playlist

		:param playlistId:string
		:param channelName:string
		:param display:bool

		:return array
		'''
		if firstOnly==True:
			# if firstonly is set dont check the timer, just grab the first value
			tempTimerValue=True
		else:
			# if the timer is true then the playlist needs refreshed
			tempTimerValue=self.checkTimer(channelName+":"+playlistId,'playlistDelay')
		if tempTimerValue:
			# create the runplugin button to list the playlist
			playlistList=self.cacheWebpage('https://www.youtube.com/playlist?list='+playlistId)
			# grab title of the playlist from the downloaded file
			title=findText('<title>','</title>',playlistList)
			# replace the youtube part in the title text
			title=title.replace('- YouTube','')
			title=self.cleanText(title)
			# set the title in the cache
			tempPlaylistCache=self.playlistCache.loadValue(channelName)
			tempPlaylistCache[playlistId]['name']=title
			# for each item in the playlist cache the data
			for item in playlistList.split('<tr class="pl-video yt-uix-tile'):
				title=findText('data-title="','"',item)
				title=self.cleanText(title)
				video=findText('data-video-id="','"',item)
				thumb=findText('data-thumb="','"',item)
				# if video id is not a dupe and does not contain any html
				if video not in str(tempPlaylistCache[playlistId]['array']) and\
				'><' not in video:
					# begin building dict to add to the category array
					temp={}
					# set the video url to the found url
					temp['video']=video
					# set the title
					temp['name']=title
					# set the thumbnail, add http to make the address resolve
					if "http" not in thumb:
						# if https is not in the path add it
						temp['thumb']="https:"+thumb
					else:
						# make sure the thumb uses https links
						if "http://" in thumb:
							thumb = thumb.replace('http://','https://')
						# add the path
						temp['thumb']=thumb
					# set the genre to youtube
					temp['genre']='youtube'
					# add the found playlist items to the playlist array value
					tempPlaylistCache[playlistId]['array'].append(temp)
					if firstOnly==True:
						# if firstonly is set only cache the first video
						# and return the function
						self.playlistCache.saveValue(channelName,tempPlaylistCache)
						return
			# save videos to the playlistcache
			self.playlistCache.saveValue(channelName,tempPlaylistCache)
		# if display is set to true then draw this playlist onscreen
		if display==True:
			# create a list for all the buttons to be stored in before
			# drawing them onscreen
			listing=[]
			# create a play all button
			action=('playAll&channel='+channelName+'&playlist='+playlistId)
			thumb=(_resdir+'/media/playAll.png')
			temp=createButton(action=action,title='Play All', thumb=thumb,\
				icon=thumb,fanart=thumb,is_folder=False)
			listing.append(temp)
			# for each video in the playlist array
			for item in self.playlistCache.loadValue(channelName)[playlistId]['array']:
				# set the title to the cached playlist title
				title=item['name']
				# set the thumbnail to the cached thumbnail
				thumb=item['thumb']
				# create a button to add the channel in the results
				action=('play&video='+item['video'])
				temp=createButton(action=action,\
						title=title,\
						thumb=thumb,\
						icon=thumb,\
						fanart=thumb,\
						is_folder=False)
				listing.append(temp)
			xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
			# change the default view to thumbnails
			xbmc.executebuiltin('Container.SetViewMode(%d)' % 500)
			# Finish creating a virtual folder.
			xbmcplugin.endOfDirectory(_handle)
	def grabChannelMetadata(self,channel):
		'''
		Takes a channel in the form of /user/username or /channel/hashvalue
		as a string. Downloads the webpage of the channel into the cache.
		Then reads the channels metadata into the channelCache for later
		use.
		'''
		# if the channel timer has expired or the channel does not
		# yet exist in the cache we need to update the channel data
		if self.checkTimer(channel+':meta','channelMetadataDelay') or\
		channel not in self.channelCache.names:
			# if channel is not in the cache then grab info from the website
			##############
			# user channel information can be found by downloading the
			# user channel page with
			#"https://youtube.com"userName
			channelPage=self.cacheWebpage("https://www.youtube.com"+channel)
			# jerk out the banner image from the downloaded user webpage
			try:
				temp=channelPage.split('.hd-banner-image {background-image: url(//')
				temp=temp[1]
				temp=temp.split(');')
				# append https to the picture so it will work
				fanArt="https://"+temp[0]
			except:
				# if this does not work set the fanart to none
				fanArt='none'
			# split the page based on tag opening
			channelPage=channelPage.split("<")
			for tag in channelPage:
				# the channels metadata is stored in a image tag for the users
				# profile picture, so search for
				#'class="channel-header-profile-image"'
				if 'class="channel-header-profile-image"' in tag:
					# inside this string you will have two important variables
					# - first src="" will have the icon you should use for the channel
					# - second title="" will have the human readable channel title
					# you should store these things in the cache somehow to use them
					# when rendering the channels view
					# grab text in src attribute between parathenesis
					icon=tag.split('src="')
					icon=icon[1].split('"')
					icon=icon[0]
					# if a generated channel uses the other wierd icon format
					if icon[:2]=='//':
						icon='https:'+icon
					# grab text in title attribute for channel title
					title=tag.split('title="')
					title=title[1].split('"')
					title=title[0]
					# clean html entities from title
					title=self.cleanText(title)
					# add channel information to the channel cache
					tempChannelCache=dict()
					# add title and icon
					tempChannelCache['title']=title
					tempChannelCache['icon']=icon
					tempChannelCache['fanArt']=fanArt
					self.channelCache.saveValue(channel,tempChannelCache)
	def searchChannel(self,searchString):
		# clean the search string of spaces
		cleanSearchString = searchString.replace(' ','+')
		# grab the channel cache limit setting
		channelLimit=addonObject.getSetting('channelLimit')
		channelLimit=int(channelLimit)
		# number of channels to delete from the cache
		deleteCounter=self.channelCache.length-channelLimit
		# ignore limit if value is zero
		if channelLimit != 0:
			# for each channel in the channel cache check
			# if the channel has been added by the user
			for channelTitle in self.channelCache.names:
				# if channel is not a user added channel
				if channelTitle not in self.cache.names:
					# if the delete counter is still above 0
					if deleteCounter>0:
						# delete the channel from the cache
						self.channelCache.deleteValue(channelTitle)
						# decrement the delete counter
						deleteCounter-=1
		# searches on youtube can be placed with the below string
		# add your search terms at the end of the string
		#"https://www.youtube.com/results?search_query="
		searchResults=self.cacheWebpage("https://www.youtube.com/results?search_query="+cleanSearchString)
		# to do next page you can add page=2 to the request

		# users can be found by scanning the search results for
		#'href="/user/'userName'"'
		searchResults=searchResults.split('"')
		temp=[]
		for link in searchResults:
			link = link.replace('https://www.youtube.com','')
			link = link.replace('https://youtube.com','')
			link = link.strip()
			# if the link is a link to a channel
			if '/user/' in link:
				link=link[link.find('/user/'):]
				# do not add duplicate entries found in the search
				if link not in temp:
					# add the link
					temp.append(link)
			elif '/channel/' in link:
				link=link[link.find('/channel/'):]
				# do not add duplicate entries found in the search
				if link not in temp:
					# add the link
					temp.append(link)
		# create and check the blocklist
		blocklist=[]
		blocklist.append('doubleclick.net')
		blocklist.append('https://')
		blocklist.append('http://')
		blocklist.append('><')
		blocklist.append('/?')
		# check for and remove blocklist items from searchResults
		for link in temp:
			for blockItem in blocklist:
				if blockItem in link:
					temp.remove(link)
		# search results is now a array of usernames
		# cut first 9 items because they are youtube menus
		searchResults=temp[9:]
		# we can take the usernames and use them to grab the user channel information
		# listing for creating directory
		listing=[]
		# create the progress bar
		progressDialog=xbmcgui.DialogProgress()
		progressDialog.create(('Searching Channels for '+searchString),'Processing...')
		progressTotal=float(len(searchResults))
		progressCurrent=0.0
		for channel in searchResults:
			# check if the cancel button was pressed
			if progressDialog.iscanceled():
				# break the loop and load the channels found thus far
				break
			# update the progress dialog
			progressDialog.update(int(100*(progressCurrent/progressTotal)),channel)
			progressCurrent+=1
			# grab the channel metadata
			self.grabChannelMetadata(channel)
			# load up the channel values from the cache
			title=self.channelCache.loadValue(channel)['title']
			icon=self.channelCache.loadValue(channel)['icon']
			fanArt=self.channelCache.loadValue(channel)['fanArt']
			# create a button to add the channel in the results
			temp=createButton(action=('addChannel&value='+channel),\
					title=title,\
					thumb=icon,\
					icon=icon,\
					fanart=fanArt)
			# add context menu actions
			contextItems=[]
			# remove category button
			contextItems.append((('Add Channel '+title),'RunPlugin('+_url+'?action=addChannel&value='+channel+')'))
			contextItems.append((('End Search'),'RunPlugin('+_url+'?action=main)'))
			# listing item is second item in a tuple, so we add the context menu
			# to the listing item stored in temp
			temp[1].addContextMenuItems(contextItems)
			# add the item
			listing.append(temp)
		# add items to listing
		xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
		# Add a sort method for the virtual folder items (alphabetically, ignore articles)
		#xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
		# change the default view to thumbnails
		xbmc.executebuiltin('Container.SetViewMode(%d)' % 500)
		# Finish creating a virtual folder.
		xbmcplugin.endOfDirectory(_handle)
	def grabWebpage(self,url):
		'''
		Download the url, strip line endings, and return a string.
		'''
		userAgent=addonObject.getSetting('userAgent')
		header = {'User-Agent': userAgent,
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
		'Accept-Encoding': 'none',
		'Accept-Language': 'en-US,en;q=0.8',
		'Connection': 'keep-alive'}
		requestObject = urllib2.Request(url,headers=header)
		# get the youtube users webpage
		try:
			# try to download the webpage
			webpageText=urllib2.urlopen(requestObject)
		except:
			popup('YoutubeTV', ('Failed to load webpage "'+str(url)+'"'))
			# download failed, return blank string
			return str()
		temp=''
		for line in webpageText:
			# mash everything into a string because they use code obscification
			# also strip endlines to avoid garbage
			temp+=(line.strip())
		return temp
	def cacheWebpage(self,url):
		# check limit of webcache
		webCacheLimit=int(addonObject.getSetting('webCacheLimit'))
		# when there are more items in the webcache than the
		# limit
		while self.webCache.length>webCacheLimit:
			# grab the key of the first item
			key=self.webCache.names[0]
			# delete the oldest item
			self.webCache.deleteValue(key)
			# delete the timer assocated with that key
			self.timer.deleteValue(key)
		# check the timer for this specific webpage
		if self.checkTimer(url,'webpageRefreshDelay') or\
		url not in self.webCache.names:
			# get the youtube users webpage
			webpageText=self.grabWebpage(url)
			# save this webpage in the cache
			self.webCache.saveValue(url,webpageText)
		# return the cached url
		return self.webCache.loadValue(url)
	def addVideo(self,channel,newVideo):
		'''channel is a string, item is a dict'''
		#if len(self.cache[channel])<1:
		tempCache=self.cache.loadValue(channel)
		if self.cache.length<1:
			# set found time for video
			newVideo['foundTime']=1
			# if the cache has no existing videos then add the video
			tempCache.append(newVideo)
			# then exit the function
			return
		# check for buttons that are not videos
		if "branded-page-gutter-padding" in newVideo['video']:
			# video is a button not a video dont add video
			return
		# create videoCounterHigh to store the highest counter value for the video
		videoCounterHigh=0
		for oldVideo in tempCache:
			# check for duplicates
			if newVideo['name'] == oldVideo['name'] :
				# duplicate found exit function
				return
			# add a time to the element for the purposes of sorting
			# this must be done after the element order has been reversed
			# in order for sorting to be properly managed the video
			# foundtime is a counter so it must find the highest foundtime
			# already in the array of videoObjects
			if oldVideo['foundTime']>videoCounterHigh:
				# the counter is equal to the highest counter on a video
				videoCounterHigh=oldVideo['foundTime']
		# set the new video to have a counter value of one more than the highest
		# foundTime counter existing on a video in the list
		newVideo['foundTime']=videoCounterHigh+1
		# create left and right variables to paste the variable
		# in the correct location
		left=[]
		right=[]
		# found variable tells the loop that the location has been found
		# so place all the rest of the variables on the right
		found=False
		# search for placement of video in existing cached videos
		for oldVideo in tempCache:
			# for each video in the channels cache
			if found:
				# if video placement has already been found
				# add remaining videos to the right
				right.append(oldVideo)
			else:
				# if video placement has not yet been found
				if oldVideo['foundTime'] < newVideo['foundTime']:
					# if newVideo is newer than oldVideo
					left.append(newVideo)
					right.append(oldVideo)
					# then set the value of found to true
					found=True
				else:
					#if newVideo is older than oldVideo
					left.append(oldVideo)
		# if now proper placement was found for the video then place
		# the video on at the end of the list of videos
		if found==False:
			right.append(newVideo)
		# add the two arrays together to get the new list
		# that has the video correctly placed inside
		tempCache=list(left+right)
		self.cache.saveValue(channel,tempCache)
	def getUserVideos(self,userName):
		# check the timer on the username
		if self.checkTimer(userName,'refreshDelay'):
			# check if the channel metadata needs updated
			self.grabChannelMetadata(userName)
			# create the progress bar
			progressDialog=xbmcgui.DialogProgress()
			# get the youtube users webpage
			temp=self.cacheWebpage("https://www.youtube.com"+str(userName)+"/videos")
			# create an array to hold the video watch strings
			videos=[]
			downloadMethod='youtubetv'
			#we have two different methods of grabing metadata
			if downloadMethod=='youtubetv':
				# search the videos without youtube-dl
				# search for the list of videos in the webpage
				temp=findText('<ul id="channels-browse-content-grid','<button class="yt-lockup-dismissable"></div>',temp)
				# start the progress dialog
				progressDialog.create(('Processing Video for '+userName),'Processing...')
				# there are 25 videos on each page so we dont need to process this
				# we multuply it by two and run progress for adding the videos to
				# the cache as well since this is half the work
				progressTotal=float(25*2)
				progressCurrent=0.0
				# split the list based on the video list items in the grid
				for line in temp.split('<li class="channels-content-item'):
					# check if the cancel button was pressed
					if progressDialog.iscanceled():
						# cancel execution and delete timer value to pervent
						# partially loaded list
						self.timer.deleteValue(userName)
						return
					# now find the youtube video information
					#findText(start,end,searchText)
					video=findText('href="/watch?v=','"',line)
					thumb=findText('src="','"',line)
					# remove the post info in the tail of the url
					# EXAMPLE: https://i.ytimg.com/vi/videoid/hqdefault.jpg?bunchOfYoutubeNonsense
					# removing the post info makes the url resolve correctly
					thumb=thumb.split('?')[0]
					title=findText('dir="ltr" title="','"',line)
					# convert all html entities in the title to unicode charcters
					title=self.cleanText(title)
					# begin building dict to add to the category array
					temp={}
					# set the video url to the found url
					temp['video']=video
					# set the title
					temp['name']=title
					# set the thumbnail, add http to make the address resolve
					if "http" not in thumb:
						# if https is not in the path add it
						temp['thumb']="http:"+thumb
					else:
						# otherwise add the path
						temp['thumb']=thumb
					# set the genre to youtube
					temp['genre']='youtube'
					# update the progress bar on screen and increment the counter
					progressDialog.update(int(100*(progressCurrent/progressTotal)),title)
					progressCurrent+=1
					# add the found data to the videos array
					videos.append(temp)
				# reverse the order of videos in order to give correct timestamps
				videos.reverse()
				# create dialog for adding videos
				progressDialog.create(('Adding video to '+userName),'Organizing...')
				progressTotal=len(videos)
				progressCurrent=0.0
				# add found video information to the cache
				for video in videos:
					# check if the cancel button was pressed
					if progressDialog.iscanceled():
						# cancel execution and delete timer value to pervent
						# partially loaded list
						self.timer.deleteValue(userName)
						return
					# this is the second half of the video updates so the dialog keeps running
					# update the progress bar on screen and increment the counter
					progressDialog.update(int(100*(progressCurrent/progressTotal)),video['name'])
					progressCurrent+=1
					# set user data in the cache
					self.addVideo(userName,video)
			elif downloadMethod=='youtube-dl':
				# split page based on parathensis since we are looking for video play strings
				webpageText=temp.split('"')
				# run though the split text array looking for watch strings in lines
				for line in webpageText:
					if '/watch?v=' in line:
						# create real youtube url from found strings
						temp='https://youtube.com'+str(line)
						# avoid duplicate entries
						if temp not in videos:
							# add video if it does not exist in the file already
							videos.append(temp)
				# start the progress dialog
				progressDialog.create(('Adding Videos to '+userName),'Processing...')
				progressTotal=float(len(videos))
				progressCurrent=0.0
				# reverse the order of videos in order to give correct timestamps
				videos.reverse()
				# generate the data for drawing videos in kodi menu
				for video in videos:
					# check if the cancel button was pressed
					if progressDialog.iscanceled():
						# cancel execution and delete timer value to pervent
						# partially loaded list
						self.timer.deleteValue(userName)
						return
					# update the progress bar on screen and increment the counter
					progressDialog.update(int(100*(progressCurrent/progressTotal)),video)
					progressCurrent+=1
					# build a list of existing video urls in cache to check aginst
					videoList=[]
					#for videoDict in self.cache[userName]:
					for videoDict in self.cache.loadValue(userName):
						# add the url of each video in the cache already
						# to the videoList array for checking
						videoList.append(videoDict['video'])
					# check if the video already exists in the video cache by
					# referencing it against the previously create videoList
					if video not in videoList:
						# begin building dict to add to the category array
						temp={}
						# set the video url to the found url
						temp['video']=video
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
						# add a time to the element for the purposes of sorting
						temp['foundTime']=datetime.datetime.now()
						# set user data in the cache
						self.addVideo(userName,temp)
			# load up the video limit from settings
			videoLimit=addonObject.getSetting('videoLimit')
			# cast videolimit from a string to a int
			videoLimit=int(videoLimit)
			# ignore videoLimit if it is set to 0
			if videoLimit!=0:
				# load up the videos
				tempVideoCache=self.cache.loadValue(userName)
				# trim videos to the video limit
				while len(tempVideoCache)>videoLimit:
					# pop off a single item from the end of
					# the array
					tempVideoCache.pop()
			# update the settings in the saved cache after the loops
			self.cache.saveValue(userName,tempVideoCache)
	def backup(self):
		# backup the channels saved in the addon
		tempTable=tables.table(_datadir+'backup/')
		tempTable.saveValue('backup',self.cache.names)
		popup('YoutubeTV','Backup Complete!')
	def restore(self):
		# clear out caches prior to restore
		# this prevents hanging cache data
		self.playlistCache.reset()
		self.cache.reset()
		self.timer.reset()
		# restore the channels saved from the last backup
		tempTable=tables.table(_datadir+'backup/')
		channels=tempTable.loadValue('backup')
		# refresh all channel data for channels
		for channel in channels:
			# grab each channels metadata and store it
			self.grabChannelMetadata(channel)
			# save all channels into the cache
			self.cache.saveValue(channel,list())
		# refresh the view and load the popup
		xbmc.executebuiltin('container.Update('+_url+',replace)')
		popup('YoutubeTV','Restore of backup Complete!')
################################################################################
def createButton(action='',title='default',thumb='default',icon='default',fanart='default',is_folder=True):
	'''Create a list item to be created that is used as a menu button'''
	url=(_url+'?action='+action)
	list_item = xbmcgui.ListItem(label=title)
	list_item.setInfo('video', {'title':title , 'genre':'menu' })
	list_item.setArt({'thumb': thumb, 'icon': icon, 'fanart': fanart})
	list_item.setProperty('IsPlayable', 'true')
	listingItem=(url, list_item, is_folder)
	return listingItem
################################################################################
# Get the plugin url in plugin:// notation.
_id= 'plugin.video.youtubetv'
_url = sys.argv[0]
# base directory
_basedir= "special://home/addons/"+_id+"/"
# translate path to system path, make plugin multiplatform
_basedir=xbmc.translatePath(_basedir)
# resources directory
_resdir = "special://home/addons/"+_id+"/resources"
_resdir=xbmc.translatePath(_resdir)
# user settings directory
_datadir=('special://userdata/addon_data/'+_id+'/')
_datadir=xbmc.translatePath(_datadir)
# add the resources directory to the sys path to import libaries
sys.path.append(_resdir+'/lib/')
# import localy stored libaries
import tables
import masterdebug
# initalize the debugging
debug=masterdebug.init(False)
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])
# load the youtube videos on that channel from
addonObject=xbmcaddon.Addon(id=str(_id))
session=YoutubeTV()
# Free sample videos are provided by www.vidsplay.com
# Here we use a fixed set of properties simply for demonstrating purposes
# In a "real life" plugin you will need to get info and links to video files/streams
# from some web-site or online service.
####################################################################
# Read videos from text file where each line contains a username to
# load the cache into videos, needs reloaded upon changes
VIDEOS = session.cache
def get_categories():
	"""
	Get the list of video categories.
	Here you can insert some parsing code that retrieves
	the list of video categories (e.g. 'Movies', 'TV-shows', 'Documentaries' etc.)
	from some site or server.

	:return: list
	"""
	# update the videos in the cache for each category
	return session.cache.names

def get_videos(category):
	"""
	Get the list of videofiles/streams.
	Here you can insert some parsing code that retrieves
	the list of videostreams in a given category from some site or server.

	:param category: str
	:return: list
	"""
	# check for updates to the category
	session.getUserVideos(category)
	# return category value
	return session.cache.loadValue(category)

def list_categories():
	"""
	Create the list of video categories in the Kodi interface.
	"""
	# Get video categories
	categories = get_categories()
	# Create a list for our items.
	listing = []
	# create a search channel button in the channels view
	searchIconPath=(_resdir+'/media/search.png')
	# create the search button
	searchButton=createButton(action='searchChannel',title='Search Channels',thumb=searchIconPath,icon=searchIconPath,fanart='default')
	# create refresh context menu item for the search button
	contextItems=[(('Refresh View'),'RunPlugin('+_url+'?action=main)')]
	# add context menu items to the search button
	searchButton[1].addContextMenuItems(contextItems)
	# add the search button to the listing
	listing.append(searchButton)
	# Iterate through categories
	for category in categories:
		# load up the channel cache data
		tempChannelCache=session.channelCache.loadValue(category)
		# if a category has nothing in it then no category will be listed in the interface
		if len(category)==0:
			return
		# store video title for use in this scope
		title=tempChannelCache['title']
		# Create a list item with a text label and a thumbnail image.
		list_item = xbmcgui.ListItem(label=title)
		# add context menu actions
		contextItems=[]
		# remove category button
		contextItems.append((('Remove '+title),'RunPlugin('+_url+'?action=removeChannel&value='+category+')'))
		# reset channel button
		contextItems.append(('Reset Channel','RunPlugin('+_url+'?action=resetChannel&value='+category+')'))
		list_item.addContextMenuItems(contextItems)
		# Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
		# Here we use the same image for all items for simplicity's sake.
		# In a real-life plugin you need to set each image accordingly.
		list_item.setArt({'thumb': tempChannelCache['icon'],\
				  'icon': tempChannelCache['icon'],\
				  'fanart': tempChannelCache['fanArt']})
				  #'fanart': session.cache.loadValue(category)[0]['thumb']})
		# Set additional info for the list item.
		# Here we use a category name for both properties for for simplicity's sake.
		# setInfo allows to set various information for an item.
		# For available properties see the following link:
		# http://mirrors.xbmc.org/docs/python-docs/15.x-isengard/xbmcgui.html#ListItem-setInfo
		list_item.setInfo('video', {'title': tempChannelCache['title'], 'genre': category})
		# Create a URL for the plugin recursive callback.
		# Example: plugin://plugin.video.example/?action=listing&category=Animals
		url = '{0}?action=listing&category={1}'.format(_url, category)
		# is_folder = True means that this item opens a sub-list of lower level items.
		is_folder = True
		# Add our item to the listing as a 3-element tuple.
		listing.append((url, list_item, is_folder))
	# Add our listing to Kodi.
	# Large lists and/or slower systems benefit from adding all items at once via addDirectoryItems
	# instead of adding one by ove via addDirectoryItem.
	xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
	# Add a sort method for the virtual folder items (alphabetically, ignore articles)
	#xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
	# change the default view to thumbnails
	xbmc.executebuiltin('Container.SetViewMode(%d)' % 500)
	# Finish creating a virtual folder.
	xbmcplugin.endOfDirectory(_handle)

def list_videos(category):
	"""
	Create the list of playable videos in the Kodi interface.

	:param category: str
	"""
	# Get the list of videos in the category.
	videos = get_videos(category)
	# Create a list for our items.
	listing = []
	# create playlists button to link to youtube playlist functionality
	listing.append(createButton(action=('channelPlaylists&channel='+category),\
		title='Playlists',thumb=(_resdir+'/media/playlist.png'),icon='',fanart=''))
	# Iterate through videos.
	for video in videos:
		# Create a list item with a text label and a thumbnail image.
		list_item = xbmcgui.ListItem(label=video['name'])
		# Set additional info for the list item.
		list_item.setInfo('video', {'title': video['name'], 'genre': video['genre']})
		# Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
		# Here we use the same image for all items for simplicity's sake.
		# In a real-life plugin you need to set each image accordingly.
		list_item.setArt({'thumb': video['thumb'], 'icon': video['thumb'], 'fanart': video['thumb']})
		# Set 'IsPlayable' property to 'true'.
		# This is mandatory for playable items!
		list_item.setProperty('IsPlayable', 'true')
		# Create a URL for the plugin recursive callback.
		# Example: plugin://plugin.video.example/?action=play&video=http://www.vidsplay.com/vids/crab.mp4
		url = '{0}?action=play&video={1}'.format(_url, video['video'])
		# Add the list item to a virtual Kodi folder.
		# is_folder = False means that this item won't open any sub-list.
		is_folder = False
		# Add our item to the listing as a 3-element tuple.
		listing.append((url, list_item, is_folder))
	# Add our listing to Kodi.
	# Large lists and/or slower systems benefit from adding all items at once via addDirectoryItems
	# instead of adding one by ove via addDirectoryItem.
	xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
	# Add a sort method for the virtual folder items (alphabetically, ignore articles)
	#xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
	# change the default view to thumbnails
	xbmc.executebuiltin('Container.SetViewMode(%d)' % 500)
	# Finish creating a virtual folder.
	xbmcplugin.endOfDirectory(_handle)
def play_video(path):
	"""
	Play a video by the provided path.

	:param path: str
	"""
	# if the previous two if statements dont hit then the path is a
	# video path so modify the string and play it with the youtube plugin
	###############
	# the path to let videos be played by the youtube plugin
	youtubePath='plugin://plugin.video.youtube/?action=play_video&videoid='
	# remove the full webaddress to make youtube plugin work correctly
	path=path.replace('https://youtube.com/watch?v=','')
	# also check for partial webaddresses we only need the video id
	path=path.replace('watch?v=','')
	# add youtube path to path to make videos play with the kodi youtube plugin
	path=youtubePath+path
	# Create a playable item with a path to play.
	play_item = xbmcgui.ListItem(path=path)
	# Pass the item to the Kodi player.
	xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)
def play_all(arrayOfObjects):
	# create the playlist
	playlist= xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
	index=1
	# for each item in the playlist
	for item in arrayOfObjects:
		path=item['video']
		# the path to let videos be played by the youtube plugin
		youtubePath='plugin://plugin.video.youtube/?action=play_video&videoid='
		# remove the full webaddress to make youtube plugin work correctly
		path=path.replace('https://youtube.com/watch?v=','')
		# also check for partial webaddresses we only need the video id
		path=path.replace('watch?v=','')
		# add youtube path to path to make videos play with the kodi youtube plugin
		path=youtubePath+path
		# create listitem to insert in the playlist
		list_item = xbmcgui.ListItem(label=item['name'])
		#list_item.setInfo('video', {'title':title , 'genre':'menu' })
		list_item.setInfo('video', item)
		list_item.setArt(item)
		list_item.setProperty('IsPlayable', 'true')
		# add item to the playlist
		playlist.add(path,list_item,index)
		# increment the playlist index
		index+=1

def router(paramstring):
	"""
	Router function that calls other functions
	depending on the provided paramstring

	:param paramstring:
	"""
	# Parse a URL-encoded paramstring to the dictionary of
	# {<parameter>: <value>} elements
	params = dict(parse_qsl(paramstring))
	# Check the parameters passed to the plugin
	if params:
		if params['action'] == 'listing':
			debug.add('action=listing was activated in router')
			if params['category'] in session.cache.names:
				# Display the list of videos in a provided category.
				list_videos(params['category'])
			else:
				# refresh the category view as a nonexisting channel
				# was clicked
				list_categories()
		elif params['action'] == 'play':
			debug.add('action=play was activated in router')
			# Play a video from a provided URL.
			play_video(params['video'])
		elif params['action'] == 'main':
			debug.add('action=main was activated in router')
			# the item is a forced return to main menu
			list_categories()
			# force refresh the view
			xbmc.executebuiltin('container.Update('+_url+',replace)')
		elif params['action'] == 'channelPlaylists':
			debug.add('action=channelPlaylists was activated in router')
			session.channelPlaylists(params['channel'])
		elif params['action'] == 'viewPlaylist':
			debug.add('action=viewPlaylist was activated in router')
			session.grabPlaylist(params['playlist'],params['channel'])
		elif params['action'] == 'playAll':
			# play all of the videos in a playlist
			play_all(session.playlistCache.loadValue(params['channel'])[params['playlist']]['array'])
		elif params['action'] == 'removeChannel':
			debug.add('action=removeChannel was activated in router')
			# remove the channel from cache and channel list
			session.removeChannel(params['value'])
			# refresh the view
			list_categories()
		elif params['action'] == 'resetChannel':
			debug.add('action=resetChannel was activated in router')
			# grab new channel information
			session.resetChannel(params['value'])
			# refresh the view
			list_categories()
		elif params['action'] == 'addChannel':
			# check for blank strings and ignore them
			if len(params['value']) > 0:
				session.addChannel(params['value'])
			# popup notification
			popup('YoutubeTV','Added Channel '+params['value'])
		elif params['action'] == 'backupChannels':
			# backup channels
			session.backup()
		elif params['action'] == 'restoreChannels':
			# restore channels
			session.restore()
			# refresh the view
			list_categories()
		elif params['action'] == 'searchChannel':
			debug.add('addChannel invoked, creating dialog')
			# the item is a button to display a input dialog
			# that will add a new channel to the addon
			dialogObject=xbmcgui.Dialog()
			returnString=dialogObject.input('Type a youtube username')
			debug.add('input return string',returnString)
			# check for blank strings and ignore them
			if len(returnString) > 0:
				session.searchChannel(returnString)
			else:
				# refresh the view
				list_categories()
	else:
		debug.add('listing categories...')
		# If the plugin is called from Kodi UI without any parameters,
		# display the list of video categories
		list_categories()

if __name__ == '__main__':
	# Call the router function and pass the plugin call parameters to it.
	# We use string slicing to trim the leading '?' from the plugin call paramstring
	debug.add('sys.argv[2][1:]',sys.argv[2][1:])
	router(sys.argv[2][1:])
