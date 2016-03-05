import os
import sys
import json
import select
import thread
import urllib
from Colonize import Colonize
from flask import Flask, url_for, request
from ThinClient import javascript
from ThinClient import ThinClient
from ThinClient import KNOWN_CLIENTS

app = Flask("AutomationFramework")
app.debug = 1

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

@app.route('/reset', methods=['POST'])
def api_reset():
	(cid, data) = getPayload()
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
	return response


@app.route('/noreset', methods=['POST'])
def api_noreset():
	(cid, data) = getPayload()
	response = ContactClient(cid, "Associated")
	return response

@app.route('/fileupload/<filename>', methods=['POST'])
def api_fileupload(filename):
	(cid, data) = getPayload()
	print filename + " uploaded"
	response = ContactClient(cid, "OK")
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

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8080)
