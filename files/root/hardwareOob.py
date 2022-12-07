from pathlib import Path
import time
import os
import syslog 
import subprocess

oldFilesize = b'2000000'

#all file path needed for checking
path_to_sd = '/dev/mmcblk0p1'
path_to_oobCheck = '/root/systemStateFlags/oobCheck.txt'
path_to_uniqueID = '/root/systemStateFlags/uniqueID.txt'

time.sleep(3)

while(1):

    resizeComplete = False
    uniqueIDPathexists = os.path.exists(path_to_uniqueID)

    sdPath = Path(path_to_sd)
    oobPath = Path(path_to_oobCheck)

    sdPathexists = os.path.exists(sdPath)
    oobPathexists = os.path.exists(oobPath)

    syslog.syslog(f'Starting oobCheck')
    syslog.syslog(f' sdPathexists = {sdPathexists}')
    syslog.syslog(f' oobPathexists = {oobPathexists}')

    #gets the mac adress of the device and saves it to a txt file
    if not uniqueIDPathexists:
            with open('/proc/device-tree/ethernet@1e100000/mac@0/mac-address', mode='rb') as file: # b is important -> binary
                macBytes = file.read()
                print(macBytes.hex())

            f = open(path_to_uniqueID, "w")
            f.write(macBytes.hex())
            f.close()

    #checks if a fileresize is need and if an sd card is inserted
    if sdPathexists and oobPathexists: # step 1 checks if sd is connected and if a file resize is needed
        syslog.syslog(f'Starting file resize')

        os.system('rm /root/systemStateFlags/oobCheck.txt')

        os.system('./root/fileresize.sh')

        syslog.syslog(f'The file {oobPath} and {sdPathexists} exists, rebooting')

        os.system('reboot')

    elif sdPathexists and not oobPathexists and not resizeComplete:  #step 2 checks if file resize is complete and if so cleans up, if not factory resets device
        syslog.syslog(f'The file {sdPath} exists and {oobPath} does not')
        syslog.syslog(f'checking if new file size is correct')
        newFilesize = subprocess.check_output("df | grep overlayfs:/overlay |  awk '{ print $4 }'", shell=True)
        syslog.syslog(f' newFilesize = {newFilesize}')
        syslog.syslog(f' oldFilesize = {oldFilesize}')

        #checks if filesize is greater then 2 GB, if not factory resets
        if newFilesize > oldFilesize:
            syslog.syslog('OOB check complete, deleting unneeded files')
            os.system('echo "file resize complete" > /root/systemStateFlags/fileResizeComplete.txt')
            os.system('echo "hardware oob check complete" > /root/systemStateFlags/hardwareOobComplete.txt')
            resizeComplete = True
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

    time.sleep(300)
