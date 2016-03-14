import os
import pexpect
from ThinClient import serverGlobalConfig

class Schedule:
	def __init__(self, ip):
		self.ip = ip
		self.minute = "0"
		self.hour = "0"
		self.dayOfMonth = "*"
		self.month = "*"
		self.dayOfWeek = "*"

	def AddCronSchedule(self):
		croncmd = "echo " + self.ip + " " + serverGlobalConfig['username'] + " " + serverGlobalConfig['password'] + " " + serverGlobalConfig["installPath"] + " " + serverGlobalConfig["downloadUrl"] + " reset > /tmp/colonize"
		cronjob= str(self.minute) + " " + str(self.hour) + " " + self.dayOfMonth + " " + self.month + " " + self.dayOfWeek + " " + croncmd
		print cronjob
		print "( crontab -l | grep -v '" + croncmd + "' ; echo '" + cronjob + "' ) | crontab -"
		os.system("( crontab -l | grep -v '" + croncmd + "'; echo '" + cronjob + "' ) | crontab -");

	def RemoveCronSchedule(self):
		croncmd = "echo " + self.ip + " " + serverGlobalConfig['username'] + " " + serverGlobalConfig['password'] + " " + serverGlobalConfig["installPath"] + " " + serverGlobalConfig["downloadUrl"] + " reset > /tmp/colonize"
		os.system("( crontab -l | grep -v '" + croncmd + "' ) | crontab -")		
	
	@staticmethod
	def GetCronSchedules():
		schedules = []
		output = pexpect.run("crontab -l")
		lines = output.split('\n')
		for l in lines:
			fmt = l.split(' ')
			if len(fmt) == 14:
				schedules.append({'ip': fmt[6], 'hour': fmt[1], 'minute': fmt[0] })
		return schedules