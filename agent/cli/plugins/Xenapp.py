from cli.core.Console import Console
from cli.core.docopt import docopt
from cli.core.ExecHelper import ExecHelper
import sys
import os
import time

#####
from thirdparty import selenium
from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
#####

class Cli(Console):
	def __init__(self):
		Console.__init__(self)
		self.doc = """
		Usage:
			Xenapp application <username> <password> <url> APPNAME...
			Xenapp desktop <username> <password> <url> APPNAME...
			Xenapp (-h | --help | --version)

		Arguments:
			APPNAME Citrix appname as it appears in the webpage.

		Options:
			-h, --help  Show this screen.
		"""

	def do_Xenapp(self, args):
		command = docopt(str(self.doc), args)
		e = ExecHelper()
		e.reset("Xenapp")
		if command["application"] or command["desktop"]:
			citrixuser = command['<username>']
			citrixpass = command['<password>']
			citrixurl = command['<url>']
			citrixapp = " ".join(command['APPNAME'])
			citrixappmod = citrixapp.replace(" ", "_0020")
				#driver = webdriver.Firefox()
			profpath = os.path.join(os.getenv('HOME'),".mozilla", "firefox", "wyse_default")
			if os.path.exists(profpath):
				e.Log("using existing profile")
				profile = FirefoxProfile(profpath)
			else:
				e.Log("using a temporary profile")
				profile = FirefoxProfile()
				driver = webdriver.Firefox(profile)
				driver.implicitly_wait(60)
				driver.get(citrixurl)
				#driver.find_element_by_id("skipWizardLink").click()
				driver.find_element_by_id("user").clear()
				driver.find_element_by_id("user").send_keys(citrixuser)
				driver.find_element_by_id("password").clear()
				driver.find_element_by_id("password").send_keys(citrixpass)
				driver.find_element_by_css_selector("span.rightDoor").click()
			if command["desktop"]:
				e.Log("finding ")
				driver.find_element_by_css_selector("#Desktops_Text > span").click()
			try:
				appid = "a[id*='%s']" % citrixappmod
				element =  driver.find_element_by_css_selector(appid)
				element.click()
				#e.setExecCodes(args, "Check app launch using Process alive wfica.orig","Pass")
			except Exception as e:
				print str(e)
				e.Log(str(e))
				print "Oops app not found!!", citrixapp
				e.setExecCodes(args, "Could not locate app","Fail")
			#The app takes its own sweet time coming up. Should sleep time be a parameter?
			print "Waiting for 90 secs before checking for window creation"
			time.sleep(90)
			chkcmd = "./agent/cli/bin/windowinfo.sh '%s'" % citrixapp
			e.RetOutput(chkcmd)
			e.Log(e.r.getOutput())

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
