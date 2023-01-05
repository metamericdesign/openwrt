import time
import sys
import subprocess
import gsDebugPrint

gsdb = gsDebugPrint.gsDebugPrint("gsServiceHandler")

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

gsdb.gsDebugPrint(f'Service Handler will start in 50 seconds',1)
time.sleep(5)

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
    gsdb.gsDebugPrint(f'Service Handler Started',1)
    WorkersToStart=[]
    ServicesToStart=[]

    gsdb.gsDebugPrint(f"gsWorkers to check = {gsWorkersToCheck}")
    gsdb.gsDebugPrint(f"gsServices to check = {gsServicesToCheck}")
    for (service,worker) in zip(gsServicesToCheck , gsWorkersToCheck):
        try:
            tempWorker= worker
            tempService= service
            gsdb.gsDebugPrint(f'worker = {worker}')
            tempString = worker
            stat = subprocess.check_output(f"ps | grep {worker} |  awk '{awkPrint}' | grep -v grep | grep -v /bin/sh ", shell=True).decode().strip()#binary->str->get rid of \n
            stat_list = (stat.split(" "))

            gsdb.gsDebugPrint(stat)
            gsdb.gsDebugPrint('-------------------------------------------------------')

        except Exception as err:
            gsdb.gsDebugPrint(f"ERROR {err} .The proccess ( {tempWorker} ) you are checking does not exist.",3)
            WorkersToStart.append(tempWorker)
            ServicesToStart.append(tempService)
            gsdb.gsDebugPrint('-------------------------------------------------------')


    gsdb.gsDebugPrint(f"WorkersToStart = {WorkersToStart}")
    gsdb.gsDebugPrint(f"ServicesToStart = {WorkersToStart}")

    for (runWorker,RunService) in zip(WorkersToStart,ServicesToStart):
        try:
            completed_process = subprocess.CompletedProcess (subprocess.run([f"/etc/init.d/{RunService}","start"]),"-1")  
            gsdb.gsDebugPrint(f"Tried restarting {RunService} Code: {completed_process.returncode}",1)
            gsdb.gsDebugPrint('=======================================================')

        except Exception as err:
            gsdb.gsDebugPrint(f"ERROR {err}." , 4)
            gsdb.gsDebugPrint(f"Failed to restart {RunService}",4)
    
    time.sleep(15)

