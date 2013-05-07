##------------------------------------------------------------------------------
## CliApp setup script
##------------------------------------------------------------------------------

import sys
from setuptools import setup, find_packages

version = __import__('cliapp').__version__
if 'cliapp' in sys.modules:
    ## Unload to prevent issues with Py3k/2to3 built code
    del sys.modules['cliapp']

test_requires = []
if sys.version_info < (2, 7):
    test_requires.append('unittest2')

setup(
    name='CliApp',
    version=version,
    url='http://github.com/rshk/cliapp',
    author='Samuele ~redShadow~ Santi',
    author_email='redshadow@hackzine.org',
    description='',
    license='Apache License, Version 2.0, January 2004',

    packages=find_packages(),
    install_requires=[
        'distribute',
    ],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 2.7",
    ],

    ## Package data
    include_package_data=True,
    package_data={'': ['README.rst', 'LICENSE']},

    ## Testing stuff
    test_requires=test_requires,
    test_suite='cliapp.tests',

    ## todo: add py3k stuff
)
