import sys
import pyreg
if __name__ == "__main__":	

	scope = dict()

	# Parse command line options, find 'port'
	port = 21000
	pyreg.setup(scope, port)
	#print("Ajax Server started...")
	
	try:
		for f in sys.argv[1:]:
			execfile(f, scope)
	except Exception as e:
		print e
		
	from IPython.Shell import IPShellEmbed
	IPShellEmbed(sys.argv[1:], user_ns=scope)()
