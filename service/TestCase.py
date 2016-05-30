import ast
import json
import ConfigParser
class TestCase:
    """
    The notional represntation of a test case constructor.
    """
    def __init__(self, name, rank, desc, commands):
        self.name = name
        self.rank = rank
        self.desc = desc
        self.commands = commands
        self.starttime = None
        self.endtime = None
        self.result = "Pending"
        self.console = ""
        self.details = "Details are not yet available ..."
    
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

    """
    Load test case configuration from disk. Called by thinclient method.
    """    
    @staticmethod
    def LoadFromDisk(filename):
        testsuite = list()
        config = ConfigParser.ConfigParser()
        config.read(filename)
        for c in config.sections():
            name = c
            desc = config.get(c , "desc")
            try:
                rank = int(config.get(c , "rank"))
            except:
                rank = 100

            commands = ast.literal_eval(config.get(c , "commands"))
            testsuite.append(TestCase(name, rank, desc, commands))
        sorted_suite = sorted(testsuite, key=lambda x: x.rank, reverse=False)
        return sorted_suite
