from cli.core.Console import Console
from cli.core.docopt import docopt
from cli.core.ExecHelper import ExecHelper
import sys

class Cli(Console):
    def __init__(self):
        Console.__init__(self)
        self.doc = """
        Usage:
            Skip <fromrank> <torank>
            Skip (-h | --help | --version)

        Options:
            -h, --help  Show this screen.
        """

    def do_Skip(self, args):
        command = docopt(str(self.doc), args)
        e = ExecHelper()
        e.reset("Skip")
        e.Log("Skip command executing")
        outstring = ("Skip", command['<fromrank>'], command['<torank>'], "null")
        e.setExecCodes(args, outstring, "Skip")

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
