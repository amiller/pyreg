import subprocess

def shell(cmd):
	p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
	return p.communicate()[0].split('\n')[:-1]