import time
import sys
import os
import subprocess
import gsDebugPrint

gsdb = gsDebugPrint.gsDebugPrint("gsNewFirmwareWorker")

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

gsdb.gsDebugPrint(f'gsNewFirmwareWorker will start in 60 seconds' , 1)
time.sleep(60)

path_to_newFirmware = '/tmp/newfirmware.bin'

while(1):

    newFirmware_path_exists = os.path.exists(path_to_newFirmware)

    if(newFirmware_path_exists):
    
        gsdb.gsDebugPrint(f'New Firmware found, doing sysupgrade in 5 seconds' , 1)
        time.sleep(5)
        os.system(f'sysupgrade -n {path_to_newFirmware}')
    
    else:
    
        time.sleep(30)
    
