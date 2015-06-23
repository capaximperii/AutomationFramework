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
            Depends <ipaddr> <rank>
            Depends (-h | --help | --version)

        Options:
            -h, --help  Show this screen.
        """

    def do_Depends(self, args):
        command = docopt(str(self.doc), args)
        e = ExecHelper()
        e.reset("Depends")
        depstring = (command['<ipaddr>'], command['<rank>'])
        e.Log("Waiting for 30 secs for %s to finish test case whose rank is %s" % (command['<ipaddr>'], command['<rank>']))
        print "Waiting for 30 secs for %s to finish test case whose rank is %s" % (command['<ipaddr>'], command['<rank>'])
        time.sleep(30)
        e.setExecCodes(args, depstring, "Wait")

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
