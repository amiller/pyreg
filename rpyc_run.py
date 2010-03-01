from rpyc import classic
from rpyc.utils.server import ThreadedServer
import threading
import sys
import os
from Queue import Queue
from threading import Event

from IPython.Shell import IPShellEmbed

def ex(text, g):
	exec(text, g)

class MySlave(classic.SlaveService):
	def exposed_maineval(self, text):
		d = {'text':text, 'f':eval, 'event':Event()}
		queue.put(d)
		d['event'].wait()
		return d['result']
		
	def exposed_mainexecute(self, text):
		queue.put({'text':text, 'f':ex})
		
	def exposed_eval(self, text):
		return eval(text, locals(), globals())
		
	def exposed_execute(self, text):
		exec(text, locals(), globals())

queue = Queue()

def shell():
	IPShellEmbed()()
	import os
	os._exit(0)
	
def start(port):
	# Start the rpyc server
	s = ThreadedServer(MySlave, port=port, protocol_config=
		{'allow_pickle': True, 
		'allow_public_attrs': True}, auto_register=False)
	t = threading.Thread(target=s.start)
	t.start()
	
	t2 = threading.Thread(target=shell)
	t2.start()
	
	while True:
		# Get a message from the queue, evaluate the function, flag event and return
		d = queue.get()
		d['result'] = d['f'](d['text'], globals())
		if d.has_key('event'):
			d['event'].set()
		print 'its done'
	
	t.join()
	t2.join()

if __name__ == '__main__':

	if len(sys.argv) >= 2:
		# Run the python file indicated by the cmd opts
		script = sys.argv[1]	
		execfile(script)
	
	port = 9001	
	if len(sys.argv) >= 3:
		port = sys.argv[2]

	start(port)
		
	


