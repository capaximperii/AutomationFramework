import os
import sys
import time
import json
import socket
import urlparse
import logging
import multiprocessing
from time import sleep
from cli import cliInterface
from cli.core import docopt
from thirdparty.pexpect import pexpect
from thirdparty.standard import urllib
from thirdparty.standard import urllib2
from cli.core.ResultStore import ResultStore
from cli.core.ExecHelper import ExecHelper
from cli.core.ResultStore import ClientConstants

"""
The automation agent implementation, the main entry class to the client side application.

@author
@version     0.1
@since       2015-01-01
"""

class AutomationAgent:
    """
    Automation agent constructor sets the sane defaults to the client side. Some of these values are
    configurable at run time.

    @param:        ip address or hostname, includes the port string.
    """
    def __init__(self, server):
        self.server = server
        self.clientip = None
        self.clientport = None
        self.hostname = socket.gethostname()
        self.currentTest = None
        self.command = None
        self.tmpdir = os.path.join(os.getcwd(), "tmp")
        if not os.path.exists(self.tmpdir):
            os.mkdir(self.tmpdir)
        self.logFile = os.path.join(self.tmpdir,"automation-run.log")
        self.url = None
        self.cid = None
        self.payload = None
        self.clientInfo = None
        self.hist = open(os.path.join(self.tmpdir,"automation-history.log"), "w")
        self.cliQueue = multiprocessing.Queue()
        self.timeout = 1800 # 30 minute timeout to every command

    """
    Request reset of the state machine of this client on the server, if there were previous test
    results on the server, those are discarded and the client starts as a new run.
    """
    def requestReset(self, agentWillReset=True):
        self.tee("Resetting client state")
        self.url = "/reset/yes"
        if agentWillReset == False:
            self.url = "/reset/no"
        self.payload = """["", "",""]"""
        self.contactServer()
        self.clientInfo = ClientConstants.getClientConstants()
        self.clientInfo.addInfo("${SERVER}", self.server)
        self.clientInfo.addInfo("${IPADDRESS}", self.clientip)
        self.clientInfo.addInfo("${HOSTNAME}", self.hostname)
        self.clientInfo.addInfo("${CID}", self.cid)
        self.clientInfo.addInfo("${LOOP}", 1)

    """
    Inform the server that the client has finished execution and will now quit.
    """
    def informQuit(self):
        self.url = "/quitting"
        self.payload = ""
        self.contactServer()

    """
    Get the next test case from the test suite.
    """
    def requestConfig(self):
        self.url = "/gettest"
        self.payload = ""
        self.contactServer()

    """
    Send response of a test case or of a command run remotely by the server.

    @param:        response: The HTTP encoded reponse to a server command.
    """
    def sendResponse(self, response):
        testresult, output, console = response
        encoded = json.dumps(response)
        self.url = "/result"
        if testresult in ["Wait"]:
            self.url = "/depcheck"
        elif testresult in ["Repeat"]:
            self.clientInfo.constants["${LOOP}"] += 1
            self.url = "/reset/yes"
        elif testresult in ["Skip"]:
            self.url = "/reset/yes"
        self.payload = encoded
        self.contactServer()

    """
    Send the contents of a file via the HTTP payload. Not all files can be uploaded so,
    unless there is a specific upload handler url coded in the server which knows how the
    uploaded file is to be handled.

    @param: fpath:    The path of the file to be uploaded.
    @param:    url:    The url that corresponds to this file upload handler
    """
    def sendFile(self, fpath, url):
        self.tee("Trying to upload run log.")
        f = open(fpath,"r")
        content = "".join(f.readlines())
        f.close()
        encoded = json.dumps(content)
        self.url = url
        self.payload = encoded
        self.contactServer()
        self.tee(self.command)

    """
    Run a command and send its output to the server. This is generally used for report generation.

    @param:    cmdline:    The full command line to be run on the client
    @url:    The url that corresponds to this command handler.
    """
    def sendCmdOutput(self, cmdline, url):
        try:
            output = pexpect.run(cmdline)
        except Exception as e:
            output = str(e)
        self.url = url
        encoded = json.dumps(output)
        self.payload = encoded
        self.contactServer()
        self.tee(self.command)

    """
    Install command plugins on demand, from an upgrade url maintained by the automation team.
    This allows for the core engine to be deployed and upgrade only required sections on demand.

    @param:    upgradeurl:    The url of the repository that has the plugin files.
    @param: plugins:    The list of plugins to be downloaded from the repo.
    @param:    rstore:        The resultStore structure that will save the result of the transaction for reports.
    """
    def installPlugins(self, upgradeurl, plugins, rstore):
        self.tee("Plugins will be upgraded from url=" + upgradeurl + ' plugins are ' + ' '.join(plugins))
        retVal = "Pass"
        try:
            for p in plugins:
                pyname = p + ".py"
                urllib.urlretrieve (os.path.join(upgradeurl, pyname),
                            os.path.join("./agent/cli/plugins", pyname))
            rstore.setExecCodes("Downloaded from " + upgradeurl, ' '.join(plugins) , retVal)
        except Exception as ex:
            retVal = "Fail"
            rstore.setExecCodes("Failed download from " + upgradeurl, str(ex), retVal)
        return retVal
    """
    Uninstall all plugins.

    @param:    rstore:        The resultStore structure that will save the result of the transaction for reports.
    """
    def uninstallPlugins(self, rstore):
        self.tee("Plugins will be removed.")
        retVal = "Pass"
        try:
            map(os.unlink, [os.path.join( "./agent/cli/plugins",f) for f in os.listdir("./agent/cli/plugins")] )
            rstore.setExecCodes("Removed all plugins","" ,retVal)
        except Exception as ex:
            retVal = "Fail"
            rstore.setExecCodes("plugin uninstall failed.", str(ex), retVal)
        return retVal

    """
    Handle server command strings that are built-in and from the plugin command system.
    """
    def ExecServerCommand(self):
        if self.command == "QuitAgent":
            if os.path.exists(self.logFile):
                self.sendFile(self.logFile, "/fileupload/runlog.txt")
            self.tee("Server asked us to quit")
            return None
        elif self.command == "Associated":
            self.tee("Server acknowleged us")
            return False
        elif self.command == "OK" :
            self.tee("Result posted")
            return False
        elif self.command == "WAITON" :
            return False
        elif self.command == "UPLOADED" :
            self.tee("file uploaded")
            return False
        else:
            self.currentTest = json.loads(self.command)
            e = ExecHelper()
            e.resetTestcase(self.currentTest['desc'])
            e.r.resetLog()
            e.Log("Starting " + self.currentTest['name'])
            qstore = ResultStore.getResultStore()
            for c in self.currentTest['commands']:
                try:
                    self.tee ("Executing: " + c)
                    varstring = False
                    if c.startswith('Capability add'):
                        c = c.strip()
                        upgradeurl = c.split(' ')[2]
                        plugins = c.split(' ')[3:]
                        retVal = self.installPlugins(upgradeurl, plugins, e)
                    elif c.startswith('Capability remove'):
                        retVal = self.uninstallPlugins(e)
                    elif c.startswith('Timeout set'):
                        self.tee("setting timeout with command " + c);
                        self.timeout = int(c.split(' ')[2])
                    else:
                        #handle all ${}substitution here
                        if c.startswith('${'):
                            varstring = True
                            split = c.split("=",1)
                            if len(split) == 2:
                                varname = c.split("=",1)[0]
                                c = c.split("=",1)[1]
                            else:
                                self.tee("command '" + c +"' syntax error")
                                break
                        c = self.clientInfo.preProcessCli(c)
                        #Write it to history file
                        self.hist.write(c + "\n")
                        #Execute in sandbox so that agent doesnt get killed on plugin exception
                        self.SandboxExec(c)
                        retVal = qstore.getRetVal()
                        if varstring:
                            varvalue = qstore.getOutput().strip()
                            if len(varvalue) == 0:
                                varvalue="null"
                            self.clientInfo.addInfo(varname, varvalue)
                    # Break on first failure in a testcase
                    # continue on to the next testcase
                    if retVal == "Fail" or retVal == "Wait":
                        # This should be logged
                        self.tee("command '" + c +"' caused abort")
                        break
                except Exception as ex:
                    e.setExecCodes(c, str(ex), "Fail")
                    self.tee(str(ex))
                    self.tee("command '" + c +"' caused abort. Probably syntax error.")
                    break
            return True
    """
    Execute a plugin command in a container, so that it does not crash the client agent.
    """
    def SandboxExec(self, c):
        e = ExecHelper()
        cliThread = multiprocessing.Process(target=cliInterface.CliExecCommandMultiprocess,
                    args=(c,self.cliQueue))
        cliThread.start()
        i = 0
        while i < self.timeout:
            i += 1
            sleep(1)
            if not cliThread.is_alive():
                break
        if cliThread.is_alive():
            self.tee("Terminating on timeout")
            e.setExecCodes(c, "Operation timed out", "Fail")
            cliThread.terminate()
        else:
            q = json.loads(self.cliQueue.get_nowait())
            e.setExecCodes(c, q['output'], q['retVal'])
            e.r.resetLog(q['log'])
    """
    Initiate a HTTP connection to the server and send the preset payload, to the preset url.
    All payload is json encoded.
    """
    def contactServer(self):
        try:
            data = json.dumps((self.cid, self.url, self.payload))
            data += "\r\n"
            self.waitForIt()
            self.response = urllib2.urlopen(self.server + self.url, data)
            self.clientip = self.response.fp._sock.fp._sock.getsockname()[0]
            self.clientport = self.response.fp._sock.fp._sock.getsockname()[1]
            data = self.response.read().strip()
            if self.cid == None:
                self.cid, self.command = json.loads(data)
            else:
                cid, self.command = json.loads(data)
                #assert(cid == self.cid)
        except Exception as e:
            self.tee("Exception on data " + str(data))
            self.tee(str(e))
            self.tee("Critical error, is the server running?")
            self.tee("Agent is aborting now.")
            sys.exit(0)
    """
    Wait till server is up
    """
    def waitForIt(self):
        parse = urlparse.urlsplit(self.server)
        while True:
            if os.system("ping -c 1 %s >/dev/null 2>&1"%(parse.hostname)) == 0:
                break
    """
    Tee the log strings to the log file as well as to the console.
    """
    def tee(self, line):
        logger = logging.getLogger("AutomationAgent")
        e = ExecHelper()
        e.Log(line)
        logging.info(line)
        print line

    """
    The destructor function does cleanup.
    """
    def __del__(self):
        self.hist.close()


if __name__=='__main__':
    doc = """
    Usage:
        AutomationAgent.py test [ --debug ] [ --noreset ]
        AutomationAgent.py server <httpurl> [ --debug ] [ --noreset ]
        AutomationAgent.py (-h | --help | --version)
    """
    command = docopt.docopt(doc, sys.argv[1:])
    agentWillReset = True
    if command['test'] == True:
        httpurl = "http://localhost:8080"
    else:
        httpurl = command["<httpurl>"]
    if command['--noreset']:
        agentWillReset = False
    print "Agent is starting ..."
    agent = AutomationAgent (httpurl)
    logging.basicConfig(filename=agent.logFile,level=logging.DEBUG,
            filemode="w",
            format='%(asctime)s - %(name)s- %(levelname)s - %(message)s')
    logging.info("Agent is starting")
    agent.requestReset(agentWillReset) #  start over from 0
    isRebooting = False
    while True:
        if isRebooting == True:
            print "Wait for reboot"
            sleep(1800)
        agent.requestConfig()
        sleep(1)
        ret = agent.ExecServerCommand()
        if ret == True:
            result = ResultStore.getResultStore()
            if result.getRetVal() == "Reboot":
                isRebooting = True
                result.setRetVal("Pass")
            #send only last 512 characters of output to prevent
            #flooding the stat page.
            agent.sendResponse((result.getRetVal(),
                result.getOutput()[:512], result.getLog()))
            sleep(2)
            agent.ExecServerCommand()
        elif ret == False:
            #this is returned by commands that do not expect a response
            pass
        else:
            if command["--debug"]:
                print "uploading debug logs"
                agent.sendCmdOutput("lspci -v", "/fileupload/lspciinfo")
                agent.sendCmdOutput("dmidecode", "/fileupload/dmidecodeinfo")
                agent.sendCmdOutput("cat /proc/cpuinfo", "/fileupload/cpuinfo")
                agent.sendCmdOutput("dmesg", "/fileupload/dmesg")
                agent.sendCmdOutput("cat /etc/modules", "/fileupload/etcmodules")
                agent.sendCmdOutput("find -L /sys/class/dmi", "/fileupload/dmiinfo")
                agent.sendCmdOutput("lsmod", "/fileupload/lsmod")
                agent.sendCmdOutput("sh -c 'cat /etc/modprobe.d/*'", "/fileupload/modprobe")
                agent.sendCmdOutput("sh -c 'cat /etc/*-release'", "/fileupload/osinfo")
                agent.sendCmdOutput("rpm -qa", "/fileupload/pkginfo")
                agent.sendCmdOutput("env", "/fileupload/envinfo")
                agent.sendCmdOutput("cat /etc/sysctl.conf", "/fileupload/sysctl")
                agent.sendCmdOutput("lshw", "/fileupload/lshwinfo")
                agent.sendCmdOutput("udevadm info --export-db", "/fileupload/sysfs")
                agent.sendCmdOutput("python agent/cli/bin/tree.py /etc/wyseroot/registry/save /etc/wyseroot/registry/temp /var/wyse/registry", "/fileupload/registry")
            print "Now quitting..."
            agent.informQuit()
            sleep(2)
            sys.exit(0)
