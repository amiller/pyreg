import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import traceback

import os
import string
import thread
import simplejson as json
import time
import logging
import sys
from Queue import Queue


def getpipe():
	r, w = os.pipe()
	return os.fdopen(r,'r',0), os.fdopen(w,'w',0)
	
class MainHandler(tornado.websocket.WebSocketHandler):
	longin, longout = getpipe()
	longqueue = Queue()
	receivers = []
	
	@classmethod
	def _write_handle(cls):
		print 'written'
	
	@classmethod
	def _push_handler(cls, fd, events):
		cls.longin.read(1)
		cmd = cls.longqueue.get()
		item = {'push':cmd}
		# Put it on the cache, notify all the waiters
		cls.receivers = [x for x in cls.receivers if not x.stream.closed()]
		for receiver in cls.receivers:
			receiver.writeback(item)

	@classmethod
	def setup(cls):
		loop = tornado.ioloop.IOLoop.instance()
		loop.add_handler(cls.longin.fileno(), cls._push_handler, loop.READ)
		loop._set_nonblocking(cls.longin.fileno())
	
	def writeback(self, jsonobj):
		if not self.stream.closed():
			self.write_message(json.dumps(jsonobj))

	def open(self):
		self.receive_message(self.on_message)
		MainHandler.receivers.append(self)
		#print 'opened', self
		
	def close(self):
		MainHandler.receivers.remove(self)
		
	def on_message(self, message):
		self.receive_message(self.on_message)

		args = json.loads(message)
		action = args['action']
		cmd = args['cmd']
		sendid = args['sendid']
		
		if action == 'exec':
			try:
				exec(cmd, MainHandler.scope)
				self.writeback({'sendid':sendid, 'result':'ok'})
			except Exception, e:
				self.writeback({'sendid':sendid, 'error':str(e)})
				logging.error(traceback.format_exc())
			
		elif action == 'eval':
			try:
				result = eval(cmd, MainHandler.scope)
				self.writeback({'sendid':sendid, 'result':result})
			except Exception, e:
				self.writeback({'sendid':sendid, 'error':str(e)})
				logging.error(traceback.format_exc())
		


def setup(scope, port=21000):
	MainHandler.scope = scope
	MainHandler.setup()
	settings = {
		"static_path": "."
	}
	application = tornado.web.Application([
		(r"/ws/websocket", MainHandler),
	], **settings)
	http_server = tornado.httpserver.HTTPServer(application)
	http_server.listen(port)
	
	thread.start_new(tornado.ioloop.IOLoop.instance().start,())
	
def push(cmd):
	MainHandler.longqueue.put(cmd)
	MainHandler.longout.write('x')	# Pipe interleaving doesn't matter
	MainHandler.longout.flush()
	
	
from Image import Image
from StringIO import StringIO
import base64
def writeimage(selector, img):
	# Save the image to a temp file

	# Save as jpeg
	s = StringIO()
	img.save(s,'jpeg')

	# b64 encode
	d = base64.b64encode(s.getvalue())
	push("$('%s').attr('src','data:image/jpeg;base64,%s')" % (selector, d))
