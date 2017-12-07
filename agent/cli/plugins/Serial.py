from cli.core.Console import Console
from cli.core.docopt import docopt
from cli.core.ExecHelper import ExecHelper
import sys

from serial import Serial
from serial import STOPBITS_ONE, EIGHTBITS, PARITY_NONE
from xmodem import XMODEM

class Cli(Console):
    def __init__(self):
        Console.__init__(self)
        self.doc = """
        Usage:
            Serial command <device> <cmdline> <wait>
            Serial sendfile <device> <cmdline> <path> <wait>
            Serial (-h | --help | --version)

        Options:
            -h, --help  Show this screen.
        """
    def getc(self, size, timeout=1):
        return self.ser.read(size) or None

    def putc(self, data, timeout=1):
        return self.ser.write(data)

    def do_Serial(self, args):
        """
        """
        command = docopt(str(self.doc), args)
        e = ExecHelper()
        e.reset("Serial")
        if command['command']:
            with Serial(port=command['<device>'], baudrate=115200,
                        stopbits=STOPBITS_ONE, bytesize=EIGHTBITS,
                        parity=PARITY_NONE, dsrdtr=True, rtscts=True) as self.ser:
                for c in command['<cmdline>']:
                    self.ser.write(c)
                self.ser.write(b'\r\n')
                while True:
                    buf = self.ser.read()
                    sys.stdout.write(buf.decode('utf-8'))
                    sys.stdout.flush()
                    if command['<wait>'] in buf:
                        break
        elif command['sendfile']:
            with Serial(port=command['<device>'], baudrate=115200,
                        stopbits=STOPBITS_ONE, bytesize=EIGHTBITS,
                        parity=PARITY_NONE, dsrdtr=True, rtscts=True) as self.ser:
                for c in command['<cmdline>']:
                    self.ser.write(c)
                self.ser.write(b'\r\n')
                modem = XMODEM(self.getc, self.putc)
                stream = open(command['<path>'], 'rb')
                modem.send(stream)
                while True:
                    buf = self.ser.read()
                    sys.stdout.write(buf.decode('utf-8'))
                    sys.stdout.flush()
                    if command['<wait>'] in buf:
                        break

        e.Log(e.r.getOutput())

    def do_help(self, arg):
        """
        """
        print(self.doc)

def setup():
    """
    """
    prompt = Cli()
    p = __name__.split('.')
    prompt.prompt = p[len(p) - 1] + " > "
    return prompt

def main():
    """
    """
    prompt = setup()
    prompt.cmdloop('Starting cli...')

if __name__ == '__main__':
    main()
