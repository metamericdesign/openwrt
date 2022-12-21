import time
import os
import syslog  
import subprocess

syslog.syslog(f'Service Handler will start in 50 seconds')
time.sleep(50)

path_to_services = '/etc/init.d/'
path_to_proccesses = '/root/'

# all required workers for every base station
gsPreInstalledWorkers = ["gsHardwareOobWorker","gsProvisionWorker","gsOpenvpnWorker","gsGithubWorker"]

# any bought workers - loaded from the "software.txt"
gsLicensedWorkers = ["win_light"] #not hard coded.

#combines all current Workers 
gsWorkers = gsPreInstalledWorkers + gsLicensedWorkers
gsServices = ["gsHardwareOobService" , "gsProvisionService" , "gsOpenvpnService" , "gsGithubService" , "gsLightingService" ]
awkPrint = "{ print $1,$4,$5,$6 }"


while(1):
    WorkersToStart=[]
    ServicesToStart=[]
    for (service,worker) in zip(gsServices , gsWorkers):
        try:
            tempWorker= worker
            tempService= service
            print(f'workers = {worker}')
            tempString = worker
            stat = subprocess.check_output(f"ps | grep {worker} |  awk '{awkPrint}' | grep -v grep | grep -v /bin/sh ", shell=True).decode().strip()#binary->str->get rid of \n
            stat_list = (stat.split(" "))

            print(stat_list)
            print('-------------------------------------------------------')

        except Exception as err:
            print(f"ERROR {err} .The proccess ( {tempWorker} ) you are checking does not exist.")
            WorkersToStart.append(tempWorker)
            ServicesToStart.append(tempService)
            print('-------------------------------------------------------')


    print(WorkersToStart)
    print(ServicesToStart)
    for (runWorker,RunService) in zip(WorkersToStart,ServicesToStart):
        try:
            completed_process = subprocess.run([f"/etc/init.d/{RunService}","start"])
            print("I tried restarting")

        except Exception as err:
            print(f"ERROR {err}.")
            print(f"I Failed")
    
    time.sleep(15)

