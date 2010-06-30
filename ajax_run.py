from __future__ import with_statement
import sys
import pyreg
import logging
import threading
#import pyglet
import traceback

if __name__ == "__main__":	

	scope = dict()

	# TODO: Parse command line options, find 'port'
	port = 21000
	pyreg.setup(scope, port)
	#print("Ajax Server started...")
	logging.disable(logging.WARNING)
	
	from IPython.Shell import IPShellEmbed
	def ajax_run():
		IPShellEmbed(sys.argv[1:], user_ns=scope)()
		# Put this here to help pyglet clean up apps immediately
		# Pointless if no one is using pyglet, oh well
		#pyglet.app.exit()
		sys.exit()
		
	thread = threading.Thread(target=ajax_run)
	thread.start()
	
	try:
		for f in sys.argv[1:]:
			execfile(f, scope)
	except Exception, e:
		traceback.print_exc()
		
	pyreg.start()
	thread.join()
