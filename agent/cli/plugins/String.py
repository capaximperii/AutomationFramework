from cli.core.Console import Console
from cli.core.docopt import docopt
from cli.core.ExecHelper import ExecHelper
import sys


class Cli(Console):
	def __init__(self):
		Console.__init__(self)
		self.doc = """
		Usage:
			String split <input> using <delimiter> joinedby <outputdelimiter> giving INDEX...
			String use <outputdelimiter> join STRINGS...
			String replace <old> with <new> in STRINGS...
			String trim <input>
			String clip head <start> and tail <end> of <input>
			String (-h | --help | --version)

		Options:
			-h, --help  Show this screen.
		"""

	def do_String(self, args):
		command = docopt(str(self.doc), args)
		e = ExecHelper()
		e.reset("String")
		#e.Log(args)
		if command["split"]:
			split = command['<input>'].split(command['<delimiter>'])
			result = ""
			for i in command['INDEX']:
				result += split[int(i)] + command['<outputdelimiter>']
		elif command["join"]: # should be command['use']
			result = ""
			for s in command['STRINGS']:
				result += s + command['<outputdelimiter>']
		elif command["replace"]:
			result = ""
			for s in command['STRINGS']:
				result += s.replace(command['<old>'], command['<new>']) + " "
		elif command["trim"]:
			result = str(command['<input>']).strip()
		elif command["clip"]:
			start = int(command['<start>'])
			end = int(command ['<end>'])
			if end == 0:
				end = - len(command['<input>'])
			result = str(command['<input>'] [start:] [:-end])		
		print result
		e.setExecCodes(command, result, "Pass")

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
