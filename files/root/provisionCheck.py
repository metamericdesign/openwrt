import time 
import os
import syslog 
import json
from urllib import request
from urllib.error import HTTPError

hibernationTime = 15

#all file paths needed for checking
path_to_systemFlags = '/root/systemStateFlags'
path_to_hardwareOobComplete = f'{path_to_systemFlags}/hardwareOobComplete.txt'
path_to_provisionComplete = f'{path_to_systemFlags}/provisionComplete.txt'
path_to_orgDetails = f'{path_to_systemFlags}/orgDetails.txt'

prov_url = 'http://gsvpn.eastus.cloudapp.azure.com/provision.php'

time.sleep(10)

while(1):

    hardwareOobCompletePathExists = os.path.exists(path_to_hardwareOobComplete)

    syslog.syslog(f'Checking for hardwareOobComplete_path')
    syslog.syslog(f'hardwareOobCompletePathExists = {hardwareOobCompletePathExists}')

    #only starts if file resize has occured
    if (hardwareOobCompletePathExists):

        provisionCompletePathExists = os.path.exists(path_to_provisionComplete)
        orgDetails_pathexists = os.path.exists(path_to_orgDetails)

        #only runs if base station has not been provisioned
        if (not provisionCompletePathExists):

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
                    syslog.syslog(body)

                    #stores org deatils
                    f = open(path_to_orgDetails, "w")
                    f.write(body)
                    f.close()
                    
                    #flag for provisioning complete
                    f = open(path_to_provisionComplete, "w")
                    f.write("provision complete")
                    f.close()

                    hibernationTime = 1800 #sets longer wait if complete

            #if problem occurs or device not allowed errors out
            except HTTPError as err:
                syslog.syslog(f"Erroneous response: {err} - no connection to provisioning url")
                print(f"Erroneous response: {err} - no connection to provisioning url")

    time.sleep(hibernationTime)
