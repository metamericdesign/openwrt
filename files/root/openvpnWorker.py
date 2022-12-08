import time 
import os
import syslog 
import json
from urllib import request
from urllib.error import HTTPError

hibernationTime = 15

#all files path needed for checking
path_to_systemFlags = '/root/systemStateFlags'
path_to_provisionComplete = f'{path_to_systemFlags}/provisionComplete.txt'
path_to_orgDetails = f'{path_to_systemFlags}/orgDetails.txt'
path_to_openvpnConfig = '/etc/config/openvpn'

path_to_openvpn = '/dummypath' #dummy path to test as false for first pass through

#makes file paths into booleans

time.sleep(15)

while(1):

    provisionCompletePathexists = os.path.exists(path_to_provisionComplete)
    openvpnPathexists = os.path.exists(path_to_openvpn)

    syslog.syslog(f'Github worker has started')
    syslog.syslog(f'Checking for provisionComplete')
    syslog.syslog(f'provisionCompletePathexists = {provisionCompletePathexists}')

    if (provisionCompletePathexists and not openvpnPathexists):

        f = open(path_to_orgDetails, "r")
        orgDetails = json.loads(f.read())
        f.close()

        openvpnUrl = orgDetails["ovpn_url"]


        base_num=orgDetails["base_num"]
        basestationName = f'base_{base_num}'
        path_to_openvpn = f'/etc/openvpn/{basestationName}.ovpn'


        with open('/root/systemStateFlags/uniqueID.txt', mode='r') as file:
                base_unique_id = file.read()

        #checks provisioning url to see if the device is allowed
        data_dict={"base_unique_id" : base_unique_id}
        json_data_encoded = json.dumps(data_dict).encode('utf-8')
        req = request.Request(url=openvpnUrl)
        req.add_header('Content-Type', 'application/json; charset=utf-8')
        req.add_header('Content-Length', len(json_data_encoded))

        try:
            # if allowed will get Org details and store to a file
            response = request.urlopen(req, json_data_encoded)
            if response.getcode() == 200:
                body = response.read().decode("utf-8")
                print(body)
                syslog.syslog(body)

                f = open(path_to_openvpn, "w")
                f.write(body)
                f.close()

                os.system('/etc/init.d/openvpn stop')

                f = open(path_to_openvpnConfig, "w")
                f.write(f"config openvpn '{basestationName}'")
                f.write(f"\n\toption config '/etc/openvpn/{basestationName}.ovpn'")
                f.write(f"\n\toption enabled '1'")
                f.close()

                os.system('/etc/init.d/openvpn restart')

                hibernationTime = 1800

         #if problem occurs or device not allowed errors out
        except HTTPError as err:
            syslog.syslog(f"Erroneous response: {err} - no connection to provisioning url")
            print(f"Erroneous response: {err} - no connection to provisioning url")

    time.sleep(hibernationTime)
