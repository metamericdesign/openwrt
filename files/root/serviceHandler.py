import os
import subprocess

path_to_services = '/etc/init.d/'

stat = subprocess.check_output("ps | grep py", shell=True).decode().strip()#binary->str->get rid of \n

print(stat)