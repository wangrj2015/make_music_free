import tornado.web
from logger import LoggerFactory

class SuggestHandler(tornado.web.RequestHandler):

	def set_default_headers(self):
		self.set_header('Access-Control-Allow-Origin', '*')
		self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
		self.set_header('Access-Control-Allow-Headers', '*')

	def post(self):
		info = self.get_argument('info')
		LoggerFactory.getLogger().info('IP:'+self.request.headers.get("X-Real-Ip",'') + ' suggest:' + info)
		self.write('true')


	def write_error(self, status_code, **kwargs):
		LoggerFactory.getLogger().info(kwargs)
		self.write(status_code)