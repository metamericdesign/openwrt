import time 
import os
import syslog 
import json
from urllib import request
from urllib.error import HTTPError
import subprocess

#all file paths needed for checking
syslog.syslog('Provisioning Service Started, waiting 10 seconds.')
time.sleep(10)
hibernationTime = 15

path_to_systemFlags = '/root/systemStateFlags'
path_to_hardwareOobComplete = f'{path_to_systemFlags}/hardwareOobComplete.txt'
path_to_provisionComplete = f'{path_to_systemFlags}/provisionComplete.txt'
path_to_orgDetails = f'{path_to_systemFlags}/orgDetails.txt'

prov_url = 'http://gsadminserver.eastus.cloudapp.azure.com:8080/provision.php'

while(1):
        syslog.syslog(" Provisioning loop start.")
        try:
            hardwareOobCompletePathexists = os.path.exists(path_to_hardwareOobComplete)
            syslog.syslog(f' hardwareOobCompletePathexists = {hardwareOobCompletePathexists}')
            OrgDetailsPathExists = os.path.exists(path_to_orgDetails)
            #only starts if file resize has occured

            if hardwareOobCompletePathexists:

                if not OrgDetailsPathExists:

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

                        #step 1 , if allowed will get Org details and store to a file
                        response = request.urlopen(req, json_data_encoded)
                        if response.getcode() == 200:
                            body = response.read().decode("utf-8")
                            print(body)
                            syslog.syslog(body)

                            if body == "": #step 2 , error checking to see if file is blank
                                syslog.syslog("Something went wrong! the json object was blank, trying again")

                            else:
                                bodyDict = json.loads(body)
                                syslog.syslog("Json object has data! checking if data is valid")
                                test_key = bodyDict["gh_key"]

                                #step 3 ,tests the key pair values that should never be empty
                                if test_key !="":
                                    syslog.syslog("gh_key has a value")
                                    base_num = bodyDict["base_num"]

                                    if base_num !="": #Step 4, changes IP address to match base num
                                        syslog.syslog(f"base_num has a value {base_num}")
                                        syslog.syslog("changing ipv4 address")
                                        os.system(f'uci set network.lan.ipaddr="172.16.{base_num}.1"')
                                        os.system('uci commit network')
                                        os.system('/etc/init.d/network restart')
                                        time.sleep(10)# needed for network restart to finish
                                        
                                        #gets actual lan ip address after network restart
                                        ipv4_lan = subprocess.check_output("ifstatus lan |  jsonfilter -e '@[\"ipv4-address\"][0].address'", shell=True).decode().strip()#binary->str->get rid of \n
                                        syslog.syslog(f"New ipv4 lan address = {ipv4_lan}")

                                        #creates what the theoretical ip adress should be
                                        ipv4_lan_org_details = f"172.16.{base_num}.1"
                                        syslog.syslog(f"ipv4_lan_org_details = {ipv4_lan_org_details}")

                                        if ipv4_lan == ipv4_lan_org_details: #tests the actaul ip adress against the theoretical ip adress to see if it worked properly
                                    
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

                                            syslog.syslog(f" Device provisioning complete. Wait {hibernationTime} seconds.")
                                            time.sleep(hibernationTime)

                                        else: #org details was gotten but the IP adress change failed
                                            syslog.syslog(f"Org details exist but ipv4 is incorrect, attempting again in {hibernationTime}")
                                            syslog.syslog(f"ipv4_lan = {ipv4_lan}")
                                            syslog.syslog(f"ipv4_lan_org_details = {ipv4_lan_org_details}")
                                            time.sleep(hibernationTime)

                                    else: 
                                            syslog.syslog(f"base_num is blank, bad data. Retrying in {hibernationTime}")
                                            time.sleep(hibernationTime)

                                else:
                                        syslog.syslog(f"gh_key is Blank, bad data. Retrying in {hibernationTime}")
                                        time.sleep(hibernationTime)

                        else:
                            syslog.syslog(f'Something went wrong -> {response.getcode()} code recieved')

                            #if problem occurs or device not allowed errors out
                    except HTTPError as err:
                        syslog.syslog(f"Erroneous response: {err} - no connection to provisioning url")
                        print(f"Erroneous response: {err} - no connection to provisioning url")
                    syslog.syslog(f" Sleep {hibernationTime} seconds.")
                    time.sleep(hibernationTime)

                else :
                    #Step 5, next run through after a succesful run to check the changes are still up to date
                    hibernationTime = 15
                    ipv4_lan = subprocess.check_output("ifstatus lan |  jsonfilter -e '@[\"ipv4-address\"][0].address'", shell=True).decode().strip()#binary->str->get rid of \n

                    f = open(path_to_orgDetails, "r")
                    base_num = json.loads(f.read())["base_num"]
                    f.close()

                    ipv4_lan_org_details = f"172.16.{base_num}.1"
                    syslog.syslog(f"ipv4_lan = {ipv4_lan}")
                    syslog.syslog(f"ipv4_lan_org_details = {ipv4_lan_org_details}")

                    if ipv4_lan == ipv4_lan_org_details:#if succeeds everything is working, sleep
                        hibernationTime = 1800
                        syslog.syslog(f" Device already provisioned. Waiting {hibernationTime} seconds to test again.")
                        time.sleep(hibernationTime)

                    else: #if fail, delete flags and start over
                        syslog.syslog(f"Org details exists but ipv4 is incorrect,deleting Org details and tring again in {hibernationTime}")
                        os.system(f'rm {path_to_orgDetails}')
                        os.system(f'rm {path_to_provisionComplete}')
                        time.sleep(hibernationTime)
            
            else:
                syslog.syslog(" Waiting on file system resize.")
                time.sleep(hibernationTime)
        except Exception as err:
           syslog.syslog("Provisioning Service Crash!")
           syslog.syslog(f"ERROR -> {err}")
           time.sleep(20)

syslog.syslog(f" Provisioning loop END. Wait 10 seconds.")
time.sleep(10)
