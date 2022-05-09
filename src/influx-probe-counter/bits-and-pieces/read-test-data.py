#!/usr/bin/env python3
#
#
#get file object
f = open("test-data.txt", "r")

while(True):
	#read next line
	line = f.readline()
	#if line is empty, you are done with all lines in the file
	if not line:
		break
	#you can access the line
	print(line.strip())

#close file
f.close
