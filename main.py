# -*- coding: utf-8 -*-
# Module: default
# Author: Roman V. M.
# Created on: 28.11.2014
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import sys
from urlparse import parse_qsl
import xbmcgui
import xbmcplugin
import xbmcaddon
###################
import urllib
import os
import subprocess
import datetime
import pickle
# session class for youtubeTV session starting
class YoutubeTV():
	def __init__(self):
		'''This object loads up the youtubeTV session for cache functionality and automated work.'''
		# create the cache for this session
		self.cache=self.loadConfig('cache','dict')
		# cache timer
		self.timer=self.loadConfig('timer','dict')
		# load the channels config
		self.channels=self.loadConfig('channels','array')
	def grabCache(self):
		# return the cache in its current state
		return self.cache
	def saveFile(self,fileName,content):
		# open the file to write
		fileObject=open(('~/.kodi/userdata/addon_data/plugin.video.youtubetv/'+fileName),'w')
		# write file content
		fileObject.write(content)
		# close the file
		fileObject.close()
	def loadFile(self,fileName):
		path=('~/.kodi/userdata/addon_data/plugin.video.youtubetv/'+fileName)
		if os.path.exists(path):
			# open the file to write
			fileObject=open(path,'r')
			# return the string text of the file
			return fileObject.read()
		else:
			# return false if the file is not found
			return False
	def saveConfig(self,config,newValue):
		'''Convert objects into strings and save in xbmc settings
		for the addon.'''
		# convert the new value into a string for storage
		temp=pickle.dumps(newValue)
		# write new config back to the addon settings
		self.saveFile(config,temp)
		#addonObject.setSettings(config,temp)
	def loadConfig(self,config,blankType):
		'''Used for loading objects from xbmc settings that were
		stored using pythons pickle functionality.'''
		# open the pickled settings using xbmcs settings api
		#configObject=addonObject.getSettings(config)
		configObject=loadFile(config)
		if configObject == True:
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
		# check if username is already in channels
		if channelUserName not in self.channels:
			# add username to channels
			self.channels.append(channelUserName)
		else:
			# end execution since it would be a dupe
			return
		# save the config changes
		self.saveConfig('channels',self.channels)
	def checkTimer(self,userName):
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
	def getUserVideos(self,userName):
		# check the timer on the username
		if checkTimer(userName):
			# reset the timer and refresh the program list
			self.timer[userName]=datetime.datetime.now()+datetime.timedelta(hours=1)
			# save changes to timer to config file
			self.saveConfig('timer',self.timer)
		else:
			# end the program and use the cached version of the video list
			return self.cache[userName]
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
			if video not in self.cache[userName].keys():
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
				# update the settings in the saved cache
				self.saveConfig('cache',self.cache)

		# return the cached videos
		return self.cache[userName]

# create addon object
addonObject=xbmcaddon.Addon()

# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])

# Free sample videos are provided by www.vidsplay.com
# Here we use a fixed set of properties simply for demonstrating purposes
# In a "real life" plugin you will need to get info and links to video files/streams
# from some web-site or online service.
####################################################################
# Read videos from text file where each line contains a username to 
# load the youtube videos on that channel from
session=YoutubeTV()
# load the cache into videos, needs reloaded upon changes
VIDEOS = session.cache
#~ VIDEOS = {'Animals': [{'name': 'Crab',
                       #~ 'thumb': 'http://www.vidsplay.com/vids/crab.jpg',
                       #~ 'video': 'http://www.vidsplay.com/vids/crab.mp4',
                       #~ 'genre': 'Animals'},
                      #~ {'name': 'Alligator',
                       #~ 'thumb': 'http://www.vidsplay.com/vids/alligator.jpg',
                       #~ 'video': 'http://www.vidsplay.com/vids/alligator.mp4',
                       #~ 'genre': 'Animals'},
                      #~ {'name': 'Turtle',
                       #~ 'thumb': 'http://www.vidsplay.com/vids/turtle.jpg',
                       #~ 'video': 'http://www.vidsplay.com/vids/turtle.mp4',
                       #~ 'genre': 'Animals'}
                      #~ ],
            #~ 'Cars': [{'name': 'Postal Truck',
                      #~ 'thumb': 'http://www.vidsplay.com/vids/us_postal.jpg',
                      #~ 'video': 'http://www.vidsplay.com/vids/us_postal.mp4',
                      #~ 'genre': 'Cars'},
                     #~ {'name': 'Traffic',
                      #~ 'thumb': 'http://www.vidsplay.com/vids/traffic1.jpg',
                      #~ 'video': 'http://www.vidsplay.com/vids/traffic1.avi',
                      #~ 'genre': 'Cars'},
                     #~ {'name': 'Traffic Arrows',
                      #~ 'thumb': 'http://www.vidsplay.com/vids/traffic_arrows.jpg',
                      #~ 'video': 'http://www.vidsplay.com/vids/traffic_arrows.mp4',
                      #~ 'genre': 'Cars'}
                     #~ ],
            #~ 'Food': [{'name': 'Chicken',
                      #~ 'thumb': 'http://www.vidsplay.com/vids/chicken.jpg',
                      #~ 'video': 'http://www.vidsplay.com/vids/bbqchicken.mp4',
                      #~ 'genre': 'Food'},
                     #~ {'name': 'Hamburger',
                      #~ 'thumb': 'http://www.vidsplay.com/vids/hamburger.jpg',
                      #~ 'video': 'http://www.vidsplay.com/vids/hamburger.mp4',
                      #~ 'genre': 'Food'},
                     #~ {'name': 'Pizza',
                      #~ 'thumb': 'http://www.vidsplay.com/vids/pizza.jpg',
                      #~ 'video': 'http://www.vidsplay.com/vids/pizza.mp4',
                      #~ 'genre': 'Food'}
                     #~ ]}


def get_categories():
    """
    Get the list of video categories.
    Here you can insert some parsing code that retrieves
    the list of video categories (e.g. 'Movies', 'TV-shows', 'Documentaries' etc.)
    from some site or server.

    :return: list
    """
    return VIDEOS.keys()


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
    # update videos
    return session.cache[category]


def list_categories():
    """
    Create the list of video categories in the Kodi interface.
    """
    # set the listing to the session channels
    listing = session.channels
    # Iterate through categories
    for category in categories:
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=category)
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
        list_item.setArt({'thumb': VIDEOS[category][0]['thumb'],
                          'icon': VIDEOS[category][0]['thumb'],
                          'fanart': VIDEOS[category][0]['thumb']})
        # Set additional info for the list item.
        # Here we use a category name for both properties for for simplicity's sake.
        # setInfo allows to set various information for an item.
        # For available properties see the following link:
        # http://mirrors.xbmc.org/docs/python-docs/15.x-isengard/xbmcgui.html#ListItem-setInfo
        list_item.setInfo('video', {'title': category, 'genre': category})
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
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
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
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def play_video(path):
    """
    Play a video by the provided path.

    :param path: str
    """
    # Create a playable item with a path to play.
    play_item = xbmcgui.ListItem(path=path)
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)


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
            # Display the list of videos in a provided category.
            list_videos(params['category'])
        elif params['action'] == 'play':
            # Play a video from a provided URL.
            play_video(params['video'])
    else:
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of video categories
        list_categories()


if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])
