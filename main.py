from flask import Flask
from flask import jsonify
from flask import request
import requests, json
from datetime import datetime


application = Flask(__name__)

neturl = '<< URL to your Netapp Ontap server on AWS>'
hdr = {'content-type': 'application/json'}
payload={'email':'<ontap admin user name>', 'password':'<ontap admin pwd>'}
r = requests.session()

def genSlackMsg(msg):
    smsg = {"text": msg, "icon_emoji": ":red_circle:"}
    return smsg

def notifySlack(msg):
    url="<Your Slack Web Hook URL Here>"
    payload=msg
    r = requests.post(url, data=json.dumps(payload))

@application.route("/")
def index():
    return "More TO come"

@application.route("/createvol", methods=['GET', 'POST'])
def createvols():
    r.post(neturl+'/auth/login', data=json.dumps(payload), headers=hdr )
    cvol={
      "workingEnvironmentId": "VsaWorkingEnvironment-cJq3ijaa",
      "svmName": "svm_NetappsVolumeSource",
      "aggregateName": "aggr1",
      "name": "test10gb",
      "size": {
        "size": "10",
        "unit": "GB"
      },
      "initialSize": {
        "size": "10",
        "unit": "GB"
      },
      "snapshotPolicyName": "default",
      "exportPolicyInfo": {
        "policyType": "custom",
        "ips": ["172.31.0.0/16"]
      },
  
      "securityStyle": "unix",
      "enableThinProvisioning": "false",
      "enableCompression": "false",
      "enableDeduplication": "false",
      "maxNumOfDisksApprovedToAdd": "1"
    }
    st = r.post(neturl+'/vsa/volumes',data=json.dumps(cvol), headers=hdr)
    tm = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    mess = "\n New Volume Created \n" + "Name:"+cvol["name"] +"\n Size: " +cvol["size"]["size"]+cvol["size"]["unit"]+"\n Create On: "+tm
    notifySlack(genSlackMsg(mess))

    #check the domain against the getdns stack
    return mess

@application.route("/getvols", methods=['GET', 'POST'])
def getvols():
    r.post(neturl+'/auth/login', data=json.dumps(payload), headers=hdr )
    gr = r.get(neturl+'/auth/current-user')
    u = gr.json()
    user = u['email']
    mess = "User: "+user+ " has logged into you OCCM Server: "+neturl
    notifySlack(genSlackMsg(mess))

    we = r.get(neturl+'/vsa/aggregates?workingEnvironmentId=VsaWorkingEnvironment-cJq3ijaa')
    wenv = we.json()
    for w in wenv:

        for v in w["volumes"]:
            mess = "Volumes: " + v["name"] +" is using:" + str(round(v["usedSize"]["size"]))+"GB of data"
            notifySlack(genSlackMsg(mess))

    return "/getvols function was run & reported to slack"

if __name__ == "__main__":
    application.debug = True 
    application.run(host='0.0.0.0')