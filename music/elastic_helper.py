# -*- coding: utf-8 -*-

from tornado.httpclient import AsyncHTTPClient,HTTPRequest
import tornado.gen
import config
from logger import LoggerFactory

class ElasticHelper():

	server_url = config.elastic_server

	default_pic = config.default_pic

	@tornado.gen.coroutine
	def search(query,callback):
		try:
			response = yield AsyncHTTPClient().fetch(url=server_url + 'music/collect/_search',body=query)
			response_json = tornado.escape.json_decode(response.body)
			LoggerFactory.getLogger().info(response_json)
			data_array = response_json['hits']['hits']
			if len(data) > 0:
				data = data_array[0]
				source = data['_source']
				result = {}
				result['pic'] = default_pic
				result['title'] = source['name'] + '--' + source['artist']
				result['location'] = source['location']
				callback(result)
		except Exception as error:
			LoggerFactory.getLogger().exception()