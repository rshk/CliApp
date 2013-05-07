from cliapp import CliApp

app = CliApp()
app.parser.add_option('--debug', dest='debug', action='store_true',
    default='False', help='Enable debugging')

@app.command(usage="[<name>]", help_text="Greets somebody or the whole world")
def hello(state):
    if len(state.arguments) > 0:
        print "Hello, {0}".format(state.arguments[0])
    else:
        print "Hello, world!"

@app.command
def hello_world(state):
    """
    Prints the phrase "Hello, world!"
    """
    print "Hello, world!"


if __name__ == '__main__':
    app.run()
