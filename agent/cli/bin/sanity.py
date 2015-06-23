from __future__ import division
from __future__ import unicode_literals
from __future__ import with_statement
import sys
import os
if os.path.exists("agent"):
	sys.path.append("agent")
	sys.path.append("agent/cli")
	sys.path.append("agent/cli/core")
	import array
	import ast
	import asyncore
	import atexit
	import base64
	import cmd
	import copy
	import errno
	import fcntl
	import ftplib
	import glob
	import hashlib
	import json
	import logging
	import math
	import os
	import platform
	from thirdparty.pexpect import pexpect
	from thirdparty.inotify import pyinotify
	import re
	import readline
	import select
	import shutil
	import signal
	import socket
	import string
	import StringIO
	import struct
	import subprocess
	import sys
	import tempfile
	import termios
	import threading
	import time
	import urllib2
	import warnings
	import zipfile
	from cli.core.Console import Console
	from cli.core.docopt import docopt
	from cli.core.ExecHelper import ExecHelper
	from cli.core import docopt
	from cli.core import ResultStore
	from cli import cliInterface
	from collections import deque
	from core import docopt
	from core.ResultStore import ResultStore
	from datetime import datetime, timedelta
	from os import listdir, sep
	from os.path import abspath, basename, isdir
	from os.path import realpath, islink
	from ResultStore import ResultStore
	from thirdparty import selenium
	from selenium.common.exceptions import ElementNotSelectableException
	from selenium.common.exceptions import ErrorInResponseException
	from selenium.common.exceptions import ImeActivationFailedException
	from selenium.common.exceptions import InvalidCookieDomainException
	from selenium.common.exceptions import InvalidSelectorException
	from selenium.common.exceptions import MoveTargetOutOfBoundsException
	from selenium.common.exceptions import NoAlertPresentException
	from selenium.common.exceptions import NoSuchElementException
	from selenium.common.exceptions import NoSuchElementException, UnexpectedTagNameException
	from selenium.common.exceptions import NoSuchFrameException
	from selenium.common.exceptions import NoSuchWindowException
	from selenium.common.exceptions import StaleElementReferenceException
	from selenium.common.exceptions import TimeoutException
	from selenium.common.exceptions import UnableToSetCookieException
	from selenium.common.exceptions import UnexpectedAlertPresentException
	from selenium.common.exceptions import WebDriverException
	from selenium import selenium
	from selenium import webdriver
	from selenium.webdriver.common.alert import Alert
	from selenium.webdriver.common.by import By
	from selenium.webdriver.common.by import By
	from selenium.webdriver.common.by import By
	from selenium.webdriver.common.by import By
	from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
	from selenium.webdriver.common.html5.application_cache import ApplicationCache
	from selenium.webdriver.common import utils
	from selenium.webdriver.common.keys import Keys
	from selenium.webdriver.common.proxy import ProxyType
	from selenium.webdriver.firefox.extension_connection import ExtensionConnection
	from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
	from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
	from selenium.webdriver.remote.command import Command
	from selenium.webdriver.remote.remote_connection import RemoteConnection
	from selenium.webdriver.remote.webdriver import WebDriver
	from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
	from selenium.webdriver.remote.webelement import WebElement
	from subprocess import PIPE
	from subprocess import Popen, STDOUT
	from sys import argv
	from time import sleep
	from xml.dom import minidom
if os.path.exists("service"):
	sys.path.append("service")
	import pexpect
	import SocketServer
	import ConfigParser
	import pxssh

import hashlib, os
import sys

#compute total hash = hash of every file in the directory
# Useful for third party tools that will not change.
def GetHashofDirDeep(directory):
	SHAhash = hashlib.sha1()
	if not os.path.exists (directory):
		return -1
	try:
		for root, dirs, files in os.walk(directory):
			for names in files:
				filepath = os.path.join(root,names)
				try:
					f1 = open(filepath, 'rb')
				except:
					# You can't open the file for some reason
					f1.close()
					continue

				while 1:
					# Read file in as little chunks
					buf = f1.read(4096)
					if not buf: break
					SHAhash.update(hashlib.sha1(buf).hexdigest())
        			f1.close()

  	except:
    		import traceback
    		# Print the stack traceback
    		traceback.print_exc()
    		return -2
	return SHAhash.hexdigest()

#Compute hash of filenames only, not the content.
# This hash changes only if some file is renamed or new file is added or deleted
def GetHashofDirShallow(directory):
	SHAhash = hashlib.sha1()
	if not os.path.exists (directory):
		return -1
	try:
		for root, dirs, files in os.walk(directory):
			for names in files:
				filepath = os.path.join(root,names)
				SHAhash.update(hashlib.sha1(filepath).hexdigest())

  	except:
    		import traceback
    		# Print the stack traceback
    		traceback.print_exc()
    		return -2
	return SHAhash.hexdigest()

if __name__=='__main__':
	#print GetHashofDirShallow("./service")  #this is how you get new checksum when source is changed.
	#print GetHashofDirDeep("./agent/selenium")  #this is how you get new checksum when source is changed.
	if os.path.exists("agent"):
		print "Checking agent install"
		if GetHashofDirDeep("./agent/thirdparty/selenium") == "167f809589652a03b296fd3a1c63e94ee8774ace":
			print "Selenium: Install seems good!"
		else:
			print "Selenium install missing? Try running again after make clean"
			sys.exit(-1)
		if os.getenv("DISPLAY") == None:
			print "DISPLAY environment not set, set it to :0 if running from an ssh shell"
			sys.exit(-1)
		if os.path.exists("/usr/bin/firefox") == False:
			print "Firefox missing in /usr/bin Browser module may tank, ignoring error"
		if os.path.exists("/usr/bin/xwininfo") == False:
			print "xwininfo missing in /usr/bin Browser module may tank, ignoring error"
		if os.path.exists("/usr/bin/xprop") == False:
			print "xprop missing in /usr/bin Browser module may tank, ignoring error"
		if os.path.exists("/usr/bin/awk") == False:
			print "awk missing in /usr/bin Some modules may tank, ignoring error"
		if os.system("which xte>/dev/null") != 0:
			print "xte missing in path Some modules may tank, ignoring error"
		if os.system("which visgrep>/dev/null") != 0:
			print "visgrep missing in path Some modules may tank, ignoring error"
		if os.system("which wmctrl>/dev/null") != 0:
			print "wmctrl missing in path Some modules may tank, ignoring error"

	if os.path.exists("service"):
		print "Checking server install"
		from SuperReport import *
		from TestCase import TestCase
		from ThinClient import ThinClient
		if GetHashofDirShallow("./service") == "f84032fa2bccc2a7db1e521ce0da65efd10884c0":
			print "Server: Install seems good!"
		else:
			print "Server: New file added of removed? update checksum or try again after make clean"
			sys.exit(-1)

	if os.path.exists("config"):
		print "Checking config"
		if GetHashofDirShallow("config") == "c5d1e007825fbd1754b1d949eb14890e3957916b":
			print "Config: Install seems good!"
		else:
			print "Are you using a custom name for config file? Ignoring checksum mismatch"
