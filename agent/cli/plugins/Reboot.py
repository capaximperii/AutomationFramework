from cli.core.Console import Console
from cli.core.docopt import docopt
from cli.core.ExecHelper import ExecHelper
import os

class Cli(Console):
    def __init__(self):
        Console.__init__(self)
        self.doc = """
        Usage:
            Reboot <sudopassword>
            Reboot (-h | --help | --version)

        Options:
            -h, --help  Show this screen.
        """

    def do_Reboot(self, args):
        command = docopt(str(self.doc), args)
        e = ExecHelper()
        e.reset("Reboot")
        e.setExecCodes("Reboot","Unknown error", "Fail")
        prepare = 'echo %s|sudo -S shutdown -k +1' %(command['<sudopassword>'])
        e.Log("Checking our permissions")
        e.Log(prepare)
        if e.Execute(prepare) == 0:
            cmd = 'shutdown -r +1 &'
            e.Log(cmd)
            e.Log("Alert: This will wipe out all the variables created before.")
            p = e.Execute('echo %s|sudo -S %s' % (command['<sudopassword>'], cmd))
            e.setExecCodes("Reboot","Going down in 1 minute", "Reboot")

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
