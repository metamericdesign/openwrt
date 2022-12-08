import time
import os
import syslog  
import json

hibernationTime = 15

#all files path needed for checking
path_to_systemFlags = '/root/systemStateFlags'
path_to_provisionComplete = f'{path_to_systemFlags}/provisionComplete.txt'
path_to_gitClonesComplete = f'{path_to_systemFlags}/gitClonesComplete.txt'
path_to_orgDetails = f'{path_to_systemFlags}/orgDetails.txt'
gitClonesComplete = f'{path_to_systemFlags}/gitClonesComplete.txt'
path_to_gsSystems_Lighting = '/root/gsSystems_Lighting'
path_to_BaseStationPHP = '/srv/www/BaseStationPHP'

#makes file paths into booleans
provisionCompletePathExists = os.path.exists(path_to_provisionComplete)
gitClonesCompletePathexists = os.path.exists(path_to_gitClonesComplete)

time.sleep(15)

while(1):

    orgDetails_pathexists = os.path.exists(path_to_orgDetails)

    #get git https key from org details
    f = open(path_to_orgDetails, "r")
    gitHttpsKey = json.loads(f.read())["gh_key"]
    f.close()

    #setting up the git clone calls
    gitlightingpath="/root"
    gitlighting=f'https://{gitHttpsKey}@github.com/metamericdesign/gsSystems_Lighting.git'
    gitphpRepo = f'git -C {gitphppath} clone {gitphp}'

    gitphppath="/srv/www" 
    gitphp=f'https://{gitHttpsKey}@github.com/metamericdesign/BaseStationPHP.git'
    gitlightingRepo =f'git -C {gitlightingpath} clone {gitlighting}'

    #creating a list to use in the for each loop
    gitRepos = [gitlightingRepo, gitphpRepo] #clone commads for thr repos
    gitRepoNames =["lightingWorker","basestationPhp"] #names to use in print statement

    provisionCompletePathExists = os.path.exists(path_to_provisionComplete)
    gitClonesCompletePathexists = os.path.exists(path_to_gitClonesComplete)

    syslog.syslog(f'Github worker has started')
    syslog.syslog(f'Checking for provisionComplete')
    syslog.syslog(f'provisionCompletePathExists = {provisionCompletePathExists}')

    #Step 1 Cloning ,while loop checks to make sure file resize has occured and clones havent been aquired yet
    if(provisionCompletePathExists and not gitClonesCompletePathexists):

        #makes file paths into booleans
        gsLightingPathexists = os.path.exists(path_to_gsSystems_Lighting)
        baseStationPhpPathexists = os.path.exists(path_to_BaseStationPHP)
        gitClonesCompletePathexists = os.path.exists(path_to_gitClonesComplete)

        #creating a list to use in the for each loop
        gitExists =[gsLightingPathexists,baseStationPhpPathexists]# boolean list

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

            f = open(gitClonesComplete, "w")
            f.write("git Clones Complete")
            f.close()
            hibernationTime = 300
    else :
        syslog.syslog(f'file size is not resized, waiting for reboot')

    #step 2 Pulling, while loop for pulling the newest versions of git repos
    if(gitClonesCompletePathexists):
        syslog.syslog(f'this is a test, clone complete now waiting')

    syslog.syslog(f'githubWorker waiting for something to do')
    time.sleep(hibernationTime)
