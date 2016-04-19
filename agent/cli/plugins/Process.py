from __future__ import division
from cli.core.Console import Console
from cli.core.docopt import docopt
from cli.core.ExecHelper import ExecHelper
import sys
import time
import os

class Cli(Console):
    def __init__(self):
        Console.__init__(self)
        self.doc = """
        Usage:
            Process monitor <name> <duration>
            Process spawn PATH...
            Process exec PATH...
            Process forfeit PATH...
            Process thrive PATH...
            Process kill <name>
            Process alive <name>
            Process dead <name>
            Process pid <name>
            Process output contains <expectation> PATH...
            Process (-h | --help | --version)

        Options:
            -h, --help  Show this screen.
            forfeit execs a process and always returns pass
        """

    def parse(self, output):
        instances = output.split("\n")
        pcpu = float(0)
        pmem = float(0)
        for i in instances:
            if len(i.strip())>0:
                pcpu += float(i.strip().split(" ")[0])
                pmem += float(i.strip().split(" ")[2])
        return pcpu,pmem

    def do_Process(self, args):
        command = docopt(str(self.doc), args)
        e = ExecHelper()
        e.reset("Process")
        if command["monitor"]:
            psopts = "/bin/ps -C %s o pcpu,pmem --cumulative --no-heading" %(command["<name>"])
            e.Log("Executing monitor " + psopts)
            counter = 0
            cpu = float(0)
            mem = float(0)
            while (counter < int(command["<duration>"])):
                pcpu,pmem = self.parse(e.RetOutput(psopts))
                cpu = cpu + pcpu
                mem = mem + pmem
                time.sleep(1)
                counter = counter + 1
            output = "%s consumed %s%% cpu and %s %% memory" % (command["<name>"],cpu/counter,mem/counter)
            e.Log(output)
            print output
            if cpu > 0 or mem > 0:
                e.setExecCodes("Process monitor",output,"Pass")
            else:
                e.setExecCodes("Process monitor",output,"Fail")
        elif command["kill"]:
            killopts = "/usr/bin/killall %s" %(command["<name>"])
            e.Log(killopts)
            e.EvalRetVal(killopts)
        elif command["spawn"]:
            spawnopts = ' '.join(command["PATH"])
            e.Log(spawnopts)
            e.Spawn(spawnopts)
        elif command["exec"]:
            execopts = ' '.join(command["PATH"])
            e.Log(execopts)
            execopts = "/bin/sh -c '%s' " %(execopts)
            e.EvalRetVal(execopts)
        elif command["forfeit"]:
            execopts = ' '.join(command["PATH"])
            e.Log(execopts)
            execopts = "/bin/sh -c '%s' " %(execopts)
            e.EvalRetVal(execopts)
            e.r.setRetVal("Fail")
        elif command["thrive"]:
            execopts = ' '.join(command["PATH"])
            e.Log(execopts)
            execopts = "/bin/sh -c '%s' " %(execopts)
            e.EvalRetVal(execopts)
            e.r.setRetVal("Pass")
        elif command["alive"]:
            killopts = "/usr/bin/killall -s 0 %s" %(command["<name>"])
            e.Log(killopts)
            e.EvalRetVal(killopts)
        elif command["dead"]:
            killopts = "pidof %s" %(command["<name>"])
            e.Log(killopts)
            e.EvalRetVal(killopts, 1)
        elif command["pid"]:
            execopts = "pidof %s" %(command["<name>"])
            e.Log(execopts)
            e.EvalRetVal(execopts)
        elif command["output"]:
            #  Process output contains 1360x78  xdpyinfo  | grep dimensions
            execopts = ' '.join(command["PATH"])
            e.Log(execopts)
            execopts = "/bin/sh -c '%s' " %(execopts)
            output = e.RetOutput(execopts)
            if command['<expectation>'] in output:
                e.setExecCodes(execopts, output, "Pass")
            else:
                e.setExecCodes(execopts, output, "Fail")
        e.Log(e.r.getOutput())
        print e.r.getRetVal()

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
