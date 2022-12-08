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

syslog.syslog(f'Github worker has started')

#makes file paths into booleans
provisionCompletePathExists = os.path.exists(path_to_provisionComplete)
gitClonesCompletePathexists = os.path.exists(path_to_gitClonesComplete)

time.sleep(5)

while(1):
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
    
    gitphppath="/srv/www" 
    gitphp=f'https://{gitHttpsKey}@github.com/metamericdesign/BaseStationPHP.git'
    gitphpRepo = f'git -C {gitphppath} clone {gitphp}'

    #creating a list to use in the for each loop
    gitRepos = [gitlightingRepo, gitphpRepo] #clone commads for thr repos
    gitRepoNames =["lightingWorker","basestationPhp"] #names to use in print statement

    provisionCompletePathExists = os.path.exists(path_to_provisionComplete)   
    syslog.syslog(f'provisionCompletePathExists = {provisionCompletePathExists}')

    #Step 1 Cloning ,while loop checks to make sure file resize has occured
    if(provisionCompletePathExists): 

        #makes file paths into booleans
        gsLightingPathexists = os.path.exists(path_to_gsSystems_Lighting)
        baseStationPhpPathexists = os.path.exists(path_to_BaseStationPHP)
      

        #creating a list to use in the for each loop
        gitExists =[gsLightingPathexists,baseStationPhpPathexists]# boolean list

        #for each loop that will attempt to clone repo if not found
        for (repoClone,gitExists,workerName) in zip(gitRepos,gitExists,gitRepoNames):

            if not gitExists :
                syslog.syslog(f'    Git {workerName} not present, attempting to clone')
                os.system(f'{repoClone}')
            
            if gitExists :
                syslog.syslog(f'    Git {workerName} exists')
        
      
       
    else :
        syslog.syslog(f'  file system size is not resized.')

    #step 2 Pulling, while loop for pulling the newest versions of git repos
    

    syslog.syslog(f' githubWorker loop end, hibernate for {hibernationTime}')
    time.sleep(hibernationTime)
