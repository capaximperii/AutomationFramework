from cli.core.Console import Console
from cli.core.docopt import docopt
from cli.core.ExecHelper import ExecHelper
import sys
import time

class Cli(Console):
    def __init__(self):
        Console.__init__(self)
        self.doc = """
        Usage:
            Sleep <sec>
            Sleep (-h | --help | --version)

        Options:
            -h, --help  Show this screen.
        """

    def do_Sleep(self, args):
        command = docopt(str(self.doc), args)
        e = ExecHelper()
        e.reset("Sleep")
        e.Log("Sleep executing")
        time.sleep(int(command['<sec>']))
        e.setExecCodes(args, "Lion sleeps 20 h per day", "Pass")

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
