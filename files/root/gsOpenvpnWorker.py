import time 
import os
import syslog 
import json
from urllib import request
from urllib.error import HTTPError
import gsDebugPrint

#all files path needed for checking
path_to_systemFlags = '/root/systemStateFlags'
path_to_provisionComplete = f'{path_to_systemFlags}/provisionComplete.txt'
path_to_orgDetails = f'{path_to_systemFlags}/orgDetails.txt'
path_to_openvpnConfig = '/etc/config/openvpn'

path_to_openvpn = '/dummypath' #dummy path 

syslog.syslog('VPN worker starts in 1000000 seconds.')
time.sleep(10)

while(1):
    try:
        while(1):
            syslog.syslog(' VPN Loop Start')
            #makes file paths into booleans
            provisionCompletePathexists = os.path.exists(path_to_provisionComplete)
            openvpnPathexists = os.path.exists(path_to_openvpn)
            syslog.syslog(f'    provisionCompletePathexists = {provisionCompletePathexists}')
            syslog.syslog(f'    openvpnPathexists = {openvpnPathexists}')
            if (provisionCompletePathexists and not openvpnPathexists):
                syslog.syslog('  VPN Download Required.')
                try:
                    f = open(path_to_orgDetails, "r")
                    orgFileContents = f.read()
                    f.close()
                    syslog.syslog('   JSON file read.1')
                    syslog.syslog(orgFileContents)
                    try:
                        orgDetails = json.loads(orgFileContents)
                    except:
                        syslog.syslog(syslog.LOG_ERR,'JSON file error!')
                        break
                    syslog.syslog('   JSON file loaded.2') 
                    base_name = orgDetails["base_name"]
                    syslog.syslog(base_name)  
                    cloud_host = orgDetails["cloud_host"]
                    syslog.syslog(cloud_host)                    
                    openvpnUrl = f'http://{cloud_host}:8754/{base_name}.ovpn'
                    syslog.syslog(openvpnUrl)    
                    base_num=orgDetails["base_num"]
                    syslog.syslog(base_num) 
                    path_to_openvpn = f'/etc/openvpn/{base_name}.ovpn'                    
                    syslog.syslog('    Loading Unique ID...')
                    with open('/root/systemStateFlags/uniqueID.txt', mode='r') as file:
                            base_unique_id = file.read()
                    syslog.syslog('    Org details, Unique ID loaded.')
                    #checks provisioning url to see if the device is allowed
                    data_dict={"base_unique_id" : base_unique_id}
                    json_data_encoded = json.dumps(data_dict).encode('utf-8')        
                except:
                    syslog.syslog(syslog.LOG_ERR,'Org Detail assignment load error!')
                    break
                try:
                    # if allowed will get Org details and store to a file
                    syslog.syslog(openvpnUrl)
                    req = request.Request(url=openvpnUrl)
                   # req.add_header('Content-Type', 'application/json; charset=utf-8')
                   # req.add_header('Content-Length', len(json_data_encoded))
                    syslog.syslog('   Trying to download')
                    response = request.urlopen(req, json_data_encoded)
                    syslog.syslog('   response received.')
                    if response.getcode() == 200:
                        body = response.read().decode("utf-8")
                        print(body)
                        syslog.syslog(body)
                        syslog.syslog('   Download Success, configuring service.')
                        f = open(path_to_openvpn, "w")
                        f.write(body)
                        f.close()

                        os.system('/etc/init.d/openvpn stop')

                        f = open(path_to_openvpnConfig, "w")
                        f.write(f"config openvpn '{base_name}'")
                        f.write(f"\n\toption config '/etc/openvpn/{base_name}.ovpn'")
                        f.write(f"\n\toption enabled '1'")
                        f.close()
                        syslog.syslog('   Restarting openvpn.')
                        os.system('/etc/init.d/openvpn restart')
                    else:
                        syslog.syslog(syslog.LOG_ERR,'Download Failed.')
                        
                #if problem occurs or device not allowed errors out
                except:
                    syslog.syslog(f"Erroneous response: - no connection to provisioning url")
                    print(f"Erroneous response: - no connection to provisioning url")
            else:
                syslog.syslog('  VPN already setup.')
                time.sleep(1800)
            
            
            syslog.syslog(' Loop End, sleeping 30 mins.')    
            time.sleep(1800)
    except:
        syslog.syslog(syslog.LOG_ERR,'Loop crash! Sleeping 30 mins.')
    syslog.syslog('Loop exit. Sleeping 2 mins.')
    time.sleep(1800)    

syslog.syslog(syslog.LOG_ERR,'VPN Worker END.')