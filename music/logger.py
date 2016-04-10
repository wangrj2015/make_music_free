# -*- coding: utf-8 -*-

import logging
import logging.config

logging.config.fileConfig("logger.conf")

class LoggerFactory():

	@staticmethod
	def getLogger(loggerName='music'):
		return logging.getLogger(loggerName)
