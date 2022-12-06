from pathlib import Path
import time
import os
import syslog 

path_to_hardwareOobComplete = '/root/systemStateFlags/hardwareOobComplete.txt'
path_to_gsSystems_Lighting = '/root/gsSystems_Lighting'
path_to_BaseStationPHP = '/srv/www/BaseStationPHP'

hardwareOobCompletePath = Path(path_to_hardwareOobComplete)
hardwareOobCompletePathexists = os.path.exists(hardwareOobCompletePath)

gitlightingpath="/root"
gitlighting="https://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@github.com/metamericdesign/gsSystems_Lighting.git"

gitphppath="/srv/www" 
gitphp="https://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@github.com/metamericdesign/BaseStationPHP.git"

time.sleep(15)

syslog.syslog(f'Checking for hardwareOobCompletePath')
syslog.syslog(f' hardwareOobCompletePathexists = {hardwareOobCompletePathexists}')

while(hardwareOobCompletePathexists):

    gsLightingPath = Path(path_to_gsSystems_Lighting)
    baseStationPhpPath = Path(path_to_BaseStationPHP)

    gsLightingPathexists = os.path.exists(gsLightingPath)
    baseStationPhpPathexists = os.path.exists(baseStationPhpPath)

    if not gsLightingPathexists:
        syslog.syslog(f'gsSystems_Lighting clone not present, attempting to clone')
        os.system(f'git -C {gitlightingpath} clone {gitlighting}')

    if not baseStationPhpPathexists:
        syslog.syslog(f'BaseStationPHP clone not present, attempting to clone')
        os.system(f'git -C {gitphppath} clone {gitphp}')

    if gsLightingPathexists :
        syslog.syslog(f'gsLighting Clone aquired')

    if baseStationPhpPathexists:
        syslog.syslog(f'baseSationPhp Clone aquired')
    
    if gsLightingPathexists and baseStationPhpPathexists:
        syslog.syslog('all Clones aquired')
        os.system('echo "Software Oob is complete" > /root/systemStateFlags/softwareOobComplete.txt')

    time.sleep(15)


    
syslog.syslog(f'file size is not resized, waiting to clone git')
time.sleep(15)

