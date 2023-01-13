import time 
import os
import sys
import json
from urllib import request
from urllib.error import HTTPError, URLError
import subprocess
import gsDebugPrint

gsdb = gsDebugPrint.gsDebugPrint("gsProvisionWorker")

if (len(sys.argv)) < 3: #if no arguments default to this
    gsdb.setPrintToTerminal(False)
    gsdb.setPrintToSysLog(True)

else:

    setPrintToTerminal = (sys.argv[1])
    setPrintToSysLog = (sys.argv[2])

    listOfTrue = ["1","True","true","yes","Yes","y","Y"]
    listOfFalse = ["0","False","false","no","No","n","N"]

    if setPrintToTerminal in listOfTrue:# if true set to true else set to false
        gsdb.setPrintToTerminal(True)
    else:
        gsdb.setPrintToTerminal(False)

    if setPrintToSysLog in listOfFalse: #if false set to false else set to true
        gsdb.setPrintToSysLog(False)
    else:
        gsdb.setPrintToSysLog(True)

#all file paths needed for checking
gsdb.gsDebugPrint('Provisioning Service Started, waiting 10 seconds.',1)
time.sleep(10)
hibernationTime = 15

error_verbosity_level=1

path_to_systemFlags = '/root/systemStateFlags'
path_to_hardwareOobComplete = f'{path_to_systemFlags}/hardwareOobComplete.txt'
path_to_provisionComplete = f'{path_to_systemFlags}/provisionComplete.txt'
path_to_orgDetails = f'{path_to_systemFlags}/orgDetails.txt'

prov_url = 'http://gsadminserver.eastus.cloudapp.azure.com:8080/provision.php'

def applyNetworkConfig(base_num, network_number):
    gsdb.gsDebugPrint('    Applying Network Number.')
    os.system(f'uci set network.lan.ipaddr="172.16.{base_num}.1"') # IP Address
    os.system('uci commit network')
    os.system(f'uci set system.@system[0].hostname="org{network_number}-base_{base_num}"') # HOSTNAME 
    os.system('uci commit system')
    os.system(f'uci add_list dhcp.@dnsmasq[0].address="/dbserver.lan/10.0.{network_number}.4"') # DATABASE CLOUD SERVER
    os.system('uci commit dhcp')

    # Restart services 
    gsdb.gsDebugPrint("    reloading system")
    os.system('/etc/init.d/system reload')
    gsdb.gsDebugPrint("    restarting dnsmasq")
    os.system('/etc/init.d/dnsmasq restart') 
    gsdb.gsDebugPrint("    restarting network, takes 10 seconds")
    os.system('/etc/init.d/network restart')
    


while(1):
        gsdb.gsDebugPrint(" Provisioning loop start.",1)
        try:
            hardwareOobCompletePathexists = os.path.exists(path_to_hardwareOobComplete)
            gsdb.gsDebugPrint(f' hardwareOobCompletePathexists = {hardwareOobCompletePathexists}')
            OrgDetailsPathExists = os.path.exists(path_to_orgDetails)
            #only starts if file resize has occured

            if hardwareOobCompletePathexists:

                gsdb.gsDebugPrint(" Starting Provisioning process")

                #gets the unique ID stored on the device
                with open('/root/systemStateFlags/uniqueID.txt', mode='r') as file:
                        base_unique_id = file.read()

                #checks provisioning url to see if the device is allowed
                data_dict={"base_unique_id" : base_unique_id , "error_verbosity_level": error_verbosity_level}

                try:
                    json_data_encoded = json.dumps(data_dict).encode('utf-8')
                    req = request.Request(url=prov_url)
                    req.add_header('Content-Type', 'application/json; charset=utf-8')
                    req.add_header('Content-Length', len(json_data_encoded))

                    #step 1 , if allowed will get Org details and store to a file
                    gsdb.gsDebugPrint("Doing a request.urlopen to get json object")
                    response = request.urlopen(req, json_data_encoded) # MW - this can throw an exception that is not an HTTPError
                    if response.getcode() == 200:
                        gsdb.gsDebugPrint("Code 200 recieved, checking if data is valid")
                        body = response.read().decode("utf-8")
                        
                        gsdb.gsDebugPrint(f"json Object data = {body}")

                        if body == "": #step 2 , error checking to see if file is blank
                            gsdb.gsDebugPrint("Something went wrong! the json object was blank, trying again",2)

                        else:
                            bodyDict = json.loads(body)
                            gsdb.gsDebugPrint("Json object has data! checking if data is accurate")

                            if error_verbosity_level == 1:
                                try:
                                    message = bodyDict["message"]
                                    gsdb.gsDebugPrint(message)
                                    gsdb.gsDebugPrint("trying again in 10 seconds")
                                    time.sleep(10)
                                    continue
                                except KeyError: # not doing anything here if device is fully provisioned and error_verbosity_level is set
                                    pass
                            else:
                                gsdb.gsDebugPrint("error_verbosity_level == 0 no message")

                            test_key = bodyDict["gh_key"]

                            #step 3 ,tests the key pair values that should never be empty
                            if test_key !="":
                                gsdb.gsDebugPrint("gh_key has a value")
                                base_num = bodyDict["base_num"]
                                org_network_number = bodyDict["org_network_num"]

                                if base_num !="": #Step 4, changes IP address to match base num
                                    # gets current IP adress
                                    ipv4_lan = subprocess.check_output("ifstatus lan |  jsonfilter -e '@[\"ipv4-address\"][0].address'", shell=True).decode().strip()#binary->str->get rid of \n
                                    gsdb.gsDebugPrint(f"Current ipv4 lan address = {ipv4_lan}")

                                    #creates what the theoretical ip address should be
                                    ipv4_lan_org_details = f"172.16.{base_num}.1"
                                    gsdb.gsDebugPrint(f"ipv4_lan_org_details = {ipv4_lan_org_details}")

                                    if ipv4_lan == ipv4_lan_org_details: #test old data to new data for IP address

                                        gsdb.gsDebugPrint(f"IP address is correct, sleeping {hibernationTime} seconds",1)
                                        time.sleep(hibernationTime)

                                    else:   #update IP address and hostname
                                        gsdb.gsDebugPrint(f"OLD IP address is incorrect , changing to new IP address and HOSTNAME")
                                        gsdb.gsDebugPrint(f"base_num has a value {base_num}")
                                        applyNetworkConfig(base_num,org_network_number)
                                        
                                        time.sleep(10) # needed for network restart to finish
                                        
                                        #gets actual lan ip address after network restart
                                        ipv4_lan = subprocess.check_output("ifstatus lan |  jsonfilter -e '@[\"ipv4-address\"][0].address'", shell=True).decode().strip()#binary->str->get rid of \n
                                        gsdb.gsDebugPrint(f"New ipv4 lan address = {ipv4_lan}")

                                        #creates what the theoretical ip address should be
                                        ipv4_lan_org_details = f"172.16.{base_num}.1"
                                        gsdb.gsDebugPrint(f"ipv4_lan_org_details = {ipv4_lan_org_details}")

                                        if ipv4_lan == ipv4_lan_org_details: #test old data to new data for IP address

                                            gsdb.gsDebugPrint(f"OLD IP address matches new IP address")
                                            gsdb.gsDebugPrint("saving data to org details and flagging provioning as complete",1)

                                            #stores org deatils
                                            f = open(path_to_orgDetails, "w")
                                            f.write(body)
                                            f.close()
                                            
                                            #flag for provisioning complete
                                            f = open(path_to_provisionComplete, "w")
                                            f.write("provision complete")
                                            f.close()
                                            gsdb.gsDebugPrint(" Provisioning Success.")
                                            hibernationTime = 1800

                                            gsdb.gsDebugPrint(f" Device provisioning complete. Wait {hibernationTime} seconds.")
                                            time.sleep(hibernationTime)

                                        else: #org details was gotten but the IP address change failed
                                            gsdb.gsDebugPrint(f"Org details exist but ipv4 is incorrect, attempting again in {hibernationTime}")
                                            gsdb.gsDebugPrint(f"ipv4_lan = {ipv4_lan}")
                                            gsdb.gsDebugPrint(f"ipv4_lan_org_details = {ipv4_lan_org_details}")
                                            time.sleep(hibernationTime)

                                else: 
                                        gsdb.gsDebugPrint(f"base_num is blank, bad data. Retrying in {hibernationTime}",2)
                                        time.sleep(hibernationTime)

                            else:
                                    gsdb.gsDebugPrint(f"gh_key is Blank, bad data. Retrying in {hibernationTime}",2)
                                    time.sleep(hibernationTime)

                    else:
                        gsdb.gsDebugPrint(f'Something went wrong -> {response.getcode()} code recieved',3)

                            #if problem occurs or device not allowed errors out

                except (HTTPError, URLError, Exception) as err:
                    gsdb.gsDebugPrint(f"Erroneous response: {err} - no connection to provisioning url",3)
                gsdb.gsDebugPrint(f" Sleep {hibernationTime} seconds.")
                time.sleep(hibernationTime)
        
            else:
                gsdb.gsDebugPrint(" Waiting on file system resize.",1)
                time.sleep(hibernationTime)
        except Exception as err:
           gsdb.gsDebugPrint("Provisioning Service Crash!",3)
           gsdb.gsDebugPrint(f"ERROR -> {err}",3)
           time.sleep(20)

gsdb.gsDebugPrint(f" Provisioning loop END. Wait 10 seconds.")
time.sleep(10)
