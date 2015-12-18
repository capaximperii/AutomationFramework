from cli.core.Console import Console
from cli.core.docopt import docopt
from cli.core.ExecHelper import ExecHelper
import sys


class Cli(Console):
    def __init__(self):
        Console.__init__(self)
        self.doc = """
        Usage:
            Math add <one> with <two>
            Math subtract <one> from <two>
            Math multiply <one> and <two>
            Math divide <one> by <two>
            Math (-h | --help | --version)

        Options:
            -h, --help  Show this screen.
        """

    def do_Math(self, args):
        command = docopt(str(self.doc), args)
        e = ExecHelper()
        e.reset("Math")
        e.Log(args)
        if command["add"]:
            result = int(command['<one>']) + int(command['<two>'])
        elif command["subtract"]:
            result = int(command['<two>']) - int(command['<one>'])
        elif command["multiply"]:
            result = int(command['<one>']) * int(command['<two>'])
        elif command["divide"]:
            result = int(command['<one>']) / int(command['<two>'])
        print result
        e.setExecCodes(command, result, "Pass")

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
