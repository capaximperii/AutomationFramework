from cli.core.Console import Console
from cli.core.docopt import docopt
from cli.core.ExecHelper import ExecHelper
from thirdparty.screenshot.mss import MSSLinux
import sys
import os
import shutil


class Cli(Console):
    def __init__(self):
        Console.__init__(self)
        self.doc = """
        Usage:
            Desktop logout
            Desktop resolution <resolution>
            Desktop screenshot <filename>
            Desktop legacyScreenshot <filename>
            Desktop windowid <process>
            Desktop windowfocus <windowid>
            Desktop windowclose <windowid>
            Desktop windowimg <filename> <windowid>
            Desktop keydown <key>
            Desktop keyup <key>
            Desktop keypress <key>
            Desktop type KEYS...
            Desktop mouseclick <windowid> <windowimg> PATTERN...
            Desktop (-h | --help | --version)

        Options:
            -h, --help  Show this screen.
        """

    def do_Desktop(self, args):
        command = docopt(str(self.doc), args)
        e = ExecHelper()
        e.reset("Desktop")
        if command["logout"]:
            e.EvalRetVal("/usr/bin/gnome-session-quit --no-prompt")
        elif command["resolution"]:
            cmd = "xrandr -d :0 --output LVDS --mode " + command["<resolution>"]
            e.Log("Desktop Resolution: " + cmd)
            e.EvalRetVal(cmd)
        elif command["screenshot"]:
            scrot = MSSLinux()
            for filename in scrot.save(output="scrot.png", screen=-1):
                shutil.move("scrot.png", command['<filename>'])
                e.Log('File: "{}" created.'.format(filename))
        elif command["legacyScreenshot"]:
        	os.system("gnome-screenshot -b -f " + command['<filename>'])
        elif command["windowimg"]:
            e.Log("Executing commands for windowimg")
            cmd = 'xte "mousemove 0 0"'
            e.Log(cmd)
            e.Execute(cmd)
            cmd = "./agent/cli/bin/windowimg.sh %s %s" % (command['<filename>'], command['<windowid>'])
            e.Log(cmd)
            e.EvalRetVal(cmd)
        elif command["windowid"]:
            e.Log("Executing commands for windowid")
            cmd = "./agent/cli/bin/windowid.sh %s" %(command['<process>'] )
            e.Log(cmd)
            e.EvalRetVal(cmd)
        elif command["windowfocus"]:
            e.Log("Executing commands for windowfocus")
            cmd = 'xdotool windowactivate %s' % (command['<windowid>'])
            e.Log(cmd)
            e.EvalRetVal(cmd)
        elif command["windowclose"]:
            cmd = 'wmctrl -i -c %s' % (command['<windowid>'])
            e.Log("Executing windowclose: " + cmd)
            e.EvalRetVal(cmd)
        elif command["keydown"]:
            cmd = "xte keydown %s" %(command['<key>'])
            e.Log(cmd);
            e.EvalRetVal(cmd)
        elif command["keyup"]:
            cmd = "xte keyup %s" %(command['<key>'])
            e.Log(cmd)
            e.EvalRetVal(cmd)
        elif command["keypress"]:
            cmd = 'xte "sleep 1" "key %s"' %(command['<key>'])
            e.Log(cmd)
            e.EvalRetVal(cmd)
        elif command["type"]:
            e.Log("Desktop Typing keys")
            special = ["Alt", "Control", "Shift", "Super"]
            press = []
            release = []
            l = 0
            for k in command['KEYS']:
                if k in special:
                    press.append('"keydown ' + k + '_R"')
                    release.append('"keyup ' + k + '_R"')
                elif len(release) > 0:
                    press.append('"key ' + k + '"')
                    release.reverse()
                    press.extend(release)
                    release = []
                else:
                    for char in k:
                        press.append('"usleep 30000" "str ' + char + '"')
                    #press.append('"str ' + k + '"')
                cmd = "xte " + ' '.join(press)
            e.EvalRetVal(cmd)
        elif command["mouseclick"]:
            e.Log("Desktop mouseclick")
            cmd = "./agent/cli/bin/mouseclick.sh %s %s %s" % (command['<windowid>'],
                    command['<windowimg>'],
                    ' '.join(command['PATTERN']))
            e.Log(cmd)
            e.EvalRetVal(cmd)
            #move the mouse out before it pollutes next screenshot
            e.Execute('xte "sleep 1" "mousemove 0 0"')

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
