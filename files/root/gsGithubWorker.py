import time
import os
import syslog  
import json
import gsDebugPrint

gsdb = gsDebugPrint.gsDebugPrint("gsGithubWorker")

gsdb.setPrintToTerminal(False)
gsdb.setPrintToSysLog(True)
#
# Get repo list from provisioning, list from data base
#

gsdb.gsDebugPrint(f'Github worker will start in 30 seconds',1)
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
            gsdb.gsDebugPrint(f' Github loop start.',1)
            orgDetails_pathexists = os.path.exists(path_to_orgDetails)

            #get git https key from org details
            try:
                gsdb.gsDebugPrint('Checking Org Details for gh_key')
                f = open(path_to_orgDetails, "r")
                gitHttpsKey = json.loads(f.read())["gh_key"]
                f.close()
                gsdb.gsDebugPrint('gh_key exists')
            except Exception as err:
                gsdb.gsDebugPrint("Github Worker Org Details Crash!",3)
                gsdb.gsDebugPrint(f"ERROR -> {err}",3)
                time.sleep(20)

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
            gsdb.gsDebugPrint(f'provisionCompletePathExists = {provisionCompletePathExists}')

            #Step 1 Cloning ,while loop checks to make sure file resize has occured
        

            #makes file paths into booleans
            gsLightingPathexists = os.path.exists(path_to_gsSystems_Lighting)
            baseStationPhpPathexists = os.path.exists(path_to_BaseStationPHP)
        

            #creating a list to use in the for each loop
            gitExists =[gsLightingPathexists,baseStationPhpPathexists]# boolean list

            #for each loop that will attempt to clone repo if not found
            for (repoClone,gitExists,workerName,repoPull) in zip(gitRepos,gitExists,gitRepoNames,pullRepos):

                if not gitExists :
                    gsdb.gsDebugPrint(f'    Git {workerName} not present, attempting to clone')
                    os.system(f'{repoClone}')
                
                if gitExists :
                    gsdb.gsDebugPrint(f'    Git {workerName} exists, attempting to pull newest version if one is available')
                    os.system(f'{repoPull}')
                    hibernationTime = 300
            
        
        
        else :
            gsdb.gsDebugPrint(f'  Device is not Provisioned Trying again in {hibernationTime} seconds',2)
            time.sleep(hibernationTime)

        gsdb.gsDebugPrint(f' githubWorker loop end, hibernate for {hibernationTime}')
        time.sleep(hibernationTime)
    except Exception as err:
           gsdb.gsDebugPrint("GitWorker CRASH",3)
           gsdb.gsDebugPrint(f"ERROR -> {err}",3)
