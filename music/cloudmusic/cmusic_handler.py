# -*- coding: utf-8 -*-

import tornado.web
import tornado.escape
import tornado.gen
from tornado.httpclient import AsyncHTTPClient,HTTPRequest
import requests
import re
from logger import LoggerFactory
import config
from pyquery import PyQuery
import lxml
from urllib import quote
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

logger = LoggerFactory.getLogger()

class CMusicHandler(tornado.web.RequestHandler):

	headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'}

	web_driver = webdriver.PhantomJS()
	wait = WebDriverWait(web_driver,30)

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
			self._search_song(song_url)
		except Exception as error:
			logger.exception('Exception loggered')
			self.write("false")
			self.finish()


	@tornado.gen.coroutine
	def _search_song(self,song_url):
		try:
			url = "http://music.163.com/#/search/m/?s="+quote(song_url.encode('utf-8'))+"&type=1"
			self.web_driver.get(url)
			self.web_driver.switch_to.frame(self.web_driver.find_element_by_xpath("//iframe"))
			self.wait.until(lambda driver: driver.find_element_by_class_name('srchsongst'))
			
			pq = PyQuery(self.web_driver.page_source)
			song_list = pq(".srchsongst div.item")
			song_ids = {}
			location_urls = []
			for i in range(song_list.size()):
				song_div = PyQuery(song_list[i])
				id_a = song_div("a[data-res-id]")
				song_id = id_a.attr("data-res-id")
				song_name = song_div("div.w0 b[title]").attr("title")
				artist_name= song_div("div.w1 a").text()
				title = song_name + '--' + artist_name
				if song_id:
					song_ids[int(song_id)] = title
					location_urls.append(config.node_server + "/geturl?id=" + song_id)
			resp = yield [AsyncHTTPClient().fetch(HTTPRequest(url=locationUrl,headers=self.headers)) for locationUrl in location_urls]
			return_vals = []

			for i in range(len(resp)):
				response = tornado.escape.json_decode(resp[i].body)
				re_song_id = response['data'][0]['id']
				re_location = response['data'][0]['url']
				return_val = {}
				return_val['title'] = song_ids.get(re_song_id)
				return_val['location'] = re_location
				return_val['song_id'] = re_song_id
				return_val['pic'] = config.default_pic
				if re_location:
					return_vals.append(return_val)

			self.write(tornado.escape.json_encode(return_vals))
			self.finish()
		except Exception as error:
			logger.exception('Exception loggered')
			self.web_driver.quit()
			self.web_driver = webdriver.PhantomJS()
			self.wait = WebDriverWait(self.web_driver,30)
			self.write("false")
			self.finish()

