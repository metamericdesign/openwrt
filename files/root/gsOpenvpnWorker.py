import time 
import os
import syslog 
import json
import sys
from urllib import request
from urllib.error import HTTPError
import gsDebugPrint

gsdb = gsDebugPrint.gsDebugPrint("gsOpenvpnWorker")

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

#all files path needed for checking
path_to_systemFlags = '/root/systemStateFlags'
path_to_provisionComplete = f'{path_to_systemFlags}/provisionComplete.txt'
path_to_orgDetails = f'{path_to_systemFlags}/orgDetails.txt'
path_to_openvpnConfig = '/etc/config/openvpn'

path_to_openvpn = '/dummypath' #dummy path 
hibernationTime = 15

gsdb.gsDebugPrint('VPN worker starts in 30 seconds.')
time.sleep(30)

while(1):
    try:
        while(1):
            gsdb.gsDebugPrint(' VPN Loop Start')
            #makes file paths into booleans
            provisionCompletePathexists = os.path.exists(path_to_provisionComplete)
            openvpnPathexists = os.path.exists(path_to_openvpn)
            gsdb.gsDebugPrint(f'    provisionCompletePathexists = {provisionCompletePathexists}')
            gsdb.gsDebugPrint(f'    openvpnPathexists = {openvpnPathexists}')
            if (provisionCompletePathexists):
                gsdb.gsDebugPrint('  VPN Download Required.')
                try:
                    f = open(path_to_orgDetails, "r")
                    orgFileContents = f.read()
                    f.close()
                    gsdb.gsDebugPrint('   JSON file read.1')
                    gsdb.gsDebugPrint(orgFileContents)
                    try:
                        orgDetails = json.loads(orgFileContents)
                    except:
                        gsdb.gsDebugPrint(syslog.LOG_ERR,'JSON file error!')
                        break
                    gsdb.gsDebugPrint('   JSON file loaded.2') 
                    base_name = orgDetails["base_name"]
                    gsdb.gsDebugPrint(base_name)  
                    cloud_host = orgDetails["cloud_host"]
                    gsdb.gsDebugPrint(cloud_host)                    
                    openvpnUrl = f'http://{cloud_host}:8754/{base_name}.ovpn'
                    gsdb.gsDebugPrint(openvpnUrl)    
                    base_num=orgDetails["base_num"]
                    gsdb.gsDebugPrint(base_num) 
                    path_to_openvpn = f'/etc/openvpn/{base_name}.ovpn'                    
                    gsdb.gsDebugPrint('    Loading Unique ID...')
                    with open('/root/systemStateFlags/uniqueID.txt', mode='r') as file:
                            base_unique_id = file.read()
                    gsdb.gsDebugPrint('    Org details, Unique ID loaded.')
                    #checks provisioning url to see if the device is allowed
                    data_dict={"base_unique_id" : base_unique_id}
                    json_data_encoded = json.dumps(data_dict).encode('utf-8')        
                except:
                    gsdb.gsDebugPrint(syslog.LOG_ERR,'Org Detail assignment load error!')
                    break
                try:
                    # if allowed will get Org details and store to a file
                    gsdb.gsDebugPrint(openvpnUrl)
                    req = request.Request(url=openvpnUrl)
                   # req.add_header('Content-Type', 'application/json; charset=utf-8')
                   # req.add_header('Content-Length', len(json_data_encoded))
                    gsdb.gsDebugPrint('   Trying to download')
                    response = request.urlopen(req, json_data_encoded)
                    gsdb.gsDebugPrint('   response received.')
                    if response.getcode() == 200:
                        body = response.read().decode("utf-8")
                        print(body)
                        gsdb.gsDebugPrint(body)
                        gsdb.gsDebugPrint('   Download Success, configuring service.')
                        f = open(path_to_openvpn, "w")
                        f.write(body)
                        f.close()

                        os.system('/etc/init.d/openvpn stop')

                        f = open(path_to_openvpnConfig, "w")
                        f.write(f"config openvpn '{base_name}'")
                        f.write(f"\n\toption config '/etc/openvpn/{base_name}.ovpn'")
                        f.write(f"\n\toption enabled '1'")
                        f.close()
                        gsdb.gsDebugPrint('   Restarting openvpn.')
                        hibernationTime = 500
                        os.system('/etc/init.d/openvpn restart')
                    else:
                        gsdb.gsDebugPrint(syslog.LOG_ERR,'Download Failed.')
                        
                #if problem occurs or device not allowed errors out
                except:
                    gsdb.gsDebugPrint(f"Erroneous response: - no connection to provisioning url")
                    print(f"Erroneous response: - no connection to provisioning url")
            else:
                gsdb.gsDebugPrint(f'  VPN already setup. sleeping {hibernationTime}')
                time.sleep(hibernationTime)
            
            
            gsdb.gsDebugPrint(f' Loop End, sleeping {hibernationTime}')    
            time.sleep(hibernationTime)
    except:
        gsdb.gsDebugPrint(syslog.LOG_ERR,'Loop crash! Sleeping 30 mins.')
    gsdb.gsDebugPrint(f'Loop exit. sleeping {hibernationTime}')
    time.sleep(hibernationTime)    

gsdb.gsDebugPrint(syslog.LOG_ERR,'VPN Worker END.')