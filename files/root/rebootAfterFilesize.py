from pathlib import Path
import time
import os
import syslog 

path_to_usb = '/dev/sda1'
path_to_oobCheck = '/root/oobCheck.txt'
path_to_cloneCheck = '/root/gitCloneRequired.txt'
path_to_cloneComplete = '/root/cloningComplete.txt'
path_to_gsSystems_Lighting = '/root/gsSystems_Lighting'
path_to_BaseStationPHP = '/srv/www/BaseStationPHP'

gitlightingpath="/root"
gitlighting="https://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@github.com/metamericdesign/gsSystems_Lighting.git"

gitphppath="/srv/www" 
gitphp="https://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@github.com/metamericdesign/BaseStationPHP.git"

gitCloneRequested = False

time.sleep(3)

while(1):
    usbPath = Path(path_to_usb)
    oobPath = Path(path_to_oobCheck)
    cloneCheckPath = Path(path_to_cloneCheck)
    cloneCompletePath = Path(path_to_cloneComplete)
    gsLightingPath = Path(path_to_gsSystems_Lighting)
    baseStationPhpPath = Path(path_to_BaseStationPHP)

    usbPathexists = os.path.exists(usbPath)
    oobPathexists = os.path.exists(oobPath)
    cloneRequired = os.path.exists(cloneCheckPath)
    cloneComplete = os.path.exists(cloneCompletePath)
    gsLightingPathexists = os.path.exists(gsLightingPath)
    baseStationPhpPathexists = os.path.exists(baseStationPhpPath)

    syslog.syslog(f'Starting oobCheck')
    syslog.syslog(f' usbPathexists = {usbPathexists}')
    syslog.syslog(f' oobPathexists = {oobPathexists}')


    if usbPathexists and oobPathexists: # checks if usb is connected and if a file resize is needed
        syslog.syslog(f'Starting file resize')
    
        os.system('rm /root/oobCheck.txt')

        os.system('./root/fileresize.sh')
        time.sleep(15)

        syslog.syslog(f'The file {oobPath} and {usbPath} exists, rebooting')

        os.system('reboot')

    elif usbPathexists and not oobPathexists and not gitCloneRequested:  # checks if file resize is complete and call for a git clone
        syslog.syslog(f'The file {usbPath} exists and {oobPath} does not')
        os.system('echo "file resize complete" > /root/fileResizeComplete.txt')
        os.system('echo "git clone required" > /root/gitCloneRequired.txt')
        gitCloneRequested = True

    elif cloneRequired: #checks if a git clone is required

        syslog.syslog(f'Clone is required')

        if not gsLightingPathexists:
            os.system('git -C {gitlightingpath} clone {gitlighting}')
            syslog.syslog(f'gsLighting Clone aquired')

        if not baseStationPhpPathexists:
            os.system('git -C {gitphppath} clone {gitphp}')
            syslog.syslog(f'baseSationPhp Clone aquired')
        
        if gsLightingPathexists and baseStationPhpPathexists:

            time.sleep(7)
            syslog.syslog(f'all Clones aquired')
            os.system('rm /root/gitCloneRequired.txt')
            os.system('echo "cloning is complete" > /root/cloningComplete.txt')

    elif cloneComplete:
        syslog.syslog(f'OOB check complete, deleting unneeded files')
        syslog.syslog(f'The file {usbPath} and {cloneCompletePath} exist')
        os.system('echo "oob check complete" > /root/oobCheckComplete.txt')
        os.system('rm /root/fileresize.sh')
        os.system('rm /etc/init.d/runOobCheck')
        os.system('rm /root/rebootAfterFilesize.py')
        os.system('reboot')

    else:
    
        syslog.syslog(f'Nothing found,going to sleep')

    time.sleep(10)
