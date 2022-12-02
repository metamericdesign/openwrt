from pathlib import Path
import time
import os
import syslog 

path_to_usb = '/dev/sda1'


path_to_oobCheck = '/root/oobCheck.txt'

time.sleep(3)

while(1):
    usbPath = Path(path_to_usb)
    oobPath = Path(path_to_oobCheck)
    usbPathexists = os.path.exists(usbPath)
    oobPathexists = os.path.exists(oobPath)
    syslog.syslog(f'Starting oobCheck')
    syslog.syslog(f' usbPathexists = {usbPathexists}')
    syslog.syslog(f' oobPathexists = {oobPathexists}')


    if os.path.exists(usbPath) and oobPath.is_file():
        syslog.syslog(f'Starting file resize')
        
        os.system('echo "file resize complete" > /root/fileResizeComplete.txt')
        os.system('rm /root/oobCheck.txt')

        os.system('./root/fileresize.sh')
        time.sleep(20)

        syslog.syslog(f'The file {oobPath} and {usbPath} exists, rebooting')

        os.system('reboot')
        
    elif os.path.exists(usbPath) and not oobPath.is_file():
        syslog.syslog(f'OOB check complete, deleting unneeded files')
        syslog.syslog(f'The file {usbPath} exists and {oobPath} does not')
        os.system('echo "oob check complete" > /root/oobCheckComplete.txt')
        os.system('echo "git clone required" > /root/gitCloneRequired.txt')
        os.system('rm /root/fileresize.sh')
        os.system('rm /etc/init.d/runOobCheck')
        os.system('rm /root/rebootAfterFilesize.py')
        os.system('reboot')
    
    syslog.syslog(f'Nothing found,going to sleep')
    time.sleep(10)