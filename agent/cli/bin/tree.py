#!/bin/env python

from os import listdir, sep
from os.path import abspath, basename, isdir
from os.path import realpath, islink
from sys import argv

def tree(d, padding):
	print padding[:-1] + '+-' + basename(abspath(d)) + '/'
	padding = padding + ' '
	files = []
	files = listdir(d)
	count = 0
	for f in files:
		count += 1
		print padding + '|'
		path = d + sep + f
		if isdir(path):
			if count == len(files):
				tree(path, padding + ' ')
			else:
				tree(path, padding + '|')
		elif islink(path):
			print padding + '+-' + f + '  ->  ' + basename(realpath(path))
		else:
			print padding + '+-' + f

if __name__ == '__main__':
	dirs = argv[1:]
	for d in dirs:
		tree(d, ' ')

