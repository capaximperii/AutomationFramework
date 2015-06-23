import sys
import logging
import os
from cli import cliInterface
from cli.core import docopt

"""
The command line interface bootstrapper.
"""
if __name__=='__main__':
	doc =   """
	Usage:
		cliStart.py test  <which>
		cliStart.py shell
		cliStart.py ncurses
		cliStart.py file <path>
		cliStart.py (-h | --help | --version)
	"""

	command = docopt.docopt(doc, sys.argv[1:])
	logging.basicConfig(filemode="w",
		format='%(asctime)s - %(name)s- %(levelname)s - %(message)s')
	if command['test']:
		cliInterface.GetShell(command['<which>'])
	elif command['shell']:
		print ("Cli configurations available:")
		mods = cliInterface.GetAvailModules()
		while True:
			index = 0
			for m in mods:
				print("\t" + str(index) + " " + str(m))
				index += 1
			try:
				select = int(raw_input("Enter your choice:"))
			except:
				sys.exit(0)
			if select < 0 or select > index:
				continue
			shell = "python agent/cliStart.py test %s" %(mods[select])
			os.system(shell)
	elif command['ncurses']:
		from thirdparty import ncurses
		from ncurses import menu_launcher as menu #do not move this import
		menu_data = {
		'title': "Automation Framework Shell", 'type': "menu", 'subtitle': "Please select an option...",
			'options':[]
		}
		mods = cliInterface.GetAvailModules()
		for m in mods:
			menu_data['options'].extend([{'title': m , 'type' : "command", 'command': 'python agent/cliStart.py test %s'%(m)}])
		menu.processmenu(menu_data)
		menu.endmenu()
		os.system('clear')
	elif command['file']:
		with open(command['<path>'], "r") as f:
			cmdlist = f.readlines()
			cliInterface.CliExecCommandList(cmdlist)
