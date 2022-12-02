from pathlib import Path
import time
import os
import syslog 

path_to_cloneCheck = '/root/gitCloneRequired.txt'
path_to_cloneComplete = '/root/gitCloneRequired.txt'


time.sleep(25)

while(1):
    cloneCheckPath = Path(path_to_cloneCheck)
    cloneCompletePath = Path(path_to_cloneComplete)
  
    cloneRequired = os.path.exists(cloneCheckPath)
    cloneComplete = os.path.exists(cloneCompletePath)

    syslog.syslog(f'Starting cloneRequiredCheck')
    syslog.syslog(f' cloneRequired = {cloneRequired}')



    if os.path.exists(cloneRequired):
        syslog.syslog(f'Clone is required')
        os.system('./root/gitClone.sh')
        time.sleep(7)
        syslog.syslog(f'Clone aquired')
        os.system('rm /root/gitCloneRequired.txt')
        os.system('echo "cloning is complete" > /root/cloningComplete.txt')

    if os.path.exists(cloneComplete):
        syslog.syslog(f'Clone is aquired, killing proccesses')

    
    syslog.syslog(f'file size is not resized, waiting to clone git')
    time.sleep(30)