from cli.core.Console import Console
from cli.core.docopt import docopt
from cli.core.ExecHelper import ExecHelper
import sys
import ftplib
import os

class Cli(Console):
    def __init__(self):
        Console.__init__(self)
        self.doc = """
        Usage:
            Ftp upload <server-ip> <user> <password> <localfile> <remotefile>
            Ftp download <server-ip> <user> <password> <localfile> <remotefile>
            Ftp (-h | --help | --version)

        Options:
            -h, --help  Show this screen.
        """

    def do_Ftp(self, args):
        command = docopt(str(self.doc), args)
        e = ExecHelper()
        e.reset("Ftp")
        try:
            ftpconn = ftplib.FTP(command['<server-ip>'])
            ftpconn.login(command['<user>'],  command['<password>'])
            ftpconn.cwd(os.path.dirname(command['<remotefile>']))

            if command['upload']:
                localfile = open(command['<localfile>'], 'r')
                ftpconn.storlines('STOR ' + command['<remotefile>'], localfile)
                localfile.close()
                ftpconn.quit()
                e.setExecCodes("", "File uploaded", "Pass")
            elif command['download']:
                ftpconn.retrbinary("RETR " + os.path.basename(command['<remotefile>']),
                            open(command['<localfile>'], 'wb').write)
                e.setExecCodes("", "File downloaded", "Pass")
            e.Log("Ftp command passed")
        except Exception as e:
            print str(e)
            e.Log("Ftp failed " + str(e))
            e.setExecCodes("", str(e), "Fail")

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
