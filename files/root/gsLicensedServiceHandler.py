import time 
import os
import sys
import json
from urllib import request
from urllib.error import HTTPError, URLError
import subprocess
import gsDebugPrint
gsdb = gsDebugPrint.gsDebugPrint("gsLicensedServiceHandler")

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

gsdb.gsDebugPrint(f'Licensed Service Handler will start in 35 seconds',1)
time.sleep(35)
gsdb.gsDebugPrint(f'liscensed Service Handler Started',1)

path_to_services = '/etc/init.d/'
path_to_proccesses = '/root/'
path_to_systemFlags = '/root/systemStateFlags'
path_to_provisionComplete = f'{path_to_systemFlags}/provisionComplete.txt'
path_to_liscensedSoftwareFile = f'{path_to_systemFlags}/liscensedSoftwareFile.txt'

bs_get_paid_software_url = 'http://gsadminserver.eastus.cloudapp.azure.com:8080/bs_get_paid_software.php'

#quick change for the column we want returned
awkPrint = "{ print $1,$4,$5,$6 }"

first_time_run = True
counter = 0

while(1):

    provisionCompletePathexists = os.path.exists(path_to_provisionComplete)

    if  provisionCompletePathexists:
        
        if first_time_run or counter == 5: # counter time is number *1 min
            # any bought workers/services - loaded from the "liscensedSoftwareFile.txt"
            gsLicensedWorkers = [] #not hard coded.
            gsLicensedServices = []

            with open('/root/systemStateFlags/uniqueID.txt', mode='r') as file:
                base_unique_id = file.read()
                file.close()
            data_dict={"base_unique_id" : base_unique_id}

            try:
                
                json_data_encoded = json.dumps(data_dict).encode('utf-8')
                req = request.Request(url=bs_get_paid_software_url)
                req.add_header('Content-Type', 'application/json; charset=utf-8')
                req.add_header('Content-Length', len(json_data_encoded))

                #step 1 , if allowed will get Org details and store to a file
                gsdb.gsDebugPrint("Doing a request.urlopen to get json object")
                response = request.urlopen(req, json_data_encoded) # MW - this can throw an exception that is not an HTTPError
                if response.getcode() == 200:
                    gsdb.gsDebugPrint("Code 200 recieved, checking if data is valid")
                    body = response.read().decode("utf-8")

                if body == "": #step 2 , error checking to see if file is blank
                        gsdb.gsDebugPrint("Something went wrong! the json object was blank, trying again",2)

                else:
                    bodyDict = json.loads(body)
                    gsdb.gsDebugPrint("Json object has data! checking if data is accurate")
                    gsdb.gsDebugPrint(f"json Object data = {body}")
                    
                    #stores liscensed software details
                    f = open(path_to_liscensedSoftwareFile, "w")
                    f.write(body)
                    f.close()

                    num_software = bodyDict["num_software"]
                    gsdb.gsDebugPrint(f"Number of liscensed software = {num_software}")

                    if num_software == 0:
                        gsdb.gsDebugPrint(f"You have not paid for any services")

                    else :
                        bodyDict.popitem() # gets rid of num_software as its not needed anymore
                        for key , value in bodyDict.items():
                            gsLicensedWorkers.append(f"{key}Worker")
                            gsLicensedServices.append(f"{key}Service")
                            first_time_run = False

                counter = 0           

            except (HTTPError, URLError, Exception) as err:
                gsdb.gsDebugPrint(f"Erroneous response: {err} - no connection to provisioning url",3)

        WorkersToStart=[]
        ServicesToStart=[]

        for (service,worker) in zip(gsLicensedServices , gsLicensedWorkers):
            try:
                tempWorker= worker
                tempService= service
                tempString = worker
                stat = subprocess.check_output(f"ps | grep {worker} |  awk '{awkPrint}' | grep -v grep | grep -v /bin/sh ", shell=True).decode().strip()#binary->str->get rid of \n
                stat_list = (stat.split(" "))

            except Exception as err:
                WorkersToStart.append(tempWorker)
                ServicesToStart.append(tempService)

        for (runWorker,RunService) in zip(WorkersToStart,ServicesToStart):
            try:
                completed_process = subprocess.CompletedProcess (subprocess.run([f"/etc/init.d/{RunService}","start"]),"-1")  

            except Exception as err:
                gsdb.gsDebugPrint(f"ERROR {err}." , 4)
                gsdb.gsDebugPrint(f"Failed to restart {RunService}",4)
        
        counter += 1
        time.sleep(60)
    
    else:
        gsdb.gsDebugPrint(f"Provision not complete. waiting 60 seconds to try again",2)
        time.sleep(60)

gsdb.gsDebugPrint(f"gsLiscensedServiceHandler has crashed",4)