from core import docopt
from cli.core.ResultStore import ResultStore
import sys
import os
import logging
import json

"""
Provides an interface between the client and the command line interface of the framework.

@author
@version     0.1
@since       2015-01-01
"""
def CliExecCommand(args):
    module = args.split()[0]
    cmdArgs = " ".join(args.split()[1:])
    importLine = """from plugins import %s as Plugin""" % ( module )
    execLine   = """prompt.do_%s("%s")""" % ( module, cmdArgs )
    store = ResultStore.getResultStore()
    try:
        exec(importLine)
        prompt = Plugin.setup()
        exec(execLine)
        retVal = store.getRetVal()
    except Exception as e:
        err =  "Command Error for : '%s' with %s" % (args, str(e))
        logger = logging.getLogger("cliInterface")
        logger.warn(err)
        store.setRetVal("Fail")
        store.Log(err)
        retVal = "Fail"
    print retVal
    return retVal

"""
Execute a cli command as a child process instead of in the same process.
"""
def CliExecCommandMultiprocess(args, q):
    store = ResultStore.getResultStore()
    CliExecCommand(args)
    q.put(store.dumps())

"""
Executes a list of commands in sequence, will continue even in case of failure.
"""
def CliExecCommandList(commandList):
    for c in commandList:
        err =  "\nExecuting '%s'" % (c.strip())
        logger = logging.getLogger("cliInterface")
        logger.warn(err)
        CliExecCommand(c)

"""
Start the command line shell for plugin commands.
"""
def GetShell(args):
    module = args
    importLine = """from plugins import %s as Plugin""" % ( module )
    execLine   = """Plugin.main()"""
    try:
        exec(importLine)
        exec(execLine)
        retVal = ResultStore.getResultStore().getRetVal()
    except Exception as e:
        print str(e)
        err =  "Command Error for : '%s' with %s" % (args, str(e))
        logger = logging.getLogger("cliInterface")
        logger.warn(err)
        ResultStore.getResultStore().setRetVal("Fail")
        retVal = "Fail"

"""
Returns a list of available plugins.
"""
def GetAvailModules():
    mods = []
    for directory, dirnames, filenames in os.walk("agent/cli/plugins"):
        break
    for f in filenames:
        if f.endswith('.py') and f != "__init__.py":
            mods.append(f.replace('.py', ''))
    return mods
