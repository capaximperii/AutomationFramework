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
            Gdm login <sudopassword> PHRASE...
            Gdm (-h | --help | --version)

        Options:
            -h, --help  Show this screen.
            PHRASE      Contains words to type, you can use special keys between words:
                        {Tab}       Presses the tab key, changing the widget in focus.
                        {Return}    Presses the return key potentially trigger an action.
                        {Clear}     Presses Ctrl+A Delete clearing contents of a widget.
                        {Space}     Presses the space bar.
        """

    def do_Gdm(self, args):
        command = docopt(str(self.doc), args)
        e = ExecHelper()
        e.reset("Gdm")
        cmd = "pidof X"
        pid = e.RetOutput(cmd).strip()
        cmd = "sh -c 'xargs -0 < /proc/" + pid + "/cmdline'"
        e.Log(cmd)
        xcmdline = e.RetOutput(cmd).split()
        count = len(xcmdline)
        i = 0
        while i < count:
            if xcmdline[i] == "-auth":
                xauthority = xcmdline[i + 1]
            i += 1
        os.environ['XAUTHORITY'] = xauthority
        for word in command['PHRASE']:
            word = word.strip()
            if word == "{Tab}":
                cmd = 'echo %s|sudo -S xdotool key Tab' %(command['<sudopassword>'])
            elif word == "{Return}":
                cmd = 'echo %s|sudo -S xdotool key Return' %(command['<sudopassword>'])
            elif word == "{Clear}":
                cmd = 'echo %s|sudo -S xdotool key ctrl+a Delete' %(command['<sudopassword>'])
            elif word == "{Space}":
                cmd = 'echo %s|sudo -S xdotool key space' %(command['<sudopassword>'])
            else:
                cmd = 'echo %s|sudo -S xdotool type %s' %(command['<sudopassword>'], word)
            e.Log(cmd)
            e.Execute(cmd)
            time.sleep(2)
            e.Log(e.r.output)

        #print e.r.output

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
