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
		self.elements = None
		self.element = None

		self.handler = {
			"start" :  self.driverLoad,
			"clickcss" : self.clickElementCSS,
			"clickname" : self.clickElementName,
			"clickid" : self.clickElementId,
			"clickxpath" : self.clickElementXPath,
			"clickmenutext" : self.clickMenuText,
			"clickmenuitem" : self.clickMenuItem,
			"clearcss" 	: self.clearElementCSS,
			"clearname" : self.clearElementName,
			"clearid"	: self.clearElementId,
			"clearxpath": self.clearElementXPath,
			"open"  : self.openLink,
			"fillcss"  : self.fillElementCSS,
			"fillname"  : self.fillElementName,
			"fillid"  : self.fillElementId,
			"fillxpath"  : self.fillElementXPath,
			"counttags"  : self.countTags,
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
		string = reader.readline().strip()
		#string = string.replace("'", "\"")
		#args = shlex.split(string)
		args = string.split()
		which = None
		what  = None
		if len(args) == 0:
			return True
		cmdInfo = args[0]
		if len(args) >= 2:
			which = args[1]
		if len(args) >= 3:
			what = " ".join(args[2:])
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
		print "Writing result " + output + result
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
		self.elements = self.driver.find_elements_by_css_selector(which)
		return self.elements[0]

	def findElementName(self, which):
		self.elements = self.driver.find_elements_by_name(which)
		return self.elements[0]

	def findElementId(self, which):
		self.elements = self.driver.find_elements_by_id(which)
		return self.elements[0]

	def findElementXPath(self, which):
		self.elements = self.driver.find_elements_by_xpath(which)
		print len(self.elements)
		return self.elements[0]

	def clickElementCSS(self, which, what):
		self.element = self.findElementCSS(which)
		self.element.click()
		return "Pass"

	def clickElementName(self, which, what):
		self.element = self.findElementName(which)
		self.element.click()
		return "Pass"

	def clickElementId(self, which, what):
		self.element = self.findElementId(which)
		self.element.click()
		return "Pass"

	def clickElementXPath(self, which, what):
		self.element = self.findElementXPath(which)
		self.element.click()
		return "Pass"

	def clickMenuText(self, which, what):
		for link in self.element:
			if link.text() == which:
				link.click()
		return "Pass"

	def clickMenuItem(self, which, what):
		sys.stdout.write("length is " + str(len(self.elements)));
		self.elements[int(which)].click()
		return "Pass"

	def fillElementCSS(self, which, what):
		self.element = self.findElementCSS(which)
		self.element.send_keys(what)
		return "Pass"

	def fillElementName(self, which, what):
		self.element = self.findElementName(which)
		self.element.send_keys(what)
		return "Pass"

	def fillElementId(self, which, what):
		self.element = self.findElementId(which)
		self.element.send_keys(what)
		return "Pass"

	def fillElementXPath(self, which, what):
		self.element = self.findElementXPath(which)
		self.element.send_keys(what)
		return "Pass"

	def countTags(self, which, what):
		self.element = self.findElementXPath(which)
		if len(self.element) == what:
			return "Pass"
		return "Fail"

	def clearElementCSS(self, which, what):
		self.element = self.findElementCSS(which)
		self.clearIfPossible(self.element)
		return "Pass"

	def clearElementName(self, which, what):
		self.element = self.findElementName(which)
		self.clearIfPossible(self.element)
		return "Pass"

	def clearElementId(self, which, what):
		self.element = self.findElementId(which)
		self.clearIfPossible(self.element)
		return "Pass"

	def clearElementXPath(self, which, what):
		self.element = self.findElementXPath(which)
		self.clearIfPossible(self.element)
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
