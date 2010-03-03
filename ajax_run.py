from SocketServer import *
from BaseHTTPServer import *
from SimpleHTTPServer import *
from Queue import Queue
import os
import string
import thread
import urlparse
import simplejson as json
from threading import Lock

class RequestHandler(SimpleHTTPRequestHandler):
	
	def writeback(self, jsonobj):
		self.send_response(200)
		self.send_header('Content-type', 'text/plain')
		self.end_headers()
		self.wfile.write('%s(' % (self.jc,))
		self.wfile.write(json.dumps(jsonobj))
		self.wfile.write(')\n')
	
	def do_GET(self):
		print("request: %s" % (self.path,))
		
		if not self.client_address[0] == '127.0.0.1':
			return
		
		if self.path.startswith("/"):
			try:
				o = urlparse.urlparse(self.path)
				qs = o.query
				d = urlparse.parse_qs(qs)
				args = d['args'][0]
				args = json.loads(args)
				self.jc = d['callback'][0]
				
				action = args['action']
				
				if action == 'exec':
					cmd = args['cmd']
					_exec(cmd)
					self.writeback('ok')
					
				elif action == 'eval':
					cmd = args['cmd']
					self.writeback(eval(cmd, server.g))
					
				elif action == 'longpoll':
					q = server.queue.get()

					while 1:
						try:
							q += server.queue.get(None)
						except Exception as e:
							break
							
					self.writeback(q)

					
				else:
					raise Exception('No action specified!')
				
			except Exception as e:
				self.send_response(500)
				self.end_headers()
				self.wfile.write(str(e))
				raise

		#else if self.path.startswith("/static/"):
		#	SimpleHTTPRequestHandler.do_GET(self)
		
		else:
			self.send_response(404)
			self.end_headers()
	
class Server(ThreadingMixIn, HTTPServer):

	def __init__(self, g, port=21000):
		self.g = g
		self.queue = Queue()	
		HTTPServer.__init__(self, ('localhost',port),RequestHandler)


	def push(self, js):
		self.queue.put(js)
	

if __name__ == '__main__':
	server = Server(globals())
	thread.start_new(server.serve_forever,())
	print("Ajax Server started...")
	
	import sys
	for f in sys.argv[1:]:
		execfile(f)

	from IPython.Shell import IPShellEmbed
	IPShellEmbed(sys.argv[1:], user_ns=globals())()
	
