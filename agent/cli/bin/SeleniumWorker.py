import os
import sys
import shlex
sys.path.append("agent")
from thirdparty import selenium
from selenium import webdriver


class SeleniumWorker:
	def __init__(self, which):
		self.driver = None
		self.rfilename = os.path.join("/tmp", 'rselenium')
		self.wfilename = os.path.join("/tmp", 'wselenium')
		self.handler = {
			"start" :  self.driverLoad,
			"clickcss" : self.clickElementCSS,
			"clickname" : self.clickElementName,
			"clickid" : self.clickElementId,
			"clickxpath" : self.clickElementXPath,
			"clearcss" 	: self.clearElementCSS,
			"clearname" : self.clearElementName,
			"clearid"	: self.clearElementId,
			"clearxpath": self.clearElementXPath,
			"open"  : self.openLink,
			"fillcss"  : self.fillElementCSS,
			"fillname"  : self.fillElementName,
			"fillid"  : self.fillElementId,
			"fillxpath"  : self.fillElementXPath,
			"stop"  :  self.driverUnload
		}
		self.exit = False
		if not os.path.exists(self.rfilename):
			os.mkfifo(self.rfilename)
			os.mkfifo(self.wfilename)
		else:
			sys.stdout.write("Selenium instance is running already\n")
		result = self.driverLoad(which, None)
		self.WriteResult(result, "Selenium worker started")

	def GetCmd(self):
		reader = open(self.rfilename, 'r')
		args = shlex.split(reader.readline().strip())
		which = None
		what  = None
		if len(args) == 0:
			return True
		cmdInfo = args[0]
		if len(args) > 1:
			which = args[1]
		if len(args) > 2:
			what = args[2]
		reader.close()
		try:
			if cmdInfo in self.handler.keys():
				result = self.handler[cmdInfo](which, what)
				self.WriteResult(result, cmdInfo + " succeeded")
			else:
				self.WriteResult("Fail", cmdInfo + " failed")
		except Exception as e:
				self.WriteResult("Fail", cmdInfo + " " +str(e))
		return True

	def WriteResult(self, result, output):
		writer = open(self.wfilename, 'w')
		writer.write(result + " " + output + os.linesep)
		writer.close()

	def driverLoad(self, which, what):
		result = "Pass"
		if self.driver == None and which.lower() == "firefox":
			self.driver = webdriver.Firefox()
		else:
			result = "Fail"
			sys.stdout.write("driver loading\n")
		return result

	def driverUnload(self, which, what):
		if self.driver is not None:
			self.driver.close()
		self.exit = True
		return "Pass"

	def openLink(self, which, what):
		print "opening '" + which + "'"
		self.driver.get(which)
		self.driver.maximize_window()
		return "Pass"

	def clearIfPossible(self, which):
		try:
			which.clear()
		except Exception as e:
			pass

	def findElementCSS(self, which):
		element = self.driver.find_element_by_css_selector(which)
		return element

	def findElementName(self, which):
		element = self.driver.find_element_by_name(which)
		return element

	def findElementId(self, which):
		element = self.driver.find_element_by_id(which)
		return element

	def findElementXPath(self, which):
		element = self.driver.find_element_by_xpath(which)
		return element

	def clickElementCSS(self, which, what):
		self.findElementCSS(which).click()
		return "Pass"

	def clickElementName(self, which, what):
		self.findElementName(which).click()
		return "Pass"

	def clickElementId(self, which, what):
		self.findElementId(which).click()
		return "Pass"

	def clickElementXPath(self, which, what):
		self.findElementXPath(which).click()
		return "Pass"

	def fillElementCSS(self, which, what):
		element = self.findElementCSS(which)
		element.send_keys(what)
		return "Pass"

	def fillElementName(self, which, what):
		element = self.findElementName(which)
		element.send_keys(what)
		return "Pass"

	def fillElementId(self, which, what):
		element = self.findElementId(which)
		element.send_keys(what)
		return "Pass"

	def fillElementXPath(self, which, what):
		element = self.findElementXPath(which)
		element.send_keys(what)
		return "Pass"

	def clearElementCSS(self, which, what):
		element = self.findElementCSS(which)
		self.clearIfPossible(element)
		return "Pass"

	def clearElementName(self, which, what):
		element = self.findElementName(which)
		self.clearIfPossible(element)
		return "Pass"

	def clearElementId(self, which, what):
		element = self.findElementId(which)
		self.clearIfPossible(element)
		return "Pass"

	def clearElementXPath(self, which, what):
		element = self.findElementXPath(which)
		self.clearIfPossible(element)
		return "Pass"

	def cleanup(self):
		os.remove(self.rfilename)
		os.remove(self.wfilename)

#unit test
if __name__=='__main__':
	worker = SeleniumWorker(sys.argv[1])
	while worker.GetCmd():
		if worker.exit is True:
			break
	worker.cleanup() # ideally in __del__ but sometimes doesnt get called?!
