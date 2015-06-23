from cli.core.Console import Console
from cli.core.docopt import docopt
from cli.core.ExecHelper import ExecHelper
import sys


class Cli(Console):
    def __init__(self):
        Console.__init__(self)
        self.doc = """
        Usage:
            Mcast server <filepath>
            Mcast client
            Mcast (-h | --help | --version)

        Options:
            -h, --help  Show this screen.
        """

    def do_Mcast(self, args):
        command = docopt(str(self.doc), args)
        e = ExecHelper()
        e.reset("Mcast")
        if command['server']:
            cmd = "python /tmp/mcastfirmware/server.py %s" %(command['<filepath>'])
            e.Spawn(cmd)
        elif command['client']:
            cmd = "python /tmp/mcastfirmware/client.py"
            e.Execute(cmd)
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
