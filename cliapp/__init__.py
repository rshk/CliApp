"""
Helpers to create CLI applications.

The "standard" application accepts a bunch of options,
followed by a command that can accept options + arguments.

Example invokation::

    myapp.py --dir=/tmp/hello --async create --force --title="Yeah!" Hello

Getting help::

    myapp.py --help
        Will print help about the application options

    myapp.py --help-commands
    myapp.py help
        Will print help about the available commands

    myapp.py help <command>
    myapp.py <command> --help
        Will print help about a specific command
"""
import re
import sys
import traceback
import readline

__version__ = '0.1'


import textwrap
from optparse import OptionParser
from collections import OrderedDict


def _indent(text, prefix='    '):
    text = textwrap.dedent(text.strip())
    return "\n".join(prefix + line for line in text.splitlines())


class CliApp(object):
    use_colors = True
    enable_commands_help = True
    enable_interactive = True
    auto_interactive = True
    complete_key = 'tab'
    prompt = None

    def __init__(self, use_colors=True, enable_commands_help=True,
                 enable_interactive=True, auto_interactive=True):
        self.use_colors = use_colors
        self.enable_interactive = True
        self.auto_interactive = auto_interactive and enable_interactive
        self._opts, self._args = None, None

        if self.prompt is None:
            if self.use_colors:
                self.prompt = '\001\033[1;32m\002cliapp>\001\033[0m\002 '
            else:
                self.prompt = 'cliapp> '

        ## Prepare the main parser
        self._parser = OptionParser(usage="%prog [options] <command> [args...]")
        self._parser.disable_interspersed_args()
        self._parser.add_option(
            '--help-commands', dest='X_help_commands', default=False,
            action="store_true", help="Print commands usage help.")

        ## Prepare the commands register
        self._commands = OrderedDict()

        ## Create the "help" command, if instructed to do so
        if enable_commands_help:
            self.command(
                lambda state: self._print_commands_help(),
                name='help',
                usage='',
                help_text="Show commands usage")

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
            _name = name or func.__name__
            method_proxy.name = _name
            method_proxy.__name__ = _name
            method_proxy.usage = \
                usage if usage is not None else ""
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

    def lookup(self, name):
        try:
            return self._commands[name]
        except KeyError:
            raise CommandNotFound("No such command: {}".format(name))

    @property
    def commands(self):
        return self._commands.iteritems()

    @property
    def command_names(self):
        return self._commands.keys()

    @property
    def parser(self):
        return self._parser

    def _parse_args(self):
        self._opts, self._args = self._parser.parse_args()

    @property
    def opts(self):
        if self._opts is None:
            self._parse_args()
        return self._opts

    @property
    def args(self):
        if self._args is None:
            self._parse_args()
        return self._args

    def run(self):
        """Start the application"""

        if len(self.args) == 0 and self.auto_interactive:
            return self.run_interactive()
        return self._run_once(self.args)

    def _run_once(self, args):
        try:
            return self._run(args)
        except ShowCommandsHelp, e:
            if e.message:
                print(e.message)
            self._print_commands_help()
        except CommandError, e:
            print(e.message)
            return 1
        except:
            traceback.print_exc()
            return 127

    def _run(self, args):
        ## Parse command-line options
        if len(args) == 0:
            raise InvalidUsage(
                "A command is required. See ``help`` for more help.")

        if self.opts.X_help_commands:
            raise ShowCommandsHelp

        command_name, command_args = args[0], args[1:]
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
            app=self,
            global_options=self.opts,
            command=command_name,
            options=cmd_opts,
            arguments=cmd_args)

        return command(state)

    def _print_commands_help(self, args=None):
        if args is None or len(args) == 0:
            print("Accepted commands:\n")
            for name, command in self.commands:
                self._print_command_usage(command)
                print("")
        else:
            name = args[0]
            command = self.lookup(name)
            self._print_command_usage(command)

    def _print_command_usage(self, command):
        usage = getattr(command, 'usage', None) or ""

        if self.use_colors:
            usage_fmt = "\033[1m{name}\033[0m {usage}"
            usage = re.sub(r"<([^>]*)>", "\033[4;36m\\1\033[0m", usage)
        else:
            usage_fmt = "{name} {usage}"

        cmd_usage = usage_fmt.format(name=command.name, usage=usage)
        print(cmd_usage)
        if hasattr(command, 'help_text') and command.help_text:
            print(_indent(command.help_text, ' ' * 8))

    ##==========================================================================
    ## Interactive mode
    ##==========================================================================

    def custom_completer(self, new_completer):
        class CustomCompleter(object):
            def __enter__(self):
                self.old_completer = readline.get_completer()
                readline.set_completer(new_completer)

            def __exit__(self, exc_type, exc_val, exc_tb):
                readline.set_completer(self.old_completer)
        return CustomCompleter()

    def run_interactive(self):
        with self.custom_completer(self.complete):
            readline.parse_and_bind(self.complete_key + ": complete")
            while True:
                try:
                    result = self._run_interactive_once()
                    if result is False:
                        break

                except KeyboardInterrupt:
                    print "^C"

                except:
                    traceback.print_exc()

    def _run_interactive_once(self):
        try:
            line = raw_input(self.prompt)
            line = line.strip()
        except EOFError:
            print "EOF"
            return False
        if line:
            parsed = self._parse_line(line)
            if len(parsed) and parsed[0] in ('exit', 'quit'):
                return False
            self._run_once(parsed)
        return True

    def complete(self, text, state):
        """Return the next possible completion for 'text'.

        If a command has not been entered, then complete against command list.
        Otherwise try to call complete_<command> to get list of completions.
        """
        ## todo: improve this thing to, eg, complete in the middle of a token
        if state == 0:
            origline = readline.get_line_buffer()
            line = origline.lstrip()
            stripped = len(origline) - len(line)
            begidx = readline.get_begidx() - stripped
            endidx = readline.get_endidx() - stripped

            compfunc = self.complete_default
            if begidx > 0:
                parts = self._parse_line(line)
                if len(parts) > 0:
                    command = self.lookup(parts[0])
                    _compfunc = getattr(self, command.complete)
                    if _compfunc is not None and callable(_compfunc):
                        compfunc = _compfunc
            else:
                compfunc = self.complete_names
            self.completion_matches = compfunc(text, line, begidx, endidx)

        try:
            return self.completion_matches[state]
        except IndexError:
            return None

    def complete_default(self, *ignored):
        return []

    def complete_names(self, text, *ignored):
        commands = self._commands.keys()
        return [a for a in commands if a.startswith(text)]

    def _parse_line(self, line):
        import shlex
        return shlex.split(line)


class State(object):
    """
    Used to keep state of the current invocation.
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
    pass


class CommandNotFound(CommandError):
    pass
