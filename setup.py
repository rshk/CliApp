##------------------------------------------------------------------------------
## CliApp setup script
##------------------------------------------------------------------------------

import sys
from setuptools import setup, find_packages

version = '0.1'

extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True
    #extra['convert_2to3_doctests'] = ['src/your/module/README.txt']
    #extra['use_2to3_fixers'] = ['your.fixers']

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

    **extra
)
