from rpyc import classic
import sys
from IPython.Shell import Term, IPShellEmbed
import IPython
# Con

c = None
root = None

def connect(port=9001):
	# Connect to rpyc
	global c
	c = classic.connect('localhost',port)
	c.modules.IPython = IPython
	
	#c.modules.sys.stdout = sys.stdout
	#c.modules.sys.stdin = sys.stdin
	#c.modules.sys.stderr = sys.stderr
	
	#c.root.shell(Term.cin, Term.cerr, Term.cout)
	global root
	root = c.root
	c.root.shell()
	
	global A
	A = 5