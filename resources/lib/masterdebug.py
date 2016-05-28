#########################################################################
# Class to assist in debugging software
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
class init():
	'''
	A master debuging object to handle all debugging output
	
	If given a value of False debugging will be disabled.
	e.g. "debug=masterDebug(False)"
	'''
	def __init__(self,debug=True):
		self.debug=debug
		self.text=[]
		if self.debug==True:
			self.banner(' PYTHON DEBUG ')
	def add(self,title=None,content=None):
		# check if debug is disabled
		if self.debug==False:
			return
		# - All arguments given here are casted to strings
		# if user gives two arguements the first is considered the title
		if content!= None:
			# append the content with a title
			self.text.append(str(title)+' : '+str(content))
			print(str(title)+' : '+str(content))
		else:
			# otherwise add the first argument as a debug line
			self.text.append(str(title))
			print(str(title))

	def get(self):
		# return the text array
		return self.text
	def banner(self,titleString=None):
		# check if debug is disabled
		if self.debug==False:
			return
		if titleString != None:
			title=str(titleString)
			edge='#'*((80-len(title))/2)
			print('#'*80)
			print(edge+title+edge)
			print('#'*80)
		else:
			print('#'*80)
	def display(self):
		# check if debug is disabled
		if self.debug==False:
			return
		# draw banner divider
		self.banner(' PYTHON DEBUG ')
		# write each line of the debug
		for line in self.text:
			# add debug to each line to use grep for error searching
			print('DEBUG:'+str(line))
		# draw bottom divider
		self.banner()

