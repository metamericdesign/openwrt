import time 
import os
import syslog 
import json
from urllib import request
from urllib.error import HTTPError

#all file paths needed for checking
syslog.syslog('Provisioning Service Started, waiting 10 seconds.')
time.sleep(10)
hibernationTime = 30

path_to_systemFlags = '/root/systemStateFlags'
path_to_hardwareOobComplete = f'{path_to_systemFlags}/hardwareOobComplete.txt'
path_to_provisionComplete = f'{path_to_systemFlags}/provisionComplete.txt'
path_to_orgDetails = f'{path_to_systemFlags}/orgDetails.txt'

prov_url = 'http://gsvpn.eastus.cloudapp.azure.com/provision.php'

while(1):
        syslog.syslog(" Provisioning loop start.")
        try:
            hardwareOobCompletePathexists = os.path.exists(path_to_hardwareOobComplete)
            syslog.syslog(f' hardwareOobCompletePathexists = {hardwareOobCompletePathexists}')
            #only starts if file resize has occured
            if (hardwareOobCompletePathexists):
                provisionCompletePathexists = os.path.exists(path_to_provisionComplete)
                orgDetailsPathexists = os.path.exists(path_to_orgDetails)

                #only runs if base station has not been provisioned
                if (not provisionCompletePathexists):

                    syslog.syslog(" Starting Provisioning process")

                    #gets the unique ID stored on the device
                    with open('/root/systemStateFlags/uniqueID.txt', mode='r') as file:
                            base_unique_id = file.read()

                    #checks provisioning url to see if the device is allowed
                    data_dict={"base_unique_id" : base_unique_id}
                    try:
                        json_data_encoded = json.dumps(data_dict).encode('utf-8')
                        req = request.Request(url=prov_url)
                        req.add_header('Content-Type', 'application/json; charset=utf-8')
                        req.add_header('Content-Length', len(json_data_encoded))

                        # if allowed will get Org details and store to a file
                        response = request.urlopen(req, json_data_encoded)
                        if response.getcode() == 200:
                            body = response.read().decode("utf-8")
                            print(body)
                            syslog.syslog(body)

                            #TODO additional checks on data from server, test JSON
                            #checks if json object is blank
                            if body == "":
                                syslog.syslog("Something went wrong! the json object was blank, trying again")

                            else:
                                syslog.syslog("Json object has data! checking if data is valid")
                                test_key = body["gh_key"]

                                #tests the key pair values that should never be empty
                                if test_key !="":
                                    syslog.syslog("gh_key has a value")
                                    base_num = body["base_num"]

                                    if base_num !="":
                                        syslog.syslog("base_num has a value")
                                        syslog.syslog("saving data to org details and flagging provioning as complete")

                                        #stores org deatils
                                        f = open(path_to_orgDetails, "w")
                                        f.write(body)
                                        f.close()
                                        
                                        #flag for provisioning complete
                                        f = open(path_to_provisionComplete, "w")
                                        f.write("provision complete")
                                        f.close()
                                        syslog.syslog(" Provisioning Success.")
                                        hibernationTime = 1800

                                    else: 
                                            syslog.syslog("base_num is blank, bad data. Retrying")
                                else:
                                       syslog.syslog("gh_key is Blank, bad data. Retrying")

                    #if problem occurs or device not allowed errors out
                    except HTTPError as err:
                        syslog.syslog(f"Erroneous response: {err} - no connection to provisioning url")
                        print(f"Erroneous response: {err} - no connection to provisioning url")
                    syslog.syslog(" Sleep 20 seconds.")
                    time.sleep(20)
                else :
                    syslog.syslog(" Device alread provisioned")
                    time.sleep(hibernationTime)
            else:
                syslog.syslog(" Waiting on file system resize.")
                time.sleep(10)
        except:
            syslog.syslog("Provisioning Service Crash!")
            time.sleep(20)
        syslog.syslog(" Provisioning loop END. Wait 10 seconds.")
        time.sleep(10)
syslog.syslog(" Provisioning service exit.")

 #{"ovpn_url":"http:\/\/gsvpn.eastus.cloudapp.azure.com\/getovpn.php","base_name":"base_101","base_num":"1","base_system_id":"101","gh_key":"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"}