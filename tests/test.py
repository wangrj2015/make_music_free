# -*- coding: utf-8 -*-

import re
import math
from urllib import unquote

def decode_url():
	str = '8h2fmF%1%3755ph187b5%5EtFii153537E33_ab1%b5E-t%l.3E5E5543%k63951E%np2ec59%%22_43e43aEd25u%F.o%925%55_Fya26c-4El3mxm29FE269la%2d%616-lA5i%F722F51.u3c75244%%.a227131%6mtD56E26%5'

	loc1 = int(str[0])
	loc2 = str[1:]
	loc3 = int(math.floor(len(loc2) / loc1))
	loc4 = int(len(loc2) % loc1)
	#print loc1,loc2,loc3,loc4
	loc5 = []
	loc6 = 0

	while loc6 < loc4:
		#if not loc5[loc6]:
			#loc5[loc6] = ''
		loc5.insert(loc6,loc2[(loc3+1) * loc6 : (loc3+1) * (loc6+1)])
		loc6 += 1

	loc6 = loc4
	while loc6 < loc1:
		temp = loc3*(loc6-loc4) + (loc3+1) * loc4
		#print temp,loc3,loc6,loc5
		loc5.insert(loc6, loc2[temp : temp + loc3] + '  ')
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

	print loc7
	loc7 = unquote(loc7)
	loc8 = ''
	loc6 = 0
	while loc6 < len(loc7):
		if loc7[loc6] != '^':
			loc8 = loc8 + loc7[loc6]
		else:
			loc8 = loc8 + '0'
		loc6 += 1

	return loc8.replace('+',' ')


if __name__ == '__main__':
	#match = re.search(r'song/(.*?)\?',u'http://www.xiami.com/song/1774926422?spm=a1z1s.6659513.0.0.Pd9hGE')
	#print match.group(1)

	print decode_url()
	#print 'ascde'[-1:7]


