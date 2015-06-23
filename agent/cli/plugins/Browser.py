from cli.core.Console import Console
from cli.core.docopt import docopt
from cli.core.ExecHelper import ExecHelper
import sys
import os
import time

class Cli(Console):
    def __init__(self):
        Console.__init__(self)
        self.doc = """
        Usage:
            Browser clearHistory
            Browser kiosk <url>
            Browser (-h | --help | --version)

        Options:
            -h, --help  Show this screen.
        """

    def do_Browser(self, args):
        command = docopt(str(self.doc), args)
        e = ExecHelper()
        e.reset("Browser")
        if command["clearHistory"]:
            e.Log("Browser clearHistory command is not implemented, marking Pass")
            e.setExecCodes(args, "Not implemented", "Pass")
        elif command["kiosk"]:
            e.Log("Browser kiosk command is not implemented, marking Pass")
            e.setExecCodes("Browser kiosk","Not implemented","Pass")

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
