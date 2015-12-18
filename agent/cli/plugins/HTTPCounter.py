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
            HTTPCounter initialize <sudopassword>
            HTTPCounter resetCounter <sudopassword>
            HTTPCounter getCount <sudopassword>            
            HTTPCounter (-h | --help | --version)

        Options:
            -h, --help  Show this screen.
        """

    def initialize(self, sudopassword):
        cmds = ["sudo -S iptables -F AF", "sudo iptables -F OUTPUT", "sudo iptables -X AF",
                "sudo -S iptables -N AF", 
                "sudo -S iptables -A AF -p tcp --dport 80 -m string --string 'GET /' --algo bm -j ACCEPT",
                "sudo -S iptables -A AF -p tcp --dport 80 -m string --string 'POST /' --algo bm -j ACCEPT",
                "sudo -S iptables -A AF -p tcp --dport 80 -m string --string 'PUT /' --algo bm -j ACCEPT",
                "sudo -S iptables -A OUTPUT -o lo -j AF" ]
        e = ExecHelper()
        for c in cmds:
            cmd = "echo %s|%s" % (sudopassword, c)
            e.Execute(cmd)

    def do_HTTPCounter(self, args):
        command = docopt(str(self.doc), args)
        e = ExecHelper()
        e.reset("HTTPCounter")
        sudopassword = command['<sudopassword>']
        if command["initialize"]:
            e.Log("HTTPCounter initalizing")
            self.initialize(sudopassword)
            e.setExecCodes(args, "Warning: Does not verify execution", "Pass")
        elif command["resetCounter"]:
            cmd = "echo %s|sudo -S iptables -Z AF" % (sudopassword)
            e.Log("HTTPCounter resetCounter")
            e.Execute(cmd)
            e.setExecCodes(args,"Warning: Does not verify execution","Pass")
        elif command["getCount"]:
            cmd = "sh -c 'echo %s|sudo -S iptables -vL AF'" % (sudopassword)
            lines = e.RetOutput(cmd).split(os.linesep)
            output =  " GET  " + lines[2].split()[0]
            output += " POST " +  lines[3].split()[0]
            output += " PUT " + lines[4].split()[0]
            e.r.setOutput(output)
            print output

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
