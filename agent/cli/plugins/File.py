from cli.core.Console import Console
from cli.core.docopt import docopt
from cli.core.ExecHelper import ExecHelper
from thirdparty.inotify import pyinotify
import sys
import os

watchpath = None

class Cli(Console):
    def __init__(self):
        Console.__init__(self)
        self.doc = """
        Usage:
            File contains <path> <expectation>
            File exists <path>
            File delete <path>
            File create <path>
            File purge <path>
            File wait create <path>
            File wait delete <path>
            File wait write  <path>
            File wait open <path>
            File wait move <path>
            File wait access <path>

            File (-h | --help | --version)

        Options:
            -h, --help  Show this screen.
        """

    def do_File(self, args):
        command = docopt(str(self.doc), args)
        e = ExecHelper()
        e.reset("File")
        path = command['<path>']
        if command['wait']:
            print args
            wm = pyinotify.WatchManager()
            if command['delete']:
                mask = pyinotify.IN_DELETE
            elif command['create']:
                if os.path.exists(path):
                    e.Log("File already exists, do not have to wait.")
                    e.setExecCodes(args, "already exists", "Pass")
                    return
                else:
                    global watchpath
                    watchpath = path
                    path = os.path.dirname(path)
                mask = pyinotify.IN_CREATE
            elif command['write']:
                mask = pyinotify.IN_CLOSE_WRITE | pyinotify.IN_CLOSE_NOWRITE
            elif command['open']:
                mask = pyinotify.IN_OPEN
            elif command['move']:
                mask = pyinotify.IN_MOVED_FROM | pyinotify.IN_MOVED_TO | pyinotify.IN_MOVED_SELF
            elif command['access']:
                mask = pyinotify.IN_ACCESS
            #mask = mask | pyinotify.IN_ONESHOT
            e.Log("Starting inotify to watch file for event")
            handler = EventHandler()
            notifier = pyinotify.Notifier(wm, handler)
            wdd = wm.add_watch(path, mask, rec=True)
            notifier.loop()
        elif command["contains"]:
            e.OutputContains("/bin/cat " + path, command['<expectation>'])
        elif command['exists']:
            if os.path.exists(path):
                e.Log("file exists")
                e.setExecCodes("File exists", "exists", "Pass")
            else:
                e.Log("file does not exist")
                e.setExecCodes("File exists", "Doesnt exist", "Fail")

        elif command['delete']:
            if os.path.exists(path):
                os.unlink(path)
        elif command['create'] or command['purge']:
            f = open(path, "w")
            f.close()
        print e.r.retVal

    def do_help(self, arg):
        print self.doc



class EventHandler(pyinotify.ProcessEvent):
    def process_IN_CREATE(self, event):
        e = ExecHelper()
        # filter out others that are created in the same directory
        if watchpath == event.pathname:
            e.setExecCodes("File wait create", event.pathname , "Pass")
            raise KeyboardInterrupt

    def process_default(self, event):
        e = ExecHelper()
        e.setExecCodes("File wait", event.pathname , "Pass")
        raise KeyboardInterrupt

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
