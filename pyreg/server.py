from __future__ import with_statement
import sys
from pyreg import browser
import logging
import threading
import traceback

import IPython
from IPython.Shell import IPShellEmbed
def start():
	
	ipshell = IPShellEmbed(sys.argv[1:], user_ns=scope)
	#ipshell.IP.runlines('from pylab import ion; ion()')
	ipshell()
	
	# Put this here to help pyglet clean up apps immediately
	# Pointless if no one is using pyglet, oh well
	try: 
		import pyglet
		pyglet.app.exit() 
	except: pass
	sys.exit()
	
def main():
	global scope
	scope = dict()

	# TODO: Parse command line options, find 'port'
	port = 21000
	browser.setup(scope, port)
	#print("Ajax Server started...")
	logging.disable(logging.WARNING)
	
	thread = threading.Thread(target=start)
	thread.start()
	
	try:
		for f in sys.argv[1:]:
			execfile(f, scope)
	except Exception, e:
		traceback.print_exc()
		
	browser.start()
	thread.join()
	
if __name__ == "__main__":	
	main()

