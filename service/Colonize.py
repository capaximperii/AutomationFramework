import os
import time
import pxssh
import socket
import struct
import thread
from ThinClient import ThinClient
from ThinClient import KNOWN_CLIENTS


# The pipe contains command in this order
IPADDR=0
USER=1
PASSWORD=2
DIR=3
URL=4
RESET=5

REMOTE_CLIENTS = {}

class Colonize:
    def __init__(self):
        self.filename = os.path.join("/tmp", 'colonize')
        self.fifo = None
        if os.path.exists(self.filename):
            os.remove(self.filename)
        os.mkfifo(self.filename)
        self.address = self.myIP()
        zombie = Zombie()

    def listen(self):
        self.fifo = open(self.filename, 'r')
        clientInfo = self.fifo.readline().split(' ')
        if len(clientInfo) != 6:
            print "Invalid user input \nExample:"
            print "\techo 192.168.10.10 admin admin /opt/automation ftp://fileserver/client.tgz reset/noreset> /tmp/colonize"
            clientInfo = None
        self.fifo.close()
        return clientInfo

    def myIP(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 0))
        return s.getsockname()[0]

    def prepare(self):
        clientInfo = self.listen()
        thread.start_new_thread( self.invade, (clientInfo,))

    def invade(self, clientInfo):
        if clientInfo is not None:
            try:
                print "starting ssh..."
                ssh = pxssh.pxssh()
                #ssh.PROMPT= 'SSH> '
                #options={"StrictHostKeyChecking": "no", "UserKnownHostsFile": "/dev/null"})
                hostname = clientInfo[IPADDR].strip()
                username = clientInfo[USER].strip()
                password = clientInfo[PASSWORD].strip()
                destDir  = clientInfo[DIR].strip()
                dloadUrl = clientInfo[URL].strip()
                reset = clientInfo[RESET].strip() == "reset"
                ssh.login(hostname, username, password)
                print ssh.before
                ssh.sendline("export DISPLAY=:0")   # cd to directory where you want to install
                ssh.prompt()             # match the prompt
                ssh.sendline("mkdir -p " + destDir)   # cd to directory where you want to install
                ssh.prompt()             # match the prompt
                ssh.sendline("cd " + destDir)   # cd to directory where you want to install
                ssh.prompt()             # match the prompt
                ssh.sendline("rm -rf agent agent.tgz")   # Remove the old install
                print ssh.before
                ssh.prompt()
                 # match the prompt
                ssh.sendline('curl -k -o client.tgz ' + dloadUrl)
                print ssh.before
                ssh.prompt()
                ssh.sendline('tar zxf client.tgz') # unzip the package
                print ssh.before
                ssh.prompt()
                if (reset == True):
                    cmd = 'setsid python agent/AutomationAgent.py server http://' + self.address + ':8080 --debug >'+ os.path.join(destDir, 'automation-console.log') +' 2>&1 &'
                    clientInfo[RESET] = "noreset"
                else:
                    cmd = 'setsid python agent/AutomationAgent.py server http://' + self.address + ':8080 --debug --noreset >'+ os.path.join(destDir, 'automation-console.log') +' 2>&1 &'
                print cmd
                ssh.sendline(cmd)
                ssh.prompt()
                #ssh.sendline("sleep 2")
                #ssh.prompt()
                ssh.logout()
                cid = ThinClient.ComputeClientID(hostname)
                REMOTE_CLIENTS[cid] = (hostname, ' '.join(clientInfo))
            except Exception as e:
                print "Remote install failed for :",' '.join(clientInfo)

    def __del__(self):
        self.fifo.close()
        os.remove(self.filename)

class Zombie:
    def __init__(self):
        thread.start_new_thread(self.awakenDead, ())

    def awakenDead(self):
        while True:
            time.sleep(120)
            for c in REMOTE_CLIENTS.keys():
                if c in KNOWN_CLIENTS.keys():
                    client = KNOWN_CLIENTS[c]
                    if client.isZombie() == True:
                        hostname, clientInfo = REMOTE_CLIENTS[c]
                        if self.checkFrankenstein(hostname) == True:
                            print "Reviving Client", hostname, "since it seems dead"
                            self.doAlchemy(clientInfo)

                else:
                    print "Client", REMOTE_CLIENTS[c], "has a failed install, most probably permissions or download url."
                    print "Removing from monitor list"
                    del REMOTE_CLIENTS[c]

    def checkFrankenstein(self, hostname):
        return os.system("ping -c 1 %s >/dev/null 2>&1" %(hostname)) == 0

    def doAlchemy(self, clientInfo):
        with open("/tmp/colonize", "w") as f:
            f.write(clientInfo)
            f.close()

#unit test
if __name__=='__main__':
    c = Colonize()
    c.prepare()
