#!/usr/bin/python

import os
import re

for dirpath, dirnames, filenames in os.walk('skeinforge'):
	for filename in filenames:
		if os.path.splitext(filename)[-1] == '.py':
			pathname = os.path.join(dirpath, filename)
			lines = open(pathname, "r").readlines()
			modified = False
			for i in range(len(lines)):
				if lines[i].startswith('from __future__ import absolute_import'):
					lines[i] = '#' + lines[i]
					modified = True
				if lines[i].find('psyco') >= 0 and not lines[i].startswith('#'):
					lineLength = len(lines[i])
					start = 0
					end = lineLength - 1
					while start < lineLength and lines[i][start].isspace():
						start = start + 1
					while end >= 0 and lines[i][end].isspace():
						end = end - 1
					if end > start:
						if lines[i][start] != '"' and lines[i][end+1] != '"':
							lines[i] = lines[i][:start] + '"' + lines[i][start:end+1] + '"' + lines[i][end+1:]
							modified = True
			if modified:
				open(pathname, "w").writelines(lines)
