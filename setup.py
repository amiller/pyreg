from setuptools import setup, find_packages
setup(
	name="pyreg",
	version="0.1",
	packages=find_packages(),
	
	package_data={
		'pyreg': ['_pyreg/*']
	},
	
	requires = ['IPython','simplejson','PIL','bunch','twisted','IPython'],
	install_requires = ['setuptools'],
	
	author="Andrew Miller",
	author_email="amiller@dappervision.com",
	description="Pyreg uses websockets to hook a python instance up with a \
	 browser running javascript. "
)