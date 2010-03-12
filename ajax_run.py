from __future__ import with_statement
import sys
import pyreg
import logging

if __name__ == "__main__":	

	scope = dict()

	# TODO: Parse command line options, find 'port'
	port = 21000
	pyreg.setup(scope, port)
	#print("Ajax Server started...")
	logging.disable(logging.WARNING)
	
	try:
		for f in sys.argv[1:]:
			execfile(f, scope)
	except Exception, e:
		print e
	
	from IPython.Shell import IPShellEmbed
	IPShellEmbed(sys.argv[1:], user_ns=scope)()
