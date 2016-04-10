# -*- coding: utf-8 -*-
import re
import math
from urllib import unquote

def decode_location(str):
	loc1 = int(str[0])
	loc2 = str[1:]
	loc3 = int(math.floor(len(loc2) / loc1))
	loc4 = int(len(loc2) % loc1)
	loc5 = []
	loc6 = 0

	while loc6 < loc4:
		loc5.insert(loc6,loc2[(loc3+1) * loc6 : (loc3+1) * (loc6+1)])
		loc6 += 1

	loc6 = loc4
	while loc6 < loc1:
		temp = loc3*(loc6-loc4) + (loc3+1) * loc4
		loc5.insert(loc6, loc2[temp : temp + loc3] + ' ')
		loc6 += 1

	loc7 = ''
	loc6 = 0
	loc9 = 0
	while loc6 < len(loc5[0]):
		loc9 = 0
		while loc9 < len(loc5):
			loc7 = loc7 + loc5[loc9][loc6]
			loc9 += 1
		loc6 += 1

	loc7 = unquote(loc7)
	loc8 = ''
	loc6 = 0
	while loc6 < len(loc7):
		if loc7[loc6] != '^':
			loc8 = loc8 + loc7[loc6]
		else:
			loc8 = loc8 + '0'
		loc6 += 1

	return loc8.replace('+',' ').rstrip()