from cli.core.Console import Console
from cli.core.docopt import docopt
from cli.core.ExecHelper import ExecHelper
import sys

class Cli(Console):
    def __init__(self):
        Console.__init__(self)
        self.doc = """
        Usage:
            SimulateDomain Logon <user> <password> <domain>
            SimulateDomain Logoff
            SimulateDomain (-h | --help | --version)

        Options:
            -h, --help  Show this screen.
        """

    def do_SimulateDomain(self, args):
        command = docopt(str(self.doc), args)
        e = ExecHelper()
        e.reset("SimulateDomain")
        if (command["Logon"] == True):
            print "regset --temp System Username " + command['<user>']
            print "regset --temp System Domain " + command['<domain>']
            print "regset --temp --encrypt System Password " + command['<password>']
        elif(command["Logoff"] == True):
            print "regdel --temp System Username "
            print "regdel --temp System Domain "
            print "regdel --temp System Password "

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
