from pathlib import Path
import time
import os
import syslog  
import json

#all files path needed for checking
path_to_provisionComplete = '/root/systemStateFlags/provisionComplete.txt'
path_to_gsSystems_Lighting = '/root/gsSystems_Lighting'
path_to_BaseStationPHP = '/srv/www/BaseStationPHP'
path_to_gitClonesComplete = '/root/systemStateFlags/gitClonesComplete.txt'

#makes file paths into booleans
provisionCompletePath = Path(path_to_provisionComplete)
provisionCompletePathexists = os.path.exists(provisionCompletePath)

gitClonesCompletePath = Path(path_to_gitClonesComplete)
gitClonesCompletePathexists = os.path.exists(gitClonesCompletePath)

path_to_orgDetails = '/root/systemStateFlags/orgDetails.txt'
orgDetailsPath = Path(path_to_orgDetails)

time.sleep(15)

syslog.syslog(f'Github worker has started')
syslog.syslog(f'Checking for provisionComplete')
syslog.syslog(f' provisionCompletePathexists = {provisionCompletePathexists}')

while(1):

    orgDetailsPathexists = os.path.exists(orgDetailsPath)

    #git clone required paths and https calls
    f = open(orgDetailsPath, "r")
    gitHttpsKey = json.loads(f.read())["gh_key"]
    f.close()

    gitlightingpath="/root"
    gitlighting=f'https://{gitHttpsKey}@github.com/metamericdesign/gsSystems_Lighting.git'

    gitphppath="/srv/www" 
    gitphp=f'https://{gitHttpsKey}@github.com/metamericdesign/BaseStationPHP.git'

    gitphpRepo = f'git -C {gitphppath} clone {gitphp}'
    gitlightingRepo =f'git -C {gitlightingpath} clone {gitlighting}'

    #creating a list to use in the for each loop
    gitRepos = [gitlightingRepo, gitphpRepo]
    gitRepoNames =["lightingWorker","basestationPhp"]

    provisionCompletePathexists = os.path.exists(provisionCompletePath)
    gitClonesCompletePathexists = os.path.exists(gitClonesCompletePath)


    #Step 1 Cloning ,while loop checks to make sure file resize has occured and clones havent been aquired yet
    if(provisionCompletePathexists and not gitClonesCompletePathexists):

        #makes file paths into booleans
        gsLightingPath = Path(path_to_gsSystems_Lighting)
        baseStationPhpPath = Path(path_to_BaseStationPHP)
        gitClonesCompletePath = Path(path_to_gitClonesComplete)

        gsLightingPathexists = os.path.exists(gsLightingPath)
        baseStationPhpPathexists = os.path.exists(baseStationPhpPath)
        gitClonesCompletePathexists = os.path.exists(gitClonesCompletePath)

        #creating a list to use in the for each loop
        gitExists =[gsLightingPathexists,baseStationPhpPathexists]

        #for each loop that will attempt to clone repo if not found
        for (repoClone,gitExists,workerName) in zip(gitRepos,gitExists,gitRepoNames):

            if not gitExists :
                syslog.syslog(f'{gitExists} not present, attempting to clone')
                os.system(f'{repoClone}')
            
            if gitExists :
                syslog.syslog(f'{workerName} Clone acquired')
        
        #if all Repos have been cloned creates a flag stating that and exists to git pull section
        if gsLightingPathexists and baseStationPhpPathexists:
            syslog.syslog('all Clones aquired')
            os.system('echo "gitClonesComplete" > /root/systemStateFlags/gitClonesComplete.txt')
        
    syslog.syslog(f'file size is not resized, waiting for reboot')

    #step 2 Pulling, while loop for pulling the newest versions of git repos
    if(gitClonesCompletePathexists):
        syslog.syslog(f'this is a test, clone complete now waiting')

    syslog.syslog(f'githubWorker waiting for something to do')
    time.sleep(15)
