# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

import tornado.ioloop
import tornado.web
import config
from logger import LoggerFactory
import sys
import tornado.websocket

class ChatHandler(tornado.websocket.WebSocketHandler):
    clients = set()

    def check_origin(self, origin):
    	return True

    def open(self):
        ChatHandler.clients.add(self)

    def on_close(self):
    	ChatHandler.clients.remove(self)


    def on_message(self,message):
    	LoggerFactory.getLogger().info(message)
    	ChatHandler.send_to_all(message)

    @staticmethod
    def send_to_all(message):
    	for client in ChatHandler.clients:
    		client.write_message(message)



application = tornado.web.Application([
	(r"/chat", ChatHandler),
])

if __name__ == "__main__":
    application.listen(sys.argv[1])
    LoggerFactory.getLogger().info("server starting at port: %s" % sys.argv[1])
    tornado.ioloop.IOLoop.instance().start()