##########
CliApp
##########

.. image:: https://travis-ci.org/rshk/CliApp.png
    :alt: Build status
    :target: https://travis-ci.org/rshk/CliApp
    :align: right

:Build status:
:Version: 0.1
:Author: Samuele Santi


Library to ease the creation of CLI applications in Python.

This is especially useful for applications that allow some global
options (through the ``optparse`` module), a command and some
options and arguments to be passed to the command.

Example usage:

.. code-block: python

    from cliapp import CliApp

    app = CliApp()
    app.parser.add_option('--debug', dest='debug', action='store_true',
        default='False', help='Enable debugging')

    @app.command(usage="<name>")
    def hello(state):
        if len(state.arguments) > 0:
            print "Hello, {0}!".format(state.arguments[0])
        else:
            print "Hello, world!"

    @app.command
    def hello_world(state):
        print "Hello, world!"


    if __name__ == '__main__':
        app.run()

And then use it like this::

    $ python myapp.py
    A command is required! See --help-commands.

    $ python myapp.py --help
    Usage: myapp.py [options]

    Options:
      -h, --help       show this help message and exit
      --help-commands  Print commands usage help.
      --debug          Enable debugging

    $ python myapp.py --help-commands
    Accepted commands:

    hello <name>

    hello_world [<opts>] [<args>]


    $ python myapp.py hello
    Hello, world!

    $ python myapp.py hello user
    Hello, user!

    $ python myapp.py hello --help
    Usage: <name>

    Options:
      -h, --help  show this help message and exit

    $ python myapp.py hello aa
    Hello, aa
