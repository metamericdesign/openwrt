import os
import syslog 

hibernationTime = 30;

path_to_requestroot = '/tmp/gsvpnrequests'
path_to_basestation_requests = f'{path_to_requestroot}/basestation'
path_to_desktop_requests = f'{path_to_requestroot}/desktop'

While(1):
  syslog.syslog('VPN Provision Worker Loop Start')
  try:
    while(1):
      syslog.syslog('  Checking for new request files...')
      # make sure temporary folders exist
      
      time.sleep(hibernationTime)
            
  except:
    syslog.syslog(syslog.LOG_ERR,'VPN Provision Main loop crash!')
  syslog.syslog('VPN Provision Worker Loop End, sleeping.')
  time.sleep(hibernationTime)
