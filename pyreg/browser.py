from twisted.internet import reactor
from websocket import WebSocketHandler, WebSocketSite
from twisted.web.static import File

import traceback
import os
import string
import thread
import simplejson as json
import time
import logging
import sys
	
class MainHandler(WebSocketHandler):
	receivers = []
		
	def __init__(self, transport):
		WebSocketHandler.__init__(self, transport)
		MainHandler.receivers.append(self)
	
	def connectionLost(self, reason):
		MainHandler.receivers.remove(self)
	
	@classmethod
	def setup(cls):
		pass
	
	def writeback(self, jsonobj):
		self.transport.write(json.dumps(jsonobj))
		
	def frameReceived(self, message):
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
		

	@classmethod
	def _push(cls, cmd):
		item = {'push':cmd}
		for receiver in cls.receivers:
			receiver.writeback(item)
def start():
	thread.start_new_thread(reactor.run, (), {'installSignalHandlers':0})

def setup(scope, port=21000):
	MainHandler.scope = scope
	MainHandler.setup()
	root = File(".")
	root.putChild('_pyreg',File(os.path.dirname(__file__)+'/_pyreg'))
	site = WebSocketSite(root)
	site.addHandler("/ws/websocket", MainHandler)
	reactor.listenTCP(port, site)
	

def push(cmd):
	reactor.callFromThread(MainHandler._push, cmd)
	
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
