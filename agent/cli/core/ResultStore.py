import json
Singleton = lambda c: c()

"""
The result store class provides a singleton object instance to store the command results.
"""
@Singleton
class ResultStore:
    """
    The constructor
    """
    def __init__(self):
        self.command = None
        self.output  = "Assume Success"
        self.retVal  = None
        self.specialRet = None
        self.specialOut = None
        self.log = ""

    """
    Reset in case of special commands. The example of a special command is Depends.
    """
    def resetSpecial(self):
        self.specialRet = None
        self.specialOut = None
    """
    Return the instance of the singleton result store.
    """
    def getResultStore(self):
        return self
    """
    Set the command that the result store will hold result for.
    """
    def setCommand(self, cmd):
        self.command = cmd
    """
    reset the console output
    """
    def resetLog(self, log=""):
        self.log = log
    """
    Log the console output
    """
    def Log(self, log):
        self.log += log + "\n"
    """
    Get the console output
    """
    def getLog(self):
        return self.log

    """
    Get the command that the result store holds result for.
    """
    def getCommand(self):
        return self.command
    """
    Set the output of the command.
    """
    def setOutput(self, output):
        if self.retVal in ["Skip", "Repeat"]:
            self.specialOut = output
        self.output = output
    """
    Get the output of the command.
    """
    def getOutput(self):
        if self.specialOut is not None:
            return self.specialOut
        return self.output

    """
    Set the return value of the command.
    """
    def setRetVal(self,retVal):
        if retVal in ["Skip", "Repeat"]:
            self.specialRet = retVal
        self.retVal = retVal
    """
    Get the return value of the command.
    """
    def getRetVal(self):
        if self.specialRet is not None:
            return self.specialRet
        return self.retVal

    """
    Serialize the resultstore object.
    """
    def dumps(self):
        return json.dumps(self,
            default=lambda o: o.__dict__,
                sort_keys=True, indent=4)

"""
ClientConstants holds the constants used for variable substitution.
"""
@Singleton
class ClientConstants:
    """
    Constructor
    """
    def __init__(self):
        self.constants = dict()
        pass
    """
    Return all client constants as a dictionary.
    """
    def getClientConstants(self):
        return self
    """
    Add a key value pair to the constant list.
    """
    def addInfo(self, key, value):
        self.constants[key] = value
    """
    Find and replace a variable in a CLI command.
    """
    def preProcessCli(self, command):
        for k in self.constants.keys():
            command = command.replace(k, str(self.constants[k]))
        return command
