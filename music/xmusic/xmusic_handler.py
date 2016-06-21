# -*- coding: utf-8 -*-

import tornado.web
import tornado.escape
import tornado.gen
from tornado.httpclient import AsyncHTTPClient,HTTPRequest
import requests
import re
from logger import LoggerFactory
from elastic_helper import ElasticHelper
import util
import traceback
from pyquery import PyQuery
import lxml
from urllib import quote

logger = LoggerFactory.getLogger()

class XMusicHandler(tornado.web.RequestHandler):

	headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'}

	def set_default_headers(self):
		self.set_header('Access-Control-Allow-Origin', '*')
		self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
		self.set_header('Access-Control-Allow-Headers', '*')

	@tornado.web.asynchronous
	def get(self):
		try:
			song_url = self.get_argument('song_url')
			if len(song_url)==0 :
				self.write("false")
				return
			logger.info('IP:'+self.request.headers.get("X-Real-Ip",'')+' song_url:' + song_url)
			#单首歌
			if song_url.find('song') != -1:
				self._handle(song_url,r'song/(\d+).*',u'http://www.xiami.com/song/playlist/id/{0}/object_name/default/object_id/0/cat/json')
			#专辑
			elif song_url.find('album') != -1:
				self._handle(song_url,r'album/(\d+).*',u'http://www.xiami.com/song/playlist/id/{0}/type/1/cat/json')
			#精选集
			elif song_url.find('collect') != -1:
				self._handle(song_url,r'collect/(\d+).*',u'http://www.xiami.com/song/playlist/id/{0}/type/3/cat/json')
			else:
				self._search_result = []
				#1.search elastic
				self._search_song_from_elastic(song_url)
				#2.search xiami
				self._search_song_from_xiami(song_url,u'http://www.xiami.com/song/playlist/id/{0}/object_name/default/object_id/0/cat/json')
		except Exception as error:
			logger.exception('Exception loggered')
			self.write("false")
			self.finish()


	#根据歌曲链接搜索
	def _handle(self,url,re_val,template):
		match = re.search(re_val,url)
		song_id = match.group(1)
		locationUrl = template.format(song_id)

		def _callback(response):
			result = self._parse_result(response.body)
			self.write(tornado.escape.json_encode(result))
			self.finish()

		AsyncHTTPClient().fetch(HTTPRequest(url=locationUrl,headers=self.headers),_callback)


	#根据歌曲名搜索
	def _search_song_from_xiami(self,song,template):
		url = 'http://www.xiami.com/search/song?key=' + quote(song.encode('utf-8'))
		
		@tornado.gen.coroutine
		def _callback(response):
			try:
				pq = PyQuery(response.body)
				song_tds = pq(".track_list .song_name")
				song_artist_tds = pq(".track_list .song_artist")
				chkboxs = pq(".track_list .chkbox")

				location_urls = []
				song_artists = {}
				for i in range(song_tds.size()):
					song_td = song_tds[i]
					song_artist = song_artist_tds[i]
					chkbox = chkboxs[i]
					song_html = lxml.html.tostring(song_td,encoding='utf-8')
					chk_html = lxml.html.tostring(chkbox,encoding='utf-8')
					song_artist = PyQuery(song_artist)("a").text()
					if chk_html.find('disabled') != -1:
						continue

					match = re.search(r'song/(\d+).*',song_html)
					if match:
						location_urls.append(template.format(match.group(1)))
						song_artists[match.group(1)] = song_artist
				resp = yield [AsyncHTTPClient().fetch(HTTPRequest(url=locationUrl,headers=self.headers)) for locationUrl in location_urls]

				for i in range(len(resp)):
					response = resp[i]
					result = self._parse_result(response.body)
					result_json = result[0];
					song_id = result_json['song_id']
					result_json['title'] = result_json['title'] + '--' + song_artists[song_id]
					self._search_result.append(result_json)
			except Exception as error:
				logger.exception('Exception loggered')

			if len(self._search_result) > 0 :
				self.write(tornado.escape.json_encode(self._search_result))	
				self.finish()
			else:
				self.write('false')
				self.finish()


		AsyncHTTPClient().fetch(HTTPRequest(url=url,headers=self.headers),_callback)


	def _search_song_from_elastic(self,song_url):

		def _callback(result):
			if not result:
				return
			self._search_result.append(result)

		try:
			query = '{"query":{"match":{"name":"'+song_url+'"}}}'
			ElasticHelper().search(query,_callback)	
		except Exception as error:
			logger.exception('Exception loggered')


	def _parse_result(self,result):
		result = tornado.escape.json_decode(result)
		songs = result['data']['trackList']
		return_vals = []
		for song in songs:
			return_val = {}
			return_val['title'] = song['songName']
			return_val['pic'] = song['pic']
			return_val['lyric'] = song['lyric_url']
			return_val['song_id'] = song['song_id']
			return_val['location'] = util.decode_location(song['location'])
      if song.get('purview'):
        location_high = song.get('purview').get('filePath')
        if location_high and 'http' in location_high:
          return_val['location'] = location_high      

			return_vals.append(return_val)
		
		return return_vals


	def write_error(self, status_code, **kwargs):
		logger.info(kwargs)
		self.write(status_code)
		


