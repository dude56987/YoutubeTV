########################################################################
# Utils for working with files
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
import os
########################################################################
def loadFile(fileName):
	'''
	Read the file located at fileName. Return the contents of that 
	file as a string if the file can be read. If the file can not
	be read then return False.

	:return string/bool
	'''
	try:
		#print "Loading :",fileName
		fileObject=open(fileName,'r');
	except:
		print("Failed to load : "+fileName)
		return False
	fileText=''
	lineCount = 0
	for line in fileObject:
		fileText += line
		#sys.stdout.write('Loading line '+str(lineCount)+'...\r')
		lineCount += 1
	#print "Finished Loading :",fileName
	fileObject.close()
	if fileText == None:
		return False
	else:
		return fileText
	#if somehow everything fails return fail
	return False
########################################################################
def writeFile(fileName,contentToWrite):
	'''
	Write the fileName path as a file containing the contentToWrite
	string value.

	:return bool
	'''
	# figure out the file path
	filepath = fileName.split(os.sep)
	filepath.pop()
	filepath = os.sep.join(filepath)
	# check if path exists
	if os.path.exists(filepath):
		try:
			fileObject = open(fileName,'w')
			fileObject.write(contentToWrite)
			fileObject.close()
			return True
		except:
			print('Failed to write file:'+fileName)
			return False
	else:
		print('Failed to write file, path:'+filepath+'does not exist!')
		return False
