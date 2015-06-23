from cli.core.Console import Console
from cli.core.docopt import docopt
from cli.core.ExecHelper import ExecHelper
import sys

class Cli(Console):
    def __init__(self):
        Console.__init__(self)
        self.doc = """
        Usage:
            Network on
            Network off
            Network restart
            Network (-h | --help | --version)

        Options:
            -h, --help  Show this screen.
        """

    def do_Network(self, args):
        command = docopt(str(self.doc), args)
        e = ExecHelper()
        e.reset("Network")
        if (command["on"] == True):
            e.EvalRetVal("service network start")
        elif(command["off"] == True):
            e.EvalRetVal("service network stop")
        elif(command["restart"] == True):
            e.EvalRetVal("service network stop")
            e.EvalRetVal("service network start")
        e.Log(e.r.getOutput())

    def do_help(self, arg):
        print self.doc

def setup():
    prompt = Cli()
    p = __name__.split('.')
    prompt.prompt = p[len(p) - 1] + " > "
    return prompt

def main():
    prompt = setup()
    prompt.cmdloop('Starting cli...')

if __name__ == '__main__':
    main()
