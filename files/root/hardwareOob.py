import time
import os
import syslog 
import subprocess

oldFilesize = b'2000000'
resizeComplete = False
hibernationTime = 30

#all file path needed for checking
path_to_sd = '/dev/mmcblk0p1'
path_to_systemFlags = '/root/systemStateFlags'
path_to_oobCheck = f'{path_to_systemFlags}/oobCheck.txt'
path_to_uniqueID = f'{path_to_systemFlags}/uniqueID.txt'
path_to_fileResizeComplete = f'{path_to_systemFlags}/fileResizeComplete.txt'
path_to_hardwareOobComplete = f'{path_to_systemFlags}/hardwareOobComplete.txt'


time.sleep(3)

while(1):

    #bools need to be rechecked every loop
    uniqueID_path_exists = os.path.exists(path_to_uniqueID)
    sdPathExists = os.path.exists(path_to_sd)
    oobCheckPathExists = os.path.exists(path_to_oobCheck)
    fileResizeCompletePathExists = os.path.exists(path_to_fileResizeComplete)


    syslog.syslog(f'Starting oobCheck')
    syslog.syslog(f'sdPathExists = {sdPathExists}')
    syslog.syslog(f'oobCheckPathExists = {oobCheckPathExists}')

    #gets the mac adress of the device and saves it to a txt file
    if not uniqueID_path_exists:
            with open('/proc/device-tree/ethernet@1e100000/mac@0/mac-address', mode='rb') as file: # b is important -> binary
                macBytes = file.read()
                print(macBytes.hex())

            f = open(path_to_uniqueID, "w")
            f.write(macBytes.hex())
            f.close()

    #checks if a fileresize is need and if an sd card is inserted
    if sdPathExists and oobCheckPathExists and not fileResizeCompletePathExists: # step 1 checks if sd is connected and if a file resize is needed
        syslog.syslog(f'Starting file resize')

        os.system('rm /root/systemStateFlags/oobCheck.txt')

        os.system('./root/fileresize.sh')

        syslog.syslog(f'The file {path_to_oobCheck} and {path_to_sd} exists, rebooting')

        os.system('reboot')

    elif sdPathExists and not oobCheckPathExists and not fileResizeCompletePathExists:  #step 2 checks if file resize is complete and if so cleans up, if not factory resets device
        syslog.syslog(f'The file {path_to_sd} exists and {path_to_oobCheck} does not')
        syslog.syslog(f'checking if new file size is correct')
        newFilesize = subprocess.check_output("df | grep overlayfs:/overlay |  awk '{ print $4 }'", shell=True)

        #checks if filesize is greater then 2 GB, if not factory resets
        if newFilesize > oldFilesize:
            syslog.syslog(f'OOB check complete,new file size is correct -> {newFilesize}, deleting unneeded files')
            hibernationTime = 1800 #sets sleep timer longer as file is no longer needed for now

            #the reason 2 files get made here is in case another prccess gets added it can look for the fileResizeComplete.txt and the hardwareOobComplete.txt would get moved to the end

            #Creates file resize complete flag
            f = open(path_to_fileResizeComplete, "w") 
            f.write("file resize complete") 
            f.close()

            f = open(path_to_hardwareOobComplete, "w") 
            f.write("hardware oob check complete") 
            f.close()

            #os.system('rm /root/fileresize.sh')
            #os.system('rm /etc/init.d/runHardwareOobCheck')
            #os.system('rm /root/hardwareOob.py')
            #os.system('reboot')

        else :
            syslog.syslog(f'ERROR: something went wrong during fileresize. Factory resetting now')
            syslog.syslog(f' newFilesize = {newFilesize}')
            syslog.syslog(f' oldFilesize = {oldFilesize}')
            os.system('firstboot && reboot now')


    else:
    
        syslog.syslog(f'Nothing found,going to sleep')
        time.sleep(hibernationTime)

    
