# -*- coding: UTF-8 -*-
import os
import re
import sys
import json
import select
import thread
import urllib
import shutil
from Colonize import Colonize
from flask import Flask, url_for, request, send_from_directory, redirect
from ThinClient import ThinClient
from Schedule import Schedule
from ThinClient import KNOWN_CLIENTS
from Colonize import REMOTE_CLIENTS_EVENTS
from ThinClient import serverGlobalConfig
from TestCase import TestCase
import ConfigParser

app = Flask("AutomationFramework")
app.debug = 1

# Simple rule for static html files
@app.route('/')
def root():
	return redirect("/html/index.html", code=302)

@app.route('/js/<path:path>')
def send_js(path):
	return send_from_directory('service/js', path)

@app.route('/fonts/<path:path>')
def send_fonts(path):
	return send_from_directory('service/assets', path)

@app.route('/html/<path:path>')
def send_html(path):
	return send_from_directory('service/html', path)

@app.route('/css/<path:path>')
def send_css(path):
	return send_from_directory('service/css', path)

@app.route('/assets/<path:path>')
def send_assets(path):
	return send_from_directory('service/assets', path)

@app.route('/reports/<path:path>')
def send_reports(path):
	return send_from_directory('service/storage/reports', path)

@app.route('/logs/<path:path>')
def send_logs(path):
	return send_from_directory('service/storage/logs', path)

@app.route('/packages/<path:path>')
def send_packages(path):
	return send_from_directory('service/release', path)

# Built-in commands of AutomationFramework
@app.route('/result', methods=['POST'])
def api_result():
	(cid, data) = getPayload()
	KNOWN_CLIENTS[cid].recieveResult(data)
	response = ContactClient(cid, "OK")
	return response

@app.route('/gettest', methods=['POST'])
def api_gettest():
	(cid, data) = getPayload()
	testcase = KNOWN_CLIENTS[cid].sendTestCase()
	response = ContactClient(cid, testcase)
	return response

@app.route('/reset/<isReset>', methods=['POST'])
def api_reset(isReset):
	(cid, data) = getPayload()
	if(isReset == 'yes'):
		c = ""
		retVal, rankarg, console = json.loads(data)
		if rankarg:
			c, fromrank, torank, times = rankarg
		if not rankarg:
			KNOWN_CLIENTS[cid].reset()
			response = ContactClient(cid, "OK")
			del KNOWN_CLIENTS[cid]
		elif c in ["Repeat"]:
			KNOWN_CLIENTS[cid].repeatTests(int(fromrank), int(torank), int(times))
			response = ContactClient(cid, "OK")
		elif c in ["Skip"]:
			KNOWN_CLIENTS[cid].deleteTests(int(fromrank), int(torank))
			response = ContactClient(cid, "OK")
	else:
		response = ContactClient(cid, "Associated")
	return response

@app.route('/fileupload/<filename>', methods=['POST'])
def api_fileupload(filename):
	(cid, data) = getPayload()
	if filename == 'cpuinfo':
		KNOWN_CLIENTS[cid].recieveCpuInfo(data)
	elif filename == 'osinfo':
		KNOWN_CLIENTS[cid].recieveInfoToFmt(data, "__osinfo__", "=")
	elif filename == 'pkginfo':
		KNOWN_CLIENTS[cid].recieveInfoToFmt(data, "__pkginfo__", "-")
	elif filename == 'runlog.txt':
		KNOWN_CLIENTS[cid].recieveLog(data)
	else:
		section = "__" + filename + "__"
		KNOWN_CLIENTS[cid].recieveInfoToRaw(data, section)
	response = ContactClient(cid, "UPLOADED")
	return response

@app.route('/quitting', methods=['POST'])
def api_quitting():
	(cid, data) = getPayload()
	KNOWN_CLIENTS[cid].close()
	response = ContactClient(cid, "OK")
	return response

@app.route('/depcheck', methods=['POST'])
def api_depcheck():
	(cid, data) = getPayload()
	retVal, deparg, console = json.loads(data)
	depip,deprank = deparg
	depcid = ThinClient.ComputeClientID(depip)
	response = ""
	if depcid in KNOWN_CLIENTS.keys() and KNOWN_CLIENTS[depcid].GetCurrentTestRank() > int(deprank):
		KNOWN_CLIENTS[cid].recieveResult(arg, True)
		response = ContactClient(cid, "OK")
	else:
		print "client %s will wait for client %s" % (client, depip)
		response = ContactClient(cid, "WAITON")
	return response

# API methods
@app.route('/api/clients', methods=['GET'])
def api_getClient():
	clientId = request.args.get('ip', None)
	response = []
	if(clientId == None):
		for k in KNOWN_CLIENTS.keys():
			client = KNOWN_CLIENTS[k]
			description = {'ip': client.address, 'history': client.history ,'current': client.GetCurrentTestRank() ,'progress': client.progress(), 'abort': client.abort}
			response.append(description)
		configPath = "config/profiles/" + serverGlobalConfig['profile'] +"/clients/"
		files = [f for f in os.listdir(configPath) if os.path.isfile(os.path.join(configPath, f))]
		for f in files:
			if 'default.ini' in f:
				continue
			found = False
			for r in response:
				if r['ip']  in f:
					found = True
			if found == False:
				ip = f.replace('.ini', '')
				cid = ThinClient.ComputeClientID(ip)
				client = ThinClient(ip)
				KNOWN_CLIENTS[cid] = client
				description = {'ip': client.address, 'history': client.history ,'current': 0 ,'progress': 0, 'abort': client.abort}
				response.append(description)
	else:
		response = {'ip': 'None', 'history':0, 'current':0 ,'progress':0, 'abort': False }
		for k in KNOWN_CLIENTS.keys():
			client = KNOWN_CLIENTS[k]
			if client.address.startswith(clientId.strip()):
				response = {'ip': client.address, 'history':client.history ,'current': client.GetCurrentTestRank() ,'progress': client.progress(), 'abort': client.abort}
				break
	return json.dumps(response)

@app.route('/api/clients', methods=['POST'])
def api_addClient():
	client = request.json
	cid = ThinClient.ComputeClientID(client['ip'])
	c = None
	if cid not in KNOWN_CLIENTS.keys():
		KNOWN_CLIENTS[cid] = ThinClient(client['ip'])
		c = KNOWN_CLIENTS[cid]
		response = {'ip': c.address, 'history': c.history ,'current': c.GetCurrentTestRank() ,'progress': c.progress()}
	else:
		response = {}
	return json.dumps(response)

@app.route('/api/tests', methods=['GET'])
def api_getTests():
	clientId = request.args.get('ip', None)
	response = []
	if (clientId == None):
		bank = TestCase.LoadFromDisk("config/profiles/" + serverGlobalConfig['profile'] + "/tests/testbank.ini")
	else:
		bank = TestCase.LoadFromDisk("config/profiles/" + serverGlobalConfig['profile'] + "/clients/" + clientId + ".ini")
	for t in bank:
		response.append(t.toJSON())
	return json.dumps(response)

@app.route('/api/tests', methods=['PUT'])
def api_updateTests():
	data = request.json
	response = {'message': 'Updated the config'}
	cid = ThinClient.ComputeClientID(data['ip'])
	if cid not in KNOWN_CLIENTS.keys():
		KNOWN_CLIENTS[cid] = ThinClient(data['ip'])
	client = KNOWN_CLIENTS[cid]
	configs = json.loads(data['config'])
	client.updateConfigFile(configs)
	return json.dumps(response)

@app.route('/api/clients', methods=['PUT'])
def api_launch():
	data = request.json
	ip = data['ip']
	response = {'message': 'Launched ' + ip}
	serverConfig = LoadServerConfig()
	sshaction = ip + " " + serverConfig['username'] + " " + serverConfig['password'] + " " + serverConfig["installPath"] + " " + serverConfig["downloadUrl"] + " reset\n"
	with open("/tmp/colonize", "w") as f:
		f.write(sshaction)
		f.close()
	return json.dumps(response)

@app.route('/api/clients', methods=['DELETE'])
def api_abort():
	ip = request.args.get('ip', None)
	cid = ThinClient.ComputeClientID(ip)
	if cid in KNOWN_CLIENTS.keys():
		client = KNOWN_CLIENTS[cid]
		client.abort = True
	response = {'message': 'Aborted ' + ip}
	return json.dumps(response)


@app.route('/api/server', methods=['GET'])
def api_getServerLogs():
	response = ""
	if os.path.exists("service/storage/logs/serverlog.txt"):
		with open("service/storage/logs/serverlog.txt") as f:
			response = f.readlines()
	return json.dumps(response)

@app.route('/api/stats', methods=['GET'])
def api_getStats():
	ip = request.args.get('ip', None)
	cid = ThinClient.ComputeClientID(ip)
	response = {}
	client = KNOWN_CLIENTS[cid]
	response['progress'] = client.progress()
	response['testoutput'] = []
	for test in client.testsuite:
		output =  {'name': test.name, 'desc': test.desc, 'commands': "\n".join(test.commands), 'starttime': test.starttime,'endtime': test.endtime, 'console': test.console, 'result': test.result }
		response['testoutput'].append(output)
	return json.dumps(response)

@app.route('/api/manage', methods=['GET', 'POST'])
def api_manageConfiguration():
	response = ""
	if request.method == 'GET':
		print os.system('tar zcf service/assets/backup.tgz config')
		response = {'url': "/assets/backup.tgz", 'message': 'Download file'}
	else:
		data = request.files['file'].read()
		with open('service/assets/backup.tgz', 'wb') as f:
			f.write(data)
			f.close()
		os.system("tar zxf service/assets/backup.tgz")
		response = {'url': "/assets/backup.tgz", 'message': 'Uploaded file'}
	return json.dumps(response)

@app.route('/api/settings', methods=['GET', 'PUT'])
def api_manageSettings():
	response = None
	if request.method == 'GET':
		response = LoadServerConfig()
	else:
		config = request.json
		response = config
		config.pop('profileMessage')
		cfgfile = open("config/server/server.ini", 'w')
		cfgfile.write("[Server]\n")
		for cfg in config.keys():
			cfgfile.write(cfg + ' = ' + config[cfg] + "\n")
		cfgfile.write("\n\n")
		cfgfile.close();
		if not os.path.exists('config/profiles/' + config['profile']):
			shutil.copytree('config/profiles/root', 'config/profiles/' + config['profile'])
		LoadServerConfig()
	d = "config/profiles"
	profiles = [os.path.join(d,o) for o in os.listdir(d) if os.path.isdir(os.path.join(d,o))]
	response['profileMessage'] = ""
	for p in profiles:
		response['profileMessage'] += p.replace("config/profiles/", " ")
	return json.dumps(response) 

@app.route('/api/remoteInstaller', methods=['GET'])
def api_getRemoteInstallerEvents():
	response = {}
	response['clients'] = REMOTE_CLIENTS_EVENTS
	response['schedules'] = Schedule.GetCronSchedules()
	return json.dumps(response)

@app.route('/api/remoteInstaller', methods=['POST'])
def api_addRemoteInstallerSchedule():
	response = {}
	payload = request.json
	schedule = Schedule(payload['ip'])
	schedule.minute = payload['minute']
	schedule.hour = payload['hour']
	schedule.AddCronSchedule()
	response['clients'] = REMOTE_CLIENTS_EVENTS
	response['schedules'] = Schedule.GetCronSchedules()
	return json.dumps(response)

@app.route('/api/remoteInstaller', methods=['DELETE'])
def api_removeRemoteInstallerSchedule():
	response = {}
	ip = request.args.get('ip', '')
	hour = request.args.get('hour', '')
	minute = request.args.get('minute', '')
	schedule = Schedule(ip)
	schedule.minute = minute
	schedule.hour = hour
	schedule.RemoveCronSchedule()
	response['clients'] = REMOTE_CLIENTS_EVENTS
	response['schedules'] = Schedule.GetCronSchedules()
	return json.dumps(response)

@app.route('/api/patterns', methods=['GET'])
def api_patterns():
	response = {}
	path = "service/storage/logs/"
	ips = os.listdir(path)
	for library in ips:
		if not os.path.isdir( os.path.join(path, library)):
			continue
		response[library] = {}
		books = os.listdir(os.path.join(path, library))
		for book in books:
			file = os.path.join(path, library, book)
			text = open(file, "r")
			for line in text:
				if re.match("(.*)(AF:->)(.*)", line):
					testSummary = line.split(':->')
					plainName = testSummary[1].strip()
					if plainName not in response.keys():
						response[library] [plainName] = {'Pass': 0, 'Fail':0, 'Misc': 0}
					if (testSummary[2].strip() == 'Pass'):
						response[library][ plainName ]['Pass'] = response[library][plainName]['Pass'] + 1
					elif (testSummary[2].strip() == 'Fail'):
						response[library][ plainName ]['Fail'] = response[library][plainName]['Fail'] + 1
					else:
						response[library][ plainName ]['Misc'] = response[library][plainName]['Misc'] + 1
			text.close()
	return json.dumps(response)

# Helper methods
def getPayload():
	client = request.remote_addr
	cid = ThinClient.ComputeClientID(client)
	data = request.get_data()
	response = "";
	if cid not in KNOWN_CLIENTS.keys():
		print "Client %s assigned CID %s"%(client, cid)
		KNOWN_CLIENTS[cid] = ThinClient(client)
	elif cid in KNOWN_CLIENTS.keys():
		pass
	arg = json.loads(data)[2]
	return (cid, arg)

def ContactClient(cid, response):
	data = json.dumps((cid,response))
	return data


"""
Load test case configuration from disk. Called by thinclient method.
"""    
def LoadServerConfig():
	filename = "config/server/server.ini"
	config = ConfigParser.ConfigParser()
	config.read(filename)
	for c in config.sections():
		serverGlobalConfig['port'] = config.get(c , "port")
		serverGlobalConfig['downloadUrl'] = config.get(c , "downloadUrl")
		serverGlobalConfig['username'] = config.get(c , "username")
		serverGlobalConfig['password'] = config.get(c , "password")
		serverGlobalConfig['installPath'] = config.get(c , "installPath")        
		serverGlobalConfig['zombieInterval'] = config.get(c , "zombieInterval")        
		serverGlobalConfig['profile'] = config.get(c , "profile")        
	return serverGlobalConfig

# Colonize thread
def AgentInstaller():
	if sys.platform.startswith("win32"):
		print "This platform does not support remote installer"
		return
	c = Colonize()
	while True:
		c.prepare()

if __name__ == '__main__':
	LoadServerConfig()
	port = int(serverGlobalConfig['port'])
	thread.start_new_thread( AgentInstaller, ())
	app.run(host='0.0.0.0', port=port, threaded=True)
