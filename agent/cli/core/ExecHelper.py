import os
import sys
import shlex
import logging
from ResultStore import ResultStore
from thirdparty.pexpect import pexpect

"""
The exechelper provides a set of helper routines to execute plugin commands and save
output in a form that is easier to send to the server for reports.
"""
class ExecHelper():
    """
    The constructor
    """
    def __init__(self):
        self.r = ResultStore.getResultStore()

    """
    Set the exit code of the command last run.

    @param:    command:    The command line
    @param:    output:        The stdout of the command
    @param:    retVal:        The return value as Pass/Fail ...
    """
    def setExecCodes(self, command, output, retVal):
        self.r.setRetVal(retVal)
        self.r.setOutput(output)
        self.r.setCommand(command)
    """
    Reset the contents of result store, since it may contain result of the previous command
    that was run.

    @param:    command:    The command line
    @param:    spl:        Indicates if it is a special command, ex: Depends
    """
    def reset(self, command, spl=False):
        self.r.setRetVal("Pass")
        self.r.setOutput("")
        self.r.setCommand(command)
        if spl == True:
            self.r.resetSpecial()
    """
    Log to resultstore
    """
    def Log(self, log):
        self.r.Log(log)

    """
    Reset the contents of result store, since it may contain result of the previous test case
    that was run.

    @param:    desc:        Description of the new test case about to run
    """

    def resetTestcase(self, desc):
        self.reset(desc, True)
        self.r.resetLog()

    """
    Check if the output contains a string.

    @param:    command:        The linux command.
    @param:    expectation:    The string expected in the output
    """
    def OutputContains(self, command, expectation):
        try:
            (output,retVal) = pexpect.run(command, withexitstatus=1)
        except Exception as e:
            output = str(e)
            logger = logging.getLogger("Exechelper")
            logger.warn(output)
        if expectation.strip() in output:
            self.setExecCodes(command, output, "Pass")
        else:
            self.setExecCodes(command, output, "Fail")
        return ["Fail","Pass"][expectation.strip() in output.strip()]

    """
    Check if the output equals a string.

    @param:    command:        The linux command.
    @param:    expectation:    The string expected in the output
    """
    def OutputEquals(self, command, expectation):
        try:
            (output,retVal) = pexpect.run(command, withexitstatus=1)
        except Exception as e:
            output = str(e)
            logger = logging.getLogger("Exechelper")
            logger.warn(output)
        if expectation.strip() == output.strip():
            self.setExecCodes(command, output, "Pass")
        else:
            self.setExecCodes(command, output, "Fail")
        return ["Fail","Pass"][expectation.strip() == output.strip()]
    """
    Check if the command exitcode is as expected.

    @param:    command:        The linux command.
    @param:    ExitCode:        The command exit code expected.
    """

    def EvalRetVal(self, command, ExitCode=0):
        try:
            (output,retVal) = pexpect.run(command, withexitstatus=1)
        except Exception as e:
            output = str(e)
            logger = logging.getLogger("Exechelper")
            logger.warn(output)
            retVal = output
        if retVal == ExitCode:
            self.setExecCodes(command, output, "Pass")
        else:
            self.setExecCodes(command, output, "Fail")
        return ["Fail","Pass"][retVal == ExitCode]

    """
    Spawns a linux command independent of the controlling program in a non blocking way.

    @param:    command:    The linux command to be run.
    """
    def Spawn(self, command, ExitCode = 0):
        if os.fork() == 0:
            if os.fork():
                sys.exit(0)
            spawnopts = shlex.split(command)
            os.execvpe(spawnopts[0], spawnopts, os.environ)
        os.wait()

    def Execute(self, command, ExitCode=0):
        return os.system(command)
    """
    Returns the output of a command to be run on console.

    @param:    command:    The linux command to be run.
    """
    def RetOutput(self, command):
        try:
            output = pexpect.run(command)
        except Exception as e:
            output = str(e)
            logger = logging.getLogger("Exechelper")
            logger.warn(output)
        #this always sets pass
        self.setExecCodes(command, output, "Pass")
        return str(output)
