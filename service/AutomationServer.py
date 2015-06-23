import os
import sys
import json
import select
import thread
import urllib
import SocketServer
from Colonize import Colonize
from ThinClient import javascript
from ThinClient import ThinClient
from ThinClient import KNOWN_CLIENTS

PORT_NUMBER = 8080

CLIENT_COMMANDS = ["/result" , "/gettest", "/reset", "/noreset","/fileupload", "/quitting", "/registry",
    "/cpuinfo", "/lspciinfo", "/dmiinfo", "/dmidecodeinfo","/dmesg", "/lshwinfo", "/sysfs",
    "/etcmodules", "/lsmod", "/modprobe", "/osinfo", "/pkginfo", "/envinfo", "/sysctl", "/depcheck"]

"""
Automation server is the server main class that is the web server providing HTTP service to clients.
"""
class AutomationServer(SocketServer.BaseRequestHandler):
    def handle(self):
        client = self.getClientAddress()
        data = ""
        while True:
            incoming = select.select([self.request],[], [], 5)
            if not incoming[0]:
                break
            quantum = self.request.recv(1400)
            if not quantum.endswith('\r\n'):
                data += quantum
            elif quantum.endswith('\r\n'):
                data += quantum
                break
            elif len(quantum) == 0:
                break
        data = data.strip()
        data = self.getPayload(data)
        if len(data.strip()) > 0:
            cid, path, arg = json.loads(data)
        else:
            #This is a browser stat request
            cid, path , arg = [ None, "/stats", ""]
        self.sendHeader()
        if not cid:
            cid = ThinClient.ComputeClientID(client)
        if cid not in KNOWN_CLIENTS.keys() and path in CLIENT_COMMANDS:
            print "Client %s assigned CID %s"%(client, cid)
            KNOWN_CLIENTS[cid] = ThinClient(client)
            KNOWN_CLIENTS[cid].reset()
            self.ContactClient(cid, "Associated")
        elif cid in KNOWN_CLIENTS.keys() and path == "/noreset":
            print "Resuming client from where it last left", client
            self.ContactClient(cid, "Associated")
        elif path == "/stats":
            res = "<!DOCTYPE html>\n<html>"
            res += javascript
            res += "<title> Automation server statistics </title>"
            for c in KNOWN_CLIENTS.keys():
                res += KNOWN_CLIENTS[c].prettyOutput()
            res += "<footer><B><a href=/ssh>Remote installer</a>&nbsp;&nbsp;&nbsp<a href=/config>Upload config</a></B></footer>"
            res += "</html>"
            self.request.sendall(res)
            #self.ContactClient(cid, res)
        elif path == "/gettest":
            testcase = KNOWN_CLIENTS[cid].sendTestCase()
            self.ContactClient(cid, testcase)
        elif path == "/result":
            KNOWN_CLIENTS[cid].recieveResult(arg)
            self.ContactClient(cid, "OK")
        elif path == "/depcheck":
            retVal, deparg, console = json.loads(arg)
            depip,deprank = deparg
            depcid = ThinClient.ComputeClientID(depip)
            if depcid in KNOWN_CLIENTS.keys() and KNOWN_CLIENTS[depcid].GetCurrentTestRank() > int(deprank):
                KNOWN_CLIENTS[cid].recieveResult(arg, True)
                self.ContactClient(cid, "OK")
            else:
                print "client %s will wait for client %s" % (client, depip)
                self.ContactClient(cid, "WAITON")
        elif path == "/fileupload":
            KNOWN_CLIENTS[cid].recieveLog(arg)
            self.ContactClient(cid, "UPLOADED")
        elif path == "/config":
            page = """
                <!DOCTYPE html>
                <html>
                <body>
                <form action="/confupload" method="post" enctype="multipart/form-data">
                    Select config file to upload:
                        <input type="file" name="fileToUpload" id="fileToUpload">
                        <input type="submit" name="submit" value="upload configuration">
                </form>

                </body>
                </html>
                """
            self.request.sendall(page)
        elif path == "/ssh":
            page = """
            <!DOCTYPE html>
            <html>
            <title>Automation Framework: SSH based remote installer</title>
            <body>
            <form action="/sshaction" method="post" encoding="form-data">
            <table>
                    <tr><td>Client ip </td><td><input type="text" name="ipaddress" required></td></tr>
                    <tr><td>SSH User </td><td><input type="text" name="username" required></td></tr>
                    <tr><td>SSH Password</td><td><input type="password" name="password" required></td></tr>
                    <tr><td>Install path </td><td><input type="text" name="path" required></td></tr>
                    <tr><td>Download URL </td><td><input type="url" name="url" required></td></tr>
                    <tr><td></td><td><input type="submit" value="Install"></td></tr>
            </table>
            </form>
            </body>
            </html>
            """
            self.request.sendall(page)
        elif path =="/sshaction":
            params = arg.strip().split('&')
            ipaddress = username = password = path = url = ""
            for p in params:
                if p.split('=')[0] == "ipaddress":
                    ipaddress = urllib.unquote(p.split('=')[1])
                elif p.split('=')[0] == "username":
                    username = urllib.unquote(p.split('=')[1])
                elif p.split('=')[0] == "password":
                    password = urllib.unquote(p.split('=')[1])
                elif p.split('=')[0] == "path":
                    path = urllib.unquote(p.split('=')[1])
                elif p.split('=')[0] == "url":
                    url = urllib.unquote(p.split('=')[1])
            sshaction = ipaddress + " " + username + " " + password + " " + path + " " + url + " reset\n"
            with open("/tmp/colonize", "w") as f:
                f.write(sshaction)
                f.close()
            page = self.redirectToStats()
            self.request.sendall(page)
        elif path =="/confupload":
            filename, filecontent = arg
            f = open(os.path.join("config", filename), "w")
            f.write(filecontent)
            f.close()
            page = self.redirectToStats()
            self.request.sendall(page)
        elif path == "/cpuinfo":
            KNOWN_CLIENTS[cid].recieveCpuInfo(arg)
            self.ContactClient(cid, "UPLOADED")
        elif path == "/lspciinfo":
            KNOWN_CLIENTS[cid].recieveInfoToRaw(arg, "__LSPCI__")
            self.ContactClient(cid, "UPLOADED")
        elif path == "/dmiinfo":
            KNOWN_CLIENTS[cid].recieveInfoToRaw(arg, "__DMI__")
            self.ContactClient(cid, "UPLOADED")
        elif path == "/dmidecodeinfo":
            KNOWN_CLIENTS[cid].recieveInfoToRaw(arg, "__DMIDECODE__")
            self.ContactClient(cid, "UPLOADED")
        elif path == "/dmesg":
            KNOWN_CLIENTS[cid].recieveInfoToRaw(arg, "__DMESG__")
            self.ContactClient(cid, "UPLOADED")
        elif path == "/etcmodules":
            KNOWN_CLIENTS[cid].recieveInfoToRaw(arg, "__ETCMODULES__")
            self.ContactClient(cid, "UPLOADED")
        elif path == "/lsmod":
            KNOWN_CLIENTS[cid].recieveInfoToRaw(arg, "__LSMOD__")
            self.ContactClient(cid, "UPLOADED")
        elif path == "/modprobe":
            KNOWN_CLIENTS[cid].recieveInfoToRaw(arg, "__MODPROBE__")
            self.ContactClient(cid, "UPLOADED")
        elif path == "/osinfo":
            KNOWN_CLIENTS[cid].recieveInfoToFmt(arg, "__OSINFO__", "=")
            self.ContactClient(cid, "UPLOADED")
        elif path == "/sysctl":
            KNOWN_CLIENTS[cid].recieveInfoToRaw(arg, "__SYSCTL__")
            self.ContactClient(cid, "UPLOADED")
        elif path == "/sysfs":
            KNOWN_CLIENTS[cid].recieveInfoToRaw(arg, "__SYSFS__")
            self.ContactClient(cid, "UPLOADED")
        elif path == "/envinfo":
            KNOWN_CLIENTS[cid].recieveInfoToRaw(arg, "__ENVINFO__")
            self.ContactClient(cid, "UPLOADED")
        elif path == "/lshwinfo":
            KNOWN_CLIENTS[cid].recieveInfoToRaw(arg, "__LSHW__")
            self.ContactClient(cid, "UPLOADED")
        elif path == "/registry":
            KNOWN_CLIENTS[cid].recieveInfoToRaw(arg, "__REGISTRY__")
            self.ContactClient(cid, "UPLOADED")
        elif path == "/pkginfo":
            KNOWN_CLIENTS[cid].recieveInfoToFmt(arg, "__PACKAGESINFO__", "-")
            self.ContactClient(cid, "UPLOADED")
        elif path == "/quitting":
            KNOWN_CLIENTS[cid].close()
            self.ContactClient(cid, "OK")
        elif path == "/reset":
            c = ""
            retVal, rankarg, console = json.loads(arg)
            if rankarg:
                c, fromrank, torank, times = rankarg
            if not rankarg:
                KNOWN_CLIENTS[cid].reset()
                self.ContactClient(cid, "OK")
                del KNOWN_CLIENTS[cid]
            elif c in ["Repeat"]:
                KNOWN_CLIENTS[cid].repeatTests(int(fromrank), int(torank), int(times))
                self.ContactClient(cid, "OK")
            elif c in ["Skip"]:
                KNOWN_CLIENTS[cid].deleteTests(int(fromrank), int(torank))
                self.ContactClient(cid, "OK")
        else:
            self.ContactClient(cid, "invalid")
        self.sendFooter()

    """
    Return the data payload sent by client skipping the HTTP header.
    """
    def getPayload(self,data):
        confupload = False
        sshaction = False
        #Skip http header, by ignoring everything above an empty line
        if "GET /config" in data:
            return json.dumps((None, "/config", ""))
        elif "POST /confupload" in data:
            confupload = True
        elif "GET /ssh" in data:
            return json.dumps((None, "/ssh", ""))
        elif "POST /sshaction" in data:
            sshaction = True
        arg = data.split("\n")
        index = 0
        for a in arg:
            if len(a.strip()) == 0:
                break
            index += 1
        arg = arg[index:]
        if confupload is True:
            filecontent = ""
            filename = "default.ini"
            index = 0
            for line in arg:
                if len(line.strip()) > 0:
                    boundary = line.strip()
                    index += 1
                    break
            for line in arg[index+1:]:
                line = line.strip()
                if boundary not in line:    # and len(line) > 0:
                    if line.startswith("Content-") and "filename=" in line:
                        filename = line.split("filename=",1)[1].replace('"','')
                    elif line.startswith("Content"):
                        pass
                    else:
                        filecontent += line + os.linesep
                elif boundary in line:
                    break
            arg = json.dumps((None, "/confupload",(filename,filecontent)))
        elif sshaction is True:
            post = "\n".join(arg)
            arg = json.dumps((None, "/sshaction", post))
        else:
            arg = "\n".join(arg)
        return arg
    """
    """
    def redirectToStats(self):
        page = """
        <html>
        <head>
            <meta http-equiv="refresh" content="2; url=/stats" />
            <title>Configuration saved</title>
        </head>
          <body>
            Configuration sent, Redirecting page...
          </body>
        </html>
        """
        return page

    """
    Send the HTTP header
    """
    def sendHeader(self):
        self.request.sendall("HTTP/1.1 200 OK\r\n Content-type: text/html \r\n\r\n")
    """
    Send the HTTP footer
    """
    def sendFooter(self):
        self.request.sendall("\r\n")
    """
    Send the statistic page.
    """
    def sendStats(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.request.sendall(self.path)
    """
    Get the address where this request originated.
    """
    def getClientAddress(self):
        return self.client_address[0]
    """
    Send data back to the client encoded as json.
    """
    def ContactClient(self, cid, response):
        data = json.dumps((cid,response))
        self.request.sendall(data)
"""
Install agent on the clients via ssh.
"""
def AgentInstaller():
    if sys.platform.startswith("win32"):
        print "This platform does not support remote installer"
        return
    c = Colonize()
    while True:
        c.prepare()


if __name__=='__main__':
    try:
        SocketServer.ThreadingTCPServer.allow_reuse_address = True
        server = SocketServer.ThreadingTCPServer(('', PORT_NUMBER), AutomationServer)
        thread.start_new_thread( AgentInstaller, ())
        print "Starting automation server..."
        server.serve_forever()

    except KeyboardInterrupt:
        print '^C received, shutting down the web server'
        server.socket.close()
