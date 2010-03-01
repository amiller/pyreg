from SocketServer import *
from BaseHTTPServer import *
from SimpleHTTPServer import *
import os
import string
import thread
import urlparse
import simplejson as json
import signal
from threading import Lock
from subprocess import *
from rpyc import classic

class RequestHandler(SimpleHTTPRequestHandler):
	
	def writeback(self, jsonobj):
		self.send_response(200)
		self.send_header('Content-type', 'text/plain')
		self.end_headers()
		self.wfile.write('%s(' % (self.jc,))
		self.wfile.write(json.dumps(jsonobj))
		self.wfile.write(')\n')
		
	def writeprocs(self):
		obj = [{'pid':p['proc'].pid, 'cmd':p['cmd']} for p in server.procs.values()]
		print obj
		self.writeback(obj)
	
	def do_GET(self):
		print("request: %s" % (self.path,))
		
		if not self.client_address[0] == '127.0.0.1':
			return
		
		if self.path.startswith("/procs/"):
			try:
				prevdir = os.getcwd()
				
				o = urlparse.urlparse(self.path)
				qs = o.query
				d = urlparse.parse_qs(qs)
				args = d['args'][0]
				curdir = d['dir'][0]
				args = json.loads(args)
				port = args['port']
				self.jc = d['callback'][0]
				
				os.chdir(curdir)
				
				action = args['action']
				if action == 'spawn':
					cmd = args['cmd']
					proc = Popen(cmd, close_fds=True, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)		
					with server.lock:
						server.procs[proc.pid] = {'proc':proc, 'cmd':cmd}					
					if args.has_key('stdin'):
						proc.stdin.write(args['stdin'])
					
					if args.has_key('wait') and args['wait']:
						self.writeback({'pid':proc.pid, 'stdout':proc.stdout.read()})
						
					else:
						self.writeback({'pid':proc.pid})	
						
				elif action == 'rpycexec':
					cmd = args['cmd']
					c = classic.connect('localhost',port)
					c.root.mainexecute(cmd)
					self.writeback('ok')
					
				elif action == 'rpyceval':
					cmd = args['cmd']
					c = classic.connect('localhost',port)
					result = classic.obtain(c.root.maineval(cmd))
					print json.dumps(result)
					self.writeback({'result':result})
			
				elif action == 'python':
					cmd = 'python rpyc_run.py %s' % (args['script'],)
					proc = Popen(cmd, close_fds=True, shell=True,
						stdin=PIPE, stdout=None, stderr=None)
						
					with server.lock:
						server.procs[proc.pid] = {'proc':proc, 'cmd':cmd, 'dir':curdir}					

					self.writeback({'pid':proc.pid})
						
					
				elif action == 'kill':
					pid = args['pid']
					with server.lock:
						p = server.procs[pid]
						p['proc'].kill()
						server.procs.pop(pid)
					self.writeprocs()
				
				elif action == 'list':
					self.writeprocs()
					
				else:
					raise Exception('No action given!')
				
			except Exception as e:
				self.send_response(500)
				self.end_headers()
				self.wfile.write(str(e))
				raise
				
			finally:
				os.chdir(prevdir)

		#else if self.path.startswith("/static/"):
		#	SimpleHTTPRequestHandler.do_GET(self)
			
		else:
			self.send_response(404)
			self.end_headers()
	
class Server(ThreadingMixIn, HTTPServer):

	def __init__(self):
		self.lock = Lock()
		self.procs = {}
		HTTPServer.__init__(self, ('',21000),RequestHandler)
	
		
def handler(signum, frame):
	with server.lock:
		server.procs = dict([(pid,p) for pid,p in server.procs.items() if p['proc'].poll() == None])
		print "Zombies purged, remaining procs: ", len(server.procs)
		
def on_exit():
	with server.lock:
		for p in server.procs.values():
			p['proc'].kill()

if __name__ == '__main__':
	signal.signal(signal.SIGCHLD, handler)
	server = Server()
	thread.start_new(server.serve_forever,())
	print("Process Server started...")
	
	import atexit
	atexit.register(on_exit)
	
	
	