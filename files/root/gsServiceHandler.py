import time
import os
import syslog  
import subprocess

syslog.syslog(f'Service Handler will start in 50 seconds')
time.sleep(50)

path_to_services = '/etc/init.d/'
path_to_proccesses = '/root/'

# all required workers/services for every base station
gsPreInstalledWorkers = ["gsHardwareOobWorker","gsProvisionWorker","gsOpenvpnWorker","gsGithubWorker"]
gsPreInstalledServices = ["gsHardwareOobService" , "gsProvisionService" , "gsOpenvpnService" , "gsGithubService"]

# any bought workers/services - loaded from the "software.txt"
gsLicensedWorkers = ["win_light"] #not hard coded.
gsLicensedServices = ["gsLightingService"]

#combines all current Workers\/services 
gsWorkersToCheck = gsPreInstalledWorkers + gsLicensedWorkers
gsServicesToCheck = gsPreInstalledServices + gsLicensedServices

#quick change for the column we want returned
awkPrint = "{ print $1,$4,$5,$6 }"


while(1):
    WorkersToStart=[]
    ServicesToStart=[]

    print(f"gsWorkers to check = {gsWorkersToCheck}")
    print(f"gsServices to check = {gsServicesToCheck}")
    for (service,worker) in zip(gsServicesToCheck , gsWorkersToCheck):
        try:
            tempWorker= worker
            tempService= service
            print(f'worker = {worker}')
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


    print(f"WorkersToStart = {WorkersToStart}")
    print(f"ServicesToStart = {WorkersToStart}")

    for (runWorker,RunService) in zip(WorkersToStart,ServicesToStart):
        try:
            completed_process = subprocess.run([f"/etc/init.d/{RunService}","start"])
            print(f"Tried restarting {RunService}")
            print(completed_process)
            print('=======================================================')

        except Exception as err:
            print(f"ERROR {err}.")
            print(f"Failed to restart {RunService}")
    
    time.sleep(15)

