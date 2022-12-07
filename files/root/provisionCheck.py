from pathlib import Path
import time 
import os
import syslog 
import json
from urllib import request
from urllib.error import HTTPError

#all file paths needed for checking
path_to_hardwareOobComplete = '/root/systemStateFlags/hardwareOobComplete.txt'
hardwareOobCompletePath = Path(path_to_hardwareOobComplete)
hardwareOobCompletePathexists = os.path.exists(hardwareOobCompletePath)

path_to_provisionComplete = '/root/systemStateFlags/provisionComplete.txt'
provisionCompletePath = Path(path_to_provisionComplete)

path_to_orgDetails = '/root/systemStateFlags/orgDetails.txt'
orgDetailsPath = Path(path_to_orgDetails)

syslog.syslog(f'Checking for hardwareOobCompletePath')
syslog.syslog(f' hardwareOobCompletePathexists = {hardwareOobCompletePathexists}')

prov_url = 'http://gsvpn.eastus.cloudapp.azure.com/provision.php'

time.sleep(10)

while(1):

    hardwareOobCompletePathexists = os.path.exists(hardwareOobCompletePath)

    #only starts if file resize has occured
    if (hardwareOobCompletePathexists):
        provisionCompletePathexists = os.path.exists(provisionCompletePath)
        orgDetailsPathexists = os.path.exists(orgDetailsPath)

        #only runs if base station has not been provisioned
        if (not provisionCompletePathexists):

            syslog.syslog("Starting Provisioning process")

            #gets the unique ID stored on the device
            with open('/root/systemStateFlags/uniqueID.txt', mode='r') as file:
                    base_unique_id = file.read()

            #checks provisioning url to see if the device is allowed
            data_dict={"base_unique_id" : base_unique_id}
            json_data_encoded = json.dumps(data_dict).encode('utf-8')
            req = request.Request(url=prov_url)
            req.add_header('Content-Type', 'application/json; charset=utf-8')
            req.add_header('Content-Length', len(json_data_encoded))

            try:
                # if allowed will get Org details and store to a file
                response = request.urlopen(req, json_data_encoded)
                if response.getcode() == 200:
                    body = response.read().decode("utf-8")
                    print(body)
                    syslog.syslog(body)

                    #stores org deatils
                    f = open(orgDetailsPath, "w")
                    f.write(body)
                    f.close()
                    
                    #flag for provisioning complete
                    f = open(provisionCompletePath, "w")
                    f.write("provision complete")
                    f.close()

            #if problem occurs or device not allowed errors out
            except HTTPError as err:
                syslog.syslog(f"Erroneous response: {err} - no connection to provisioning url")
                print(f"Erroneous response: {err} - no connection to provisioning url")

            time.sleep(120)
        else :
            time.sleep(300)

    time.sleep(10)
