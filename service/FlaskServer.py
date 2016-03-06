import os
import sys
import json
import select
import thread
import urllib
from Colonize import Colonize
from flask import Flask, url_for, request, send_from_directory, redirect
from ThinClient import ThinClient
from ThinClient import KNOWN_CLIENTS

app = Flask("AutomationFramework")
app.debug = 1

#TODO: noreset

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
			description = {'ip': client.address, 'history': client.history ,'current': client.GetCurrentTestRank() ,'progress': client.progress()}
			response.append(description)
		configPath = "config"
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
				description = {'ip': client.address, 'history': client.history ,'current': 0 ,'progress': 0}
				response.append(description)
	else:
		response = {'ip': 'None', 'history':0, 'current':0 ,'progress':0 }
		for k in KNOWN_CLIENTS.keys():
			client = KNOWN_CLIENTS[k]
			if client.address.startswith(clientId.strip()):
				response = {'ip': client.address, 'history':client.history ,'current': client.GetCurrentTestRank() ,'progress': client.progress()}
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

# Helper methods
def getPayload():
	client = request.remote_addr
	cid = ThinClient.ComputeClientID(client)
	data = request.get_data()
	response = "";
	if cid not in KNOWN_CLIENTS.keys():
		print "Client %s assigned CID %s"%(client, cid)
		KNOWN_CLIENTS[cid] = ThinClient(client)
		#KNOWN_CLIENTS[cid].reset()
	elif cid in KNOWN_CLIENTS.keys():
		print "Resuming client from where it last left", client
	arg =json.loads(data)[2]
	return (cid, arg)

def ContactClient(cid, response):
	data = json.dumps((cid,response))
	return data

# Colonize thread
def AgentInstaller():
	if sys.platform.startswith("win32"):
		print "This platform does not support remote installer"
		return
	c = Colonize()
	while True:
		c.prepare()

if __name__ == '__main__':
	thread.start_new_thread( AgentInstaller, ())
	app.run(host='0.0.0.0', port=8080)
