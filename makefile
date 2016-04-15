build: *.py *.md *.xml *.png resources/
	# output the addon into a zipfile so it can be installed
	zip -r -9 output.zip *.py *.md *.xml *.png resources/ 
