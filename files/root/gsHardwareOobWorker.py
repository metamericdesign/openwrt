import time
import sys
import os
import subprocess
import gsDebugPrint

gsdb = gsDebugPrint.gsDebugPrint("gsHardwareOobWorker")

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

gsdb.gsDebugPrint(f'HardwareOOb will start in 3 seconds' , 1)
time.sleep(3)

oldFilesize ='2000000'
hibernationTime = 15

#all file path needed for checking
path_to_sd = '/dev/mmcblk0p1'
path_to_systemFlags = '/root/systemStateFlags'
path_to_oobCheck = f'{path_to_systemFlags}/oobCheck.txt'
path_to_uniqueID = f'{path_to_systemFlags}/uniqueID.txt'
path_to_fileResizeComplete = f'{path_to_systemFlags}/fileResizeComplete.txt'
path_to_hardwareOobComplete = f'{path_to_systemFlags}/hardwareOobComplete.txt'

while(1):

    #bools need to be rechecked every loop
    uniqueID_path_exists = os.path.exists(path_to_uniqueID)
    sdPathExists = os.path.exists(path_to_sd)
    oobCheckPathExists = os.path.exists(path_to_oobCheck)
    fileResizeCompletePathExists = os.path.exists(path_to_fileResizeComplete)
    hardwareOobCompletePathExists = os.path.exists(path_to_hardwareOobComplete)

    newFilesize = subprocess.check_output("df | grep overlayfs:/overlay |  awk '{ print $4 }'", shell=True).decode().strip()#binary->str->get rid of \n
 
    gsdb.gsDebugPrint(f'Starting oobCheck',1)
    gsdb.gsDebugPrint(f'sdPathExists = {sdPathExists}')
    gsdb.gsDebugPrint(f'oobCheckPathExists = {oobCheckPathExists}')

    gsdb.gsDebugPrint(f' newFilesize = {newFilesize}')
    gsdb.gsDebugPrint(f' oldFilesize = {oldFilesize}')
    try :
        if int(newFilesize) < int(oldFilesize):
                    #generates a unique ID or skips it
            if not uniqueID_path_exists:
                gsdb.gsDebugPrint(f'uniqueID does not exist , adding now')
                with open('/proc/device-tree/ethernet@1e100000/mac@0/mac-address', mode='rb') as file: # b is important -> binary
                    macBytes = file.read()
                    print(macBytes.hex())

                f = open(path_to_uniqueID, "w")
                f.write(macBytes.hex())
                f.close()
            else:
                gsdb.gsDebugPrint(f'uniqueID already exists')

            if sdPathExists:

                if oobCheckPathExists: #step 1 , uses the file resize shell script and deletes OobFlag

                    gsdb.gsDebugPrint(f'Starting file resize')

                    os.system('rm /root/systemStateFlags/oobCheck.txt')

                    os.system('./root/fileresize.sh')

                    gsdb.gsDebugPrint(f'The file {path_to_oobCheck} and {path_to_sd} exists, rebooting')

                    os.system('reboot')

                    time.sleep(10) # this is needed otherwise device infinite boot loops

                else: #Step 2, factory rests device if fileresize fails
                    gsdb.gsDebugPrint(f'something went wrong during fileresize. Factory resetting now',4)
                    gsdb.gsDebugPrint(f' newFilesize = {newFilesize}')
                    gsdb.gsDebugPrint(f' oldFilesize = {oldFilesize}')

                    os.system('echo y | firstboot && reboot now') # factory reset command

            else:
                gsdb.gsDebugPrint(f'No SD card detected for fileresize, retying in {hibernationTime} seconds',3)
                time.sleep(hibernationTime)
        else: #Step 3 , fileresize successful --> create new flags

            #Creates file resize complete flag
            if fileResizeCompletePathExists :
                gsdb.gsDebugPrint(f'{path_to_fileResizeComplete} already exists')

            else:
                gsdb.gsDebugPrint(f'{path_to_fileResizeComplete} does not exists , creating file.')
                f = open(path_to_fileResizeComplete, "w") 
                f.write("file resize complete") 
                f.close()

            #creates hardware oob complete flag
            if hardwareOobCompletePathExists:
                gsdb.gsDebugPrint(f'{path_to_hardwareOobComplete} already exists')

            else:
                gsdb.gsDebugPrint(f'{path_to_hardwareOobComplete} does not exists , creating file.')
                f = open(path_to_hardwareOobComplete, "w") 
                f.write("hardware oob check complete") 
                f.close()

            hibernationTime = 1800 #changes wait time upon successful run
            gsdb.gsDebugPrint(f'Hardware Oob has succesfully gone through all its proccesses',1)
            gsdb.gsDebugPrint(f'hardare Oob going to sleep for {hibernationTime} seconds')
            time.sleep(hibernationTime)

    except Exception as err:
           gsdb.gsDebugPrint("Hardware Oob CRASH",3)
           gsdb.gsDebugPrint(f"ERROR -> {err}",3)
           time.sleep(hibernationTime)

gsdb.gsDebugPrint(f'hardare Oob going to sleep for {hibernationTime} seconds')
time.sleep(hibernationTime)
