from cli.core.Console import Console
from cli.core.docopt import docopt
from cli.core.ExecHelper import ExecHelper
import sys
import socket
import struct
import fcntl

class Cli(Console):
    def __init__(self):
        Console.__init__(self)
        self.doc = """
        Usage:
            IP equals <interface> <address>
            IP contains <interface> <address>
            IP (-h | --help | --version)

        Options:
            -h, --help  Show this screen.
        """
    def myIP(self, interface):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sockfd = sock.fileno()
        SIOCGIFADDR = 0x8915
        ifreq = struct.pack('16sH14s', interface, socket.AF_INET, '\x00'*14)
        try:
            res = fcntl.ioctl(sockfd, SIOCGIFADDR, ifreq)
        except Exception as e:
            print str(e)
            return "127.0.0.1"
        ip = struct.unpack('16sH2x4s8x', res)[2]
        return socket.inet_ntoa(ip)

    def do_IP(self, args):
        command = docopt(str(self.doc), args)
        e = ExecHelper()
        e.reset("IP")
        interface = command["<interface>"]

        myIp = self.myIP(interface)
        e.Log("Found client ip: " + myIp)
        if command["equals"]:
            if command["<address>"] == myIp:
                e.Log("ip addresss equal")
                e.setExecCodes("", "ip addresses equal", "Pass")
                retVal = "Pass"
            else:
                e.Log("IP address not equal")
                e.setExecCodes("", "ip addresses inequal", "Fail")
                retVal = "Fail"
        elif command["contains"]:
            if myIp.startswith(command["<address>"]):
                e.Log("ip addresses contains")
                e.setExecCodes("", "ip addresses contains", "Pass")
                retVal = "Pass"
            else:
                e.Log("ip addresses does not contain")
                e.setExecCodes("", "ip addresses does not contain", "Fail")
                retVal = "Fail"
        print retVal

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
