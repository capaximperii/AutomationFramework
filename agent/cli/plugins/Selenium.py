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
            Selenium start        <which>
            Selenium stop
            Selenium clickname    <which>
            Selenium clickcss     <which>
            Selenium clickid      <which>
            Selenium clearxpath   <which>
            Selenium clearname    <which>
            Selenium clearcss     <which>
            Selenium clearid      <which>
            Selenium clickxpath   <which>
            Selenium open         <which>
            Selenium fillname     <which> WHAT...
            Selenium fillcss      <which> WHAT...
            Selenium fillid       <which> WHAT...
            Selenium fillxpath    <which> WHAT...
            Selenium counttags    <which> WHAT...
            Selenium (-h | --help | --version)

        Options:
            -h, --help  Show this screen.
        """

    def SendWorkerCommand(self, cmd):
        with open(os.path.join("/tmp", 'rselenium'), "w") as writer:
            writer.write(cmd)

    def ReadWorkerResult(self):
        retval = "Empty"
        output = "Empty"
        with open(os.path.join("/tmp", 'wselenium'), "r") as reader:
            line = reader.readline().split(' ', 1)
            retval = line[0]
            output = line[1]
        return retval, output

    def do_Selenium(self, args):
        command = docopt(str(self.doc), args)
        e = ExecHelper()
        e.reset("Selenium")
        if command["start"]:
            e.Spawn("python ./agent/cli/bin/SeleniumWorker.py %s" % (command['<which>']) )
            time.sleep(5)
            retval, output = self.ReadWorkerResult()
        elif command["stop"]:
            self.SendWorkerCommand("stop")
            retval, output = self.ReadWorkerResult()
        elif command["clickcss"]:
            self.SendWorkerCommand("clickcss " + command['<which>'] + "")
            retval, output = self.ReadWorkerResult()
        elif command["clickname"]:
            self.SendWorkerCommand("clickname " + command['<which>'] + "")
            retval, output = self.ReadWorkerResult()
        elif command["clickid"]:
            self.SendWorkerCommand("clickid " + command['<which>'] + "")
            retval, output = self.ReadWorkerResult()
        elif command["clickxpath"]:
            self.SendWorkerCommand("clickxpath " + command['<which>'] + "")
            retval, output = self.ReadWorkerResult()
        elif command["clearcss"]:
            self.SendWorkerCommand("clearcss " + command['<which>'] + "")
            retval, output = self.ReadWorkerResult()
        elif command["clearname"]:
            self.SendWorkerCommand("clearname " + command['<which>'] + "")
            retval, output = self.ReadWorkerResult()
        elif command["clearid"]:
            self.SendWorkerCommand("clearid " + command['<which>'] + "")
            retval, output = self.ReadWorkerResult()
        elif command["clearxpath"]:
            self.SendWorkerCommand("clearxpath " + command['<which>'] + "")
            retval, output = self.ReadWorkerResult()
        elif command["open"]:
            self.SendWorkerCommand("open " + command['<which>'] + "")
            retval, output = self.ReadWorkerResult()
        elif command["fillcss"]:
            self.SendWorkerCommand("fillcss " + command['<which>'] + " " + ' '.join(command['WHAT']) + "")
            retval, output = self.ReadWorkerResult()
        elif command["fillname"]:
            self.SendWorkerCommand("fillname " + command['<which>'] + " " + ' '.join(command['WHAT']) + "")
            retval, output = self.ReadWorkerResult()
        elif command["fillid"]:
            self.SendWorkerCommand("fillid " + command['<which>'] + " " + ' '.join(command['WHAT']) + "")
            retval, output = self.ReadWorkerResult()
        elif command["fillxpath"]:
            self.SendWorkerCommand("fillxpath " + command['<which>'] + " " + ' '.join(command['WHAT']) + "")
            retval, output = self.ReadWorkerResult()
        elif command["counttags"]:
            self.SendWorkerCommand("counttags " + command['<which>'] + " " + ' '.join(command['WHAT']) + "")
            retval, output = self.ReadWorkerResult()
        else:
            retval, output = "Fail", "Invalid command"
        
        e.Log(output)
        e.setExecCodes(args, output, retval)


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
