import time
import os
import syslog  
import json


syslog.syslog(f'Github worker will start in 30 seconds')
time.sleep(30)

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

while(1):
    try:
        provisionCompletePathExists = os.path.exists(path_to_provisionComplete)
        if(provisionCompletePathExists):
            syslog.syslog(f' Github loop start.')
            orgDetails_pathexists = os.path.exists(path_to_orgDetails)

            #get git https key from org details
            f = open(path_to_orgDetails, "r")
            gitHttpsKey = json.loads(f.read())["gh_key"]
            f.close()

            #setting up the git clone calls
            gitlightingpath="/root"
            gitlighting=f'https://{gitHttpsKey}@github.com/metamericdesign/gsSystems_Lighting.git'
            gitlightingRepo =f'git -C {gitlightingpath} clone {gitlighting}'
            pulllightingRepo =f'git -C {gitlightingpath} pull {gitlighting}'
            
            gitphppath="/srv/www" 
            gitphp=f'https://{gitHttpsKey}@github.com/metamericdesign/BaseStationPHP.git'
            gitphpRepo = f'git -C {gitphppath} clone {gitphp}'
            pullphpRepo = f'git -C {gitphppath} pull {gitphp}'

            #creating a list to use in the for each loop
            gitRepos = [gitlightingRepo, gitphpRepo] #clone commads for thr repos
            pullRepos = [pulllightingRepo, pullphpRepo] #pull commads for thr repos
            gitRepoNames =["lightingWorker","basestationPhp"] #names to use in print statement

            provisionCompletePathExists = os.path.exists(path_to_provisionComplete)   
            syslog.syslog(f'provisionCompletePathExists = {provisionCompletePathExists}')

            #Step 1 Cloning ,while loop checks to make sure file resize has occured
        

            #makes file paths into booleans
            gsLightingPathexists = os.path.exists(path_to_gsSystems_Lighting)
            baseStationPhpPathexists = os.path.exists(path_to_BaseStationPHP)
        

            #creating a list to use in the for each loop
            gitExists =[gsLightingPathexists,baseStationPhpPathexists]# boolean list

            #for each loop that will attempt to clone repo if not found
            for (repoClone,gitExists,workerName,repoPull) in zip(gitRepos,gitExists,gitRepoNames,pullRepos):

                if not gitExists :
                    syslog.syslog(f'    Git {workerName} not present, attempting to clone')
                    os.system(f'{repoClone}')
                
                if gitExists :
                    syslog.syslog(f'    Git {workerName} exists, attempting to pull newest version if one is available')
                    os.system(f'{repoPull}')
                    hibernationTime = 300
            
        
        
        else :
            syslog.syslog(f'  Device is not Provisioned Trying again in {hibernationTime} seconds')
            time.sleep(hibernationTime)

        syslog.syslog(f' githubWorker loop end, hibernate for {hibernationTime}')
        time.sleep(hibernationTime)
    except Exception as err:
           syslog.syslog("GitWorker CRASH")
           syslog.syslog(f"ERROR -> {err}")
