from cli.core.Console import Console
from cli.core.docopt import docopt
from cli.core.ExecHelper import ExecHelper
import sys

class Cli(Console):
    def __init__(self):
            Console.__init__(self)
            self.doc = """
                Usage:
                        Dot1x tls <cacert> <clientcert> <privkey> <pkeypass> <authmode>
                        Dot1x peap <cacert> <authmode>
                        Dot1x reset
                        Dot1x (-h | --help | --version)

                Options:
                        -h, --help  Show this screen.
                """

    def do_Dot1x(self, args):
        command = docopt(str(self.doc), args)
        e = ExecHelper()
        e.reset("Dot1x")
        e.EvalRetVal("regset --temp Network-eth0 Enable802 yes")
        e.EvalRetVal("regset Network-eth0 ca_cert " + command['<cacert>'])
        if (command["tls"] == True):
            e.Log("Configuring for tls")
            e.EvalRetVal("regset Network-eth0 Authentication TLS")
            e.EvalRetVal("regset Network-eth0 client_cert " + command['<clientcert>'])
            e.EvalRetVal("regset Network-eth0 private_key " + command['<privkey>'])
            e.EvalRetVal("regset Network-eth0 private_key_password " + command['<pkeypass>'])
            e.EvalRetVal("regset Network-eth0 Authmode " + command['<authmode>'])
        elif(command["peap"] == True):
            e.Log("Configuring for PEAP")
            e.EvalRetVal("regset Network-eth0 Authentication PEAP")
            e.EvalRetVal("regset Network-eth0 Authmode " + command['<authmode>'])
        elif(command["reset"] == True):
            e.Log("Doing dot1x reset")
            e.EvalRetVal("regdel Network-eth0 Authmode")
            e.EvalRetVal("regdel Network-eth0 Authentication")
            e.EvalRetVal("regdel Network-eth0 Enable802")
            e.EvalRetVal("regdel Network-eth0 ca_cert")
            e.EvalRetVal("regdel Network-eth0 client_cert")
            e.EvalRetVal("regdel Network-eth0 private_key")
            e.EvalRetVal("regdel Network-eth0 private_key_password")

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
