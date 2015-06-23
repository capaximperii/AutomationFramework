import ast
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
        self.console = None
        self.details = "Details are not yet available ..."
    """
    Html representation of a test case for the stats page.
    """
    def prettyOutput(self):
        c = "<br>".join(self.commands)
        #c = "\n".join(self.commands)
        red = "#E84C3D"
        pink = "#F899C3"
        green ="#267E79"
        orange = "#FAB148"
        if not self.console:
            self.console = ""
        fmt = "<tr><td> %s </td> <td> %s </td> <td> %s </td> <td> %s </td> <td> %s </td> <td> %s </td> <td bgcolor='%s'> %s</td></tr> "
        if self.result == "Pass":
            o = fmt % (self.name, self.desc, c, self.starttime, self.endtime, self.console.replace("\n","<br>"), green, self.result)
        elif self.result == "Fail":
            o = fmt % (self.name, self.desc, c, self.starttime, self.endtime, self.console.replace("\n","<br>"), red, self.result)
        elif self.result == "Running":
            o = fmt % (self.name, self.desc, c, self.starttime, self.endtime, self.console.replace("\n","<br>"), pink, self.result)
        else:
            o = fmt % (self.name, self.desc, c, self.starttime, self.endtime, self.console.replace("\n","<br>"), orange, self.result)
        o += "<tr><td colspan=7><pre>%s</pre></td></tr>" % (self.details)
        return o
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
