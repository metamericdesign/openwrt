import time
import os
import syslog 
import subprocess

syslog.syslog(f'HardwareOOb will start in 3 seconds')
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
 
    syslog.syslog(f'Starting oobCheck')
    syslog.syslog(f'sdPathExists = {sdPathExists}')
    syslog.syslog(f'oobCheckPathExists = {oobCheckPathExists}')

    syslog.syslog(f' newFilesize = {newFilesize}')
    syslog.syslog(f' oldFilesize = {oldFilesize}')
    try :
        if int(newFilesize) < int(oldFilesize):
                    #generates a unique ID or skips it
            if not uniqueID_path_exists:
                syslog.syslog(f'uniqueID does not exist , adding now')
                with open('/proc/device-tree/ethernet@1e100000/mac@0/mac-address', mode='rb') as file: # b is important -> binary
                    macBytes = file.read()
                    print(macBytes.hex())

                f = open(path_to_uniqueID, "w")
                f.write(macBytes.hex())
                f.close()
            else:
                syslog.syslog(f'uniqueID already exists')

            if sdPathExists:

                if oobCheckPathExists: #step 1 , uses the file resize shell script and deletes OobFlag

                    syslog.syslog(f'Starting file resize')

                    os.system('rm /root/systemStateFlags/oobCheck.txt')

                    os.system('./root/fileresize.sh')

                    syslog.syslog(f'The file {path_to_oobCheck} and {path_to_sd} exists, rebooting')

                    os.system('reboot')

                    time.sleep(10) # this is needed otherwise device infinite boot loops

                else: #Step 2, factory rests device if fileresize fails
                    syslog.syslog(f'ERROR: something went wrong during fileresize. Factory resetting now')
                    syslog.syslog(f' newFilesize = {newFilesize}')
                    syslog.syslog(f' oldFilesize = {oldFilesize}')

                    os.system('echo y | firstboot && reboot now') # factory reset command

            else:
                syslog.syslog(f'No SD card detected for fileresize, retying in {hibernationTime} seconds')
                time.sleep(hibernationTime)
        else: #Step 3 , fileresize successful --> create new flags

            #Creates file resize complete flag
            if fileResizeCompletePathExists :
                syslog.syslog(f'{path_to_fileResizeComplete} already exists')

            else:
                syslog.syslog(f'{path_to_fileResizeComplete} does not exists , creating file.')
                f = open(path_to_fileResizeComplete, "w") 
                f.write("file resize complete") 
                f.close()

            #creates hardware oob complete flag
            if hardwareOobCompletePathExists:
                syslog.syslog(f'{path_to_hardwareOobComplete} already exists')

            else:
                syslog.syslog(f'{path_to_hardwareOobComplete} does not exists , creating file.')
                f = open(path_to_hardwareOobComplete, "w") 
                f.write("hardware oob check complete") 
                f.close()

            hibernationTime = 1800 #changes wait time upon successful run
            syslog.syslog(f'Hardware Oob has succesfully gone through all its proccesses')
            syslog.syslog(f'hardare Oob going to sleep for {hibernationTime} seconds')
            time.sleep(hibernationTime)

    except Exception as err:
           syslog.syslog("Hardware Oob CRASH")
           syslog.syslog(f"ERROR -> {err}")
           time.sleep(hibernationTime)

syslog.syslog(f'hardare Oob going to sleep for {hibernationTime} seconds')
time.sleep(hibernationTime)
