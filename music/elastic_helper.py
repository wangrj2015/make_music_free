# -*- coding: utf-8 -*-

from tornado.httpclient import AsyncHTTPClient,HTTPRequest
import tornado.gen
import config
from logger import LoggerFactory

logger = LoggerFactory.getLogger()

class ElasticHelper():

	server_url = config.elastic_server

	default_pic = config.default_pic

	@tornado.gen.coroutine
	def search(self,query,callback):
		try:
			response = yield AsyncHTTPClient().fetch(HTTPRequest(url=self.server_url + 'music/collect/_search',method='POST',body=query))
			response_json = tornado.escape.json_decode(response.body)
			data_array = response_json['hits']['hits']
			if len(data_array) > 0:
				for data in data_array:
					source = data['_source']
					result = {}
					result['pic'] = self.default_pic
					result['title'] = source['name'] + '--' + source['artist']
					result['location'] = source['location'] + '?attname='
					callback(result)
		except Exception as error:
			logger.exception('Exception')