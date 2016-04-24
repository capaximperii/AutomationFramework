from cli.core.Console import Console
from cli.core.docopt import docopt
from cli.core.ExecHelper import ExecHelper
import sys
import urllib
import urllib2
import os

class UploadFile(file):
	def __init__(self, *args, **keyws):
		file.__init__(self, *args, **keyws)

	def __len__(self):
		return int(os.fstat(self.fileno())[6])



class Cli(Console):
	def __init__(self):
		Console.__init__(self)
		self.doc = """
		Usage:
			Http upload <url> <localfile>
			Http download <url> <localfile>
			Http (-h | --help | --version)

		Options:
			-h, --help  Show this screen.
		"""

	def do_Http(self, args):
		command = docopt(str(self.doc), args)
		e = ExecHelper()
		e.reset("Http")
		try:
			if command["download"]:
				e.Log("Http downloading")
				urllib.urlretrieve (command["<url>"], command["<localfile>"])
				e.setExecCodes("Http", "File downloaded", "Pass")
			else:
				e.Log("Http uploading")
				toUpload = UploadFile(command["<localfile>"], 'r')
				theHeaders= {'Content-Type': 'text/xml'}
				theRequest = urllib2.Request(command["<url>"], toUpload, theHeaders)
				response = urllib2.urlopen(theRequest)
				toUpload.close()
			e.Log("Http command passed")
		except Exception as e:
			print str(e)
			e.Log("Http failed " + str(e))
			e.setExecCodes("", str(e), "Fail")

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
