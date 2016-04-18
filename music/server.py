# -*- coding: utf-8 -*-

import tornado.ioloop
import tornado.web
import config
from logger import LoggerFactory
from xmusic.xmusic_handler import XMusicHandler
from suggest_handler import SuggestHandler
import sys



application = tornado.web.Application([
	(r"/xmusic", XMusicHandler),
	(r"/suggest", SuggestHandler),
	(r"/download/(.*)", tornado.web.StaticFileHandler, {"path": config.resource_dir}),
])

if __name__ == "__main__":
    application.listen(sys.argv[1])
    LoggerFactory.getLogger().info("server starting at port: %s" % sys.argv[1])
    tornado.ioloop.IOLoop.instance().start()