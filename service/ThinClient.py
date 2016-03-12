from __future__ import division
import hashlib
import json
import math
import os
from datetime import datetime
from TestCase import TestCase
from SuperReport import *
import shutil
import copy

KNOWN_CLIENTS = {}
serverGlobalConfig = {}

## keep a js here just in case needed to alter report in future, replace this

class ThinClient:
	"""
	Constructor  for notional representation of each client
	"""
	def __init__(self, address):
		self.configPath = os.path.join("config", 'clients',"default.ini")
		self.address = address
		self.testsuite   = self.loadConfig()
		self.completed   = []
		self.lastseen = str(datetime.now()).split('.')[0]
		self.template = os.path.join("service","html","template.html")
		self.html = None
		self.superreport = ""
		self.storagePrefix = ""
		self.reset()
		self.history = self.findPreviousRuns()

	"""
	Returns the percentage of completion of test cases per client.
	"""
	def progress(self):
		if len(self.testsuite) == 0:
			return 100;
		done =  math.floor((len(self.completed) / len(self.testsuite)) * 100)
		return done
	"""
	Send the next text case to be executed in order of rank.
	"""
	def sendTestCase(self):
		if self.progress() == 100:
			return "QuitAgent"
		test = self.testsuite[len(self.completed)]
		print "sending",test.name,"to",self.address
		timenow = str(datetime.now()).split('.')[0]
		self.lastseen = timenow
		test.starttime = timenow
		test.result = "Running"
		serialize = json.dumps(test, default=lambda o: o.__dict__)
		return serialize
	"""
	Receive the result of the last test case sent.
	"""
	def recieveResult(self, result, dependency=False):
		if (len(self.testsuite) > len(self.completed)):
			test = self.testsuite[len(self.completed)]
			if dependency:
				(test.result, test.console, test.details) = ("Pass", "Remaining commands in this TestCase ignored.", "")
			else:
				(test.result, test.console, test.details) = json.loads(result)
			print ("\nCompleted " + test.desc + " with result: " + test.console + " and evaluated " + test.result)
			timenow = str(datetime.now()).split('.')[0]
			test.endtime = timenow
			self.lastseen = timenow
			self.completed.append(test)
		else:
			print "discarding rogue result " + str(result)
	"""
	Receive the test log file.
	"""
	def recieveLog(self, ClientLog):
		unserialized = json.loads(ClientLog)
		timenow = str(datetime.now()).split('.')[0]
		self.storagePrefix = ('client-' + self.address + "-" + timenow).replace(":","-")
		logName = self.storagePrefix + ".log"
		self.html = os.path.join("service/storage/reports/", self.address, self.storagePrefix + ".html")
		logPath = os.path.join("service/storage/logs/" + self.address, logName)
		f = open(logPath, "w")
		f.write(unserialized)
		f.close()
		self.history = self.findPreviousRuns()
	"""
	Receive raw data to include in the report file.
	"""
	def recieveInfoToRaw(self, Info, rawtag, separator=":"):
		unserialized = json.loads(Info)
		report = SuperReport(rawtag ,rawtag, separator, unserialized)
		self.superreport = report.dataToBuffer(self.superreport, False)
	"""
	Receive data and format into table for the report file.
	"""
	def recieveInfoToFmt(self, Info, fmttag, separator=":"):
		unserialized = json.loads(Info)
		report = SuperReport(fmttag, fmttag, separator, unserialized)
		report.formatHtmlTable()
		self.superreport = report.dataToBuffer(self.superreport, True)
	"""
	Receive CPU information of the client.
	"""
	def recieveCpuInfo(self, CpuInfo):
		unserialized = json.loads(CpuInfo)
		report = CpuReport("__CPUINFOFMT__", "__CPUINFORAW__", ":", unserialized)
		report.formatHtmlTable()
		self.superreport = report.dataToBuffer(self.superreport, True)
		self.superreport = report.dataToBuffer(self.superreport, False)
	"""
	Reset the client information from the previous run if it exists.
	"""
	def reset(self):
		if not os.path.exists("service/storage/logs/" + self.address):
			os.makedirs("service/storage/logs/" + self.address)
		if not os.path.exists("service/storage/reports/" + self.address):
			os.makedirs("service/storage/reports/" + self.address)
		f = open(self.template)
		lines = f.readlines()
		self.superreport = "".join(lines)
		f.close()
	"""
	Repeat tests specified by a rank range.
	"""
	def repeatTests(self, fromrank, torank, times):
		startindex = 0
		stopindex = 0
		testsuitedup = self.loadConfig()
		for test in testsuitedup:
			if test.rank < fromrank:
				startindex +=1
		for test in testsuitedup:
			if test.rank <= torank:
				stopindex +=1
		repeatlist = []
		while times > 0:
			times = times - 1
			repeatlist.extend(copy.deepcopy(testsuitedup[startindex:stopindex]))

		self.testsuite.extend(repeatlist)
		result = json.dumps(("Pass", "Tests repeat added", "Repeating tests clears logs."))
		self.recieveResult(result)
	"""
	Skip test cases specified by ranks.
	"""
	def deleteTests(self, fromrank, torank):
		startindex = 0
		stopindex = 0
		for test in self.testsuite:
			if test.rank < fromrank:
				startindex +=1
		for test in self.testsuite:
			if test.rank <= torank:
				stopindex +=1
		for i in reversed(range(startindex, stopindex)):
			if (self.testsuite[i].result == "Pending"):
				print "deleting", self.testsuite[i].name
				del self.testsuite[i]

		result = json.dumps(("Pass", "Tests skipped", "Skipping tests clears log"))
		self.recieveResult(result)
	"""
	Load configuration file for specific client from disk.
	"""
	def loadConfig(self):
		for r in range(0,4):
			stars = ".*" * r
			fname = self.address.rsplit(".", r)[0] + stars + ".ini"
			if os.path.exists(os.path.join("config/profiles/", serverGlobalConfig['profile'], "clients", fname)):
				self.configPath = os.path.join("config/profiles/", serverGlobalConfig['profile'], "clients", fname)
				break
		print "Loading %s for client %s" %(self.configPath, self.address)
		if not self.configPath.startswith("config/profiles/" + serverGlobalConfig['profile'] + "/clients/" + self.address + ".ini"):
			shutil.copyfile(self.configPath, "config/profiles/" + serverGlobalConfig['profile'] + "/clients/" + self.address + ".ini")
			self.configPath = "config/profiles/" + serverGlobalConfig['profile'] +"/clients/" + self.address + ".ini"
		return TestCase.LoadFromDisk(self.configPath)
	"""
	Compute UUID for the client.
	"""
	@staticmethod
	def ComputeClientID(client):
		md5 = hashlib.md5()
		md5.update(client)
		return md5.hexdigest()
	"""
	Return the rank of the currently running test case.
	"""
	def GetCurrentTestRank(self):
		cur = 0
		# all test case finished, send 'infinity'
		if len(self.testsuite) == len(self.completed):
			cur = 10000
		# none completed, send 'minus infinity'
		elif len(self.completed) == 0:
			cur = -10000
		else :
			cur = self.testsuite[len(self.completed)].rank
		return cur

	"""
	Format test cases into a html output report.
	"""
	def recieveTestInfo(self):
		html = ""
		for test in self.testsuite:
			if test.result == "Pass":
				html += green_img
				html += """<td><img class="resultimg" id="passed"/></td><td class="label">%s</td><td style="background-color: #0f0">PASSED</td><td/>%s<td></test></tr>""" %(test.name, test.console)
			else:
				html += red_img
				html += """<td><img class="resultimg" id="failed"/></td><td class="label">%s</td><td style="background-color: #f00">FAILED</td><td/>%s<td></test></tr>""" %(test.name, test.console)
		return html
	"""
	End the processing for this client and generate report.
	"""
	def close(self):
		print "Closing client"
		testtable = self.recieveTestInfo()
		self.superreport = self.superreport.replace("__TESTSUITE__", testtable)
		self.superreport = self.superreport.replace("__IPADDR__", self.address)
		now = str(datetime.now()).split(".")[0]
		self.superreport = self.superreport.replace("__DATE__", now)
		SuperReport.dataToFile(self.superreport, self.html)

	"""
	"""
	def isZombie(self):
		zombieInterval = int(serverGlobalConfig['zombieInterval'])
		if len(self.completed) == len(self.testsuite):
			return False
		elif self.getTimeSinceLastSeen() > zombieInterval and self.testsuite[len(self.completed)].result == 'Pending':
			return True
		return False

	"""
	"""
	def findPreviousRuns(self):
		history = []
		if not os.path.exists("service/storage/logs"):
			return history
		logPath = "service/storage/logs/" + self.address
		files = [f for f in os.listdir(logPath) if os.path.isfile(os.path.join(logPath, f))]
		for f in files:
			with open(os.path.join(logPath, f)) as contents:
				runlog = contents.read()
				contents.close()
				passed = runlog.count('Sending response: Pass') 
				failed = runlog.count('Sending response: Fail')
				total = runlog.count('Sending response')
				timestamp = f.replace('client-' + self.address + '-', '').replace('.log', '')
				history.append({'passed': passed, 
					'failed': failed, 'total': total, 'timestamp': timestamp})
		return history
	"""
	"""
	def getTimeSinceLastSeen(self):
		now = datetime.now()
		lastseen = datetime.strptime(self.lastseen, '%Y-%m-%d %H:%M:%S')
		seconds = (now - lastseen).total_seconds()
		return seconds

	"""
	"""
	def updateConfigFile(self, configs):
		rank = 1
		cfgfile = open(self.configPath, 'w')
		for config in configs:
			cfgfile.write("[" + config['name'] + "]\n")
			cfgfile.write('rank = '+ str(rank) + "\n")
			cfgfile.write('desc = ' + config['desc'] + "\n")
			cfgfile.write("commands = [\n")
			for c in config['commands']:
				cfgfile.write('\t"' + c.encode('latin-1') + '",\n')
			cfgfile.write("\t]\n")
			cfgfile.write("\n\n")
			rank += 1
		cfgfile.close();
		
	"""
	Destructor of object.
	"""
	def __del__(self):
		pass
