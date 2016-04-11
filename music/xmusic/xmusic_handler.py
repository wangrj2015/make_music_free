# -*- coding: utf-8 -*-

import tornado.web
import tornado.escape
import requests
import re
from logger import LoggerFactory
import util
import traceback
from pyquery import PyQuery
import lxml

logger = LoggerFactory.getLogger()

class XMusicHandler(tornado.web.RequestHandler):

	def set_default_headers(self):
		self.set_header('Access-Control-Allow-Origin', '*')
		self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
		self.set_header('Access-Control-Allow-Headers', '*')

	def get(self):
		try:
			song_url = self.get_argument('song_url')
			if len(song_url)==0 :
				self.write("false")
				return
			logger.info('IP:'+self.request.remote_ip+' song_url:' + song_url)
			#单首歌
			if song_url.find('song') != -1:
				result = self._handle(song_url,r'song/(\d+).*',u'http://www.xiami.com/song/playlist/id/{0}/object_name/default/object_id/0/cat/json')
				self.write(result)
			#专辑
			elif song_url.find('album') != -1:
				result = self._handle(song_url,r'album/(\d+).*',u'http://www.xiami.com/song/playlist/id/{0}/type/1/cat/json')
				self.write(result)
			#精选集
			elif song_url.find('collect') != -1:
				result = self._handle(song_url,r'collect/(\d+).*',u'http://www.xiami.com/song/playlist/id/{0}/type/3/cat/json')
				self.write(result)
			else:
				result = self._search_song(song_url,u'http://www.xiami.com/song/playlist/id/{0}/object_name/default/object_id/0/cat/json')
				self.write(result)
		except Exception as error:
			logger.exception('Exception loggered')
			self.write("false")


	#根据歌曲链接搜索
	def _handle(self,url,re_val,template):
		match = re.search(re_val,url)
		song_id = match.group(1)
		locationUrl = template.format(song_id)
		result = self._send_request(locationUrl)
		return self._parse_result(result)

	#根据歌曲名搜索
	def _search_song(self,song,template):
		return_vals = []
		resp = self._send_request('http://www.xiami.com/search/song?key=' + song)
		pq = PyQuery(resp)
		song_tds = pq(".track_list .song_name")
		song_artist_tds = pq(".track_list .song_artist")
		chkboxs = pq(".track_list .chkbox")
		for i in range(song_tds.size()):
			song_td = song_tds[i]
			song_artist = song_artist_tds[i]
			chkbox = chkboxs[i]
			song_html = lxml.html.tostring(song_td,encoding='utf-8')
			chk_html = lxml.html.tostring(chkbox,encoding='utf-8')
			song_artist = PyQuery(song_artist)("a").text()
			#logger.info(song_html + "  " + chk_html)
			if chk_html.find('disabled') != -1:
				continue

			match = re.search(r'song/(\d+).*',song_html)
			if match:
				locationUrl = template.format(match.group(1))
				response = self._send_request(locationUrl)
				result = self._parse_result(response)
				result_json = tornado.escape.json_decode(result)[0];
				result_json['title'] = result_json['title'] + '--' + song_artist
				return_vals.append(result_json)
		return tornado.escape.json_encode(return_vals)


	def _send_request(self,url):
		headers = {}
		headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'
		resp = requests.get(url=url,headers=headers)
		return resp.text

	def _parse_result(self,result):
		result = tornado.escape.json_decode(result)
		return_vals = []
		songs = result['data']['trackList']
		for song in songs:
			return_val = {}
			return_val['title'] = song['title']
			return_val['pic'] = song['pic']
			return_val['lyric'] = song['lyric_url']
			return_val['location'] = util.decode_location(song['location'])

			return_vals.append(return_val)
		
		return tornado.escape.json_encode(return_vals)

	def write_error(self, status_code, **kwargs):
		logger.info(kwargs)
		self.write(status_code)
		


