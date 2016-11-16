#########################################################################
# Generic database libary using pickle to store values in files.
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
import masterdebug
debug=masterdebug.init(False)
from files import loadFile
from files import writeFile
################################################################################
# import all the things
from pickle import loads as unpickle
from pickle import dumps as pickle
from os.path import join as pathJoin
from os.path import exists as pathExists
from os import listdir
from os import makedirs
from os import remove as removeFile
from random import choice
################################################################################
class table():
	def __init__(self,path):
		'''
		DB table to store things as files and directories. This is
		designed to reduce ram usage when reading things from large
		databases. Specifically this is designed for caches.

		# variables #
		.path
		  The path on the filesystem where the table is stored.
		.names
		  Gives you a list containing the names of all stored
		  values as strings.
		.namePaths
		  Gives you a dict where the keys are the names and
		  the value is the path of that value database file
		.length
		  The length of names stored in this table
		'''
		# path of the root of the cache, this is where files
		# will be stored on the system
		self.path=path
		# create the paths if they do not exist
		if not pathExists(self.path):
			makedirs(self.path)
		debug.add('table path',self.path)
		# the path prefix is for tables stored in tables
		self.pathPrefix=''
		# tables are stored as files
		tempTable=[]
		# array of all the value names stored on table
		namesPath=pathJoin(self.path,'names.table')
		# if no namepaths exist create them
		if not pathExists(pathJoin(namesPath)):
			# write the new value to the system
			writeFile(namesPath,pickle(dict()))
		# load the name paths
		self.namePaths=unpickle(loadFile(namesPath))
		debug.add('self.namePaths',self.namePaths)
		# create a array of all the names of values stored
		self.names=self.namePaths.keys()
		debug.add('self.names',self.names)
		# length of all the values stored on the table
		self.length=len(self.names)
		debug.add('self.length',self.length)
		# the protected list is a array of names that are
		# protected from limit cleaning
		protectedPath=pathJoin(self.path,'protected.table')
		if pathExists(pathJoin(protectedPath)):
			# load the list
			self.protectedList=unpickle(loadFile(protectedPath))
		else:
			# create a blank list
			self.protectedList=[]
		# limit value to limit the number of values
		# load the limit value from file if it exists
		limitPath=pathJoin(self.path,'limit.table')
		if pathExists(pathJoin(limitPath)):
			self.limit=unpickle(loadFile(limitPath))
		else:
			self.limit=None
	################################################################################
	def reset(self):
		'''
		Delete all stored values stored in the table.
		'''
		for value in self.names:
			self.deleteValue(value)
	################################################################################
	def setProtected(self,name):
		'''
		Set a name in the table to be protected from removal
		because of limits.
		'''
		# generate the filepath to the protected values
		# list
		filePath=pathJoin(self.path,'protected.table')
		# check if the path exists
		if pathExists(filePath):
			# read the protected list from the file
			protectedList=unpickle(loadFile(filePath))
		else:
			# create the list and append the name
			protectedList=[]
		# append the new value to the list
		protectedList.append(name)
		# pickle the protected list for storage
		protectedList=pickle(protectedList)
		# write the changes back to the protected list
		writeFile(filePath,protectedList)
	################################################################################
	def setLimit(self,limit):
		'''
		Set the limit of values that are stored in this table.
		This ignores protected values.
		'''
		# write the limit value to the limit file in the table
		filePath=pathJoin(self.path,'limit.table')
		# set the limit in this instance
		self.limit=limit
		# write the new limit back to the storage
		success=writeFile(filePath,limit)
		return success
	################################################################################
	def checkLimits(self):
		if self.limit is not None and\
		self.length-len(self.protectedList) > limit:
			deathList=[]
			for name in self.names:
				if name not in self.protectedList:
					deathList.append(name)
			# randomly pick a value to delete
			# TODO: create table metadata to dertermine the
			#       time that values were added to the table
			#       and remove the oldest value when limits
			#       have been exceeded
			deathMark=choice(deathList)
			# delete the value
			if self.deleteValue(deathMark) is False:
				return False
		# successfully removed item or no items needed
		# to be removed
		return True
	################################################################################
	def loadValue(self,name):
		'''
		Loads a saved value and returns it.
		'''
		# find the file path in the names array
		if name in self.names:
			filePath=self.namePaths[name]
		else:
			return False
		# check if the path exists
		if pathExists(filePath):
			# load the data
			fileData=loadFile(filePath)
		else:
			# return false if the value does not exist
			return False
		# unpickle the filedata
		fileData = unpickle(fileData)
		debug.add('loading value '+str(name),fileData)
		# returns the value of a table stored on disk
		return fileData
	################################################################################
	def saveValue(self,name,value):
		'''
		Save a value with the name name and the value value.
		'''
		debug.add('saving value '+str(name),value)
		# create a file assocation for the name to store the value
		if name not in self.names:
			debug.add('name not in self.names')
			# create a counter for the generated filename
			counter=0
			# seed value for while loop
			newName = (str(counter)+'.value')
			# find a filename that does not already exist in
			# the database directory
			while newName in listdir(self.path):
				# increment the counter
				counter+=1
				# iterate the value
				newName=(str(counter)+'.value')
			debug.add('newname',newName)
			# set the metadata value for the filepaths in this table instance
			self.namePaths[name]=pathJoin(self.path,newName)
			# write the newly created name assocation to table metadata on disk
			writeFile(pathJoin(self.path,'names.table'),pickle(self.namePaths))
		debug.add('namePaths',self.namePaths)
		# update the length and names attributes
		self.names=self.namePaths.keys()
		self.length=len(self.names)
		# saves a table changes back onto the disk
		fileData=writeFile(self.namePaths[name],pickle(value))
		return fileData
	################################################################################
	def deleteValue(self,name):
		'''
		Delete a value with name name.
		'''
		# clean up names to avoid stupid
		debug.add('deleting value ',name)
		# figure out the path to the named value file
		if name in self.names:
			filePath=self.namePaths[name]
			# remove the metadata entry
			del self.namePaths[name]
			# write changes to database metadata file
			writeFile(pathJoin(self.path,'names.table'),pickle(self.namePaths))
			# update the length and names attributes
			self.names=self.namePaths.keys()
			self.length=len(self.names)
		else:
			return False
		if pathExists(filePath):
			# remove the file accocated with the value
			removeFile(filePath)
			return True
		else:
			return False
################################################################################
