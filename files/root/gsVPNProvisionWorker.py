import os
import syslog 
import time

hibernationTime = 30;

path_to_requestroot = '/tmp/gsvpnrequests'
path_to_basestation_requests = f'{path_to_requestroot}/basestation'
path_to_desktop_requests = f'{path_to_requestroot}/desktop'

def processBaseStaRequests(requestlist):
    pass

def processDesktopRequests(requestlist):
    pass

while(1):
  syslog.syslog('VPN Provision Worker Loop Start')
  try:
    while(1):
      syslog.syslog('  Checking for new request files...')
      
      if not os.path.exists(path_to_requestroot):                           # make sure temporary folders exist
          os.makedirs(path_to_basestation_requests)
          os.makedirs(path_to_desktop_requests)
      
      list_BaseStaRequests = os.listdir(path_to_basestation_requests)       # get a list of basestation requests
      list_DesktopRequests = os.listdir(path_to_desktop_requests)           # get a list of desktop requests
      
      if len(list_BaseStaRequests):                                         # process basestation requests
          syslog.syslog('   Found Basestation Requests')
          processBaseStaRequests(list_BaseStaRequests)
          pass
      
      if len(list_DesktopRequests):                                         # process desktop requests
          syslog.syslog('   Found Basestation Requests')
          processDesktopRequests(list_DesktopRequests)
          pass
      
      time.sleep(hibernationTime)
            
  except:
    syslog.syslog(syslog.LOG_ERR,'VPN Provision Main loop crash!')
  syslog.syslog('VPN Provision Worker Loop End, sleeping.')
  time.sleep(hibernationTime)
