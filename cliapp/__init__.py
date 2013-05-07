"""
Helpers to create CLI applications.

The "standard" application accepts a bunch of options,
followed by a command that can accept options + arguments.

Example invokation::

    myapp.py --dir=/tmp/hello --async create --force --title="Yeah!" Hello

Getting help:

    myapp.py --help
        Will print help about the application options

    myapp.py --help-commands
    myapp.py help
        Will print help about the available commands

    myapp.py help <command>
    myapp.py <command> --help
        Will print help about a specific command
"""

__version__ = '0.1'


import textwrap
from optparse import OptionParser
from collections import OrderedDict


def _indent(text, prefix='    '):
    text = textwrap.dedent(text.strip())
    return "\n".join(prefix + line for line in text.splitlines())


class CliApp(object):
    def __init__(self):
        self._parser = OptionParser()
        self._parser.disable_interspersed_args()
        self._parser.add_option(
            '--help-commands', dest='X_help_commands', default=False,
            action="store_true", help="Print commands usage help.")
        self._commands = OrderedDict()

    def command(self, func=None, name=None, usage=None, help_text=None,
                 options=None):
        """
        Register a function as a command.

        :param func:
            The callable to be used to handle the command.
            A single argument, state, will be passed.
            If ``func`` is None, a suitable decorator will be returned
            instead of registering the function.
        :param name:
            The command name. If not specified, the function name
            will be used.
        :param usage:
            A brief usage description. Defaults to "[<opts>] [<args>]".
        :param help_text:
            A, possibly longer, help text for the command.
            If not specified, the function docstring will be used.
        :param options:
            Options to be added to the parser.
            Use optparse.make_option() to create those.
        """
        def decorator(func):
            def method_proxy(*a, **kw):
                return func(*a, **kw)
            if not callable(func):
                raise ValueError("function must be callable!")
            # name = name
            # if name is None:
            #     name = func.__name__
            _name = name or func.__name__
            method_proxy.name = _name
            method_proxy.__name__ = _name
            method_proxy.usage = \
                usage if usage is not None else "[<opts>] [<args>]"
            method_proxy.help_text = \
                help_text if help_text is not None else func.__doc__
            method_proxy.options = options
            self._commands[_name] = method_proxy
            return func

        # If func is not None, it means the method
        # has been used either as a simple decorator
        # or as a plain method. The function will be
        # registered by calling decorator, otherwise,
        # decorator will be returned.
        if func:
            return decorator(func)
        return decorator

    def lookup(self, method):
        return self._commands[method]

    @property
    def methods(self):
        return self._commands.iteritems()

    @property
    def parser(self):
        return self._parser

    def run(self):
        try:
            return self._run()

        except ShowCommandsHelp, e:
            if e.message:
                print(e.message)
            self._print_commands_help()

        except CommandError, e:
            print(e.message)
            return 1

    def _run(self):
        """Run the application"""

        ## Parse command-line options
        opts, args = self._parser.parse_args()

        if opts.X_help_commands:
            self._print_commands_help()
            return

        if len(args) == 0:
            raise InvalidUsage("A command is required! See --help-commands.")

        command_name = args[0]
        command_args = args[1:]

        if opts.X_help_commands or command_name == 'help':
            self._print_commands_help()
            return

        command = self.lookup(command_name)
        parser = OptionParser(
            usage=command.usage,
            description=command.help_text,
            prog=command.name)
        if command.options is not None:
            for opt in command.options:
                parser.add_option(opt)
        cmd_opts, cmd_args = parser.parse_args(command_args)

        state = State(
            app=self, global_options=opts, command=command_name,
            options=cmd_opts, arguments=cmd_args)

        return command(state)

    def _print_commands_help(self, args=None):
        if args is None or len(args) == 0:
            print("Accepted commands:\n")
            for name, command in self.methods:
                self._print_command_usage(command)
                print("")
        else:
            name = args[0]
            command = self.lookup(name)
            self._print_command_usage(command)

    def _print_command_usage(self, command):
        usage = getattr(command, 'usage', None) or ""
        cmd_usage = "{name} {usage}".format(name=command.name, usage=usage)
        print(cmd_usage)
        if hasattr(command, 'help_text') and command.help_text:
            print(_indent(command.help_text, ' ' * 8))


class State(object):
    """
    Used to keep state of the current invokation.
    """
    def __init__(self, app, global_options, command, options, arguments):
        self.app = app
        self.global_options = global_options
        self.command = command
        self.options = options
        self.arguments = arguments


##==============================================================================
## Exceptions
##==============================================================================

class CommandError(Exception):
    pass


class InvalidUsage(CommandError):
    pass


class ShowCommandsHelp(CommandError):
    def __init__(self, message=None, args=None):
        super(ShowCommandsHelp, self).__init__(message)
        self.args = args
