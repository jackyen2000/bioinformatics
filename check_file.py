import time
import os
import sys
import subprocess
#from subprocess import Popen, PIPE

#directories = "/var/www/analysis/4646"

#find /var/www/analysis -mmin -60 -mmin +5 -type d


## create the global variable directoryies
directories = subprocess.check_output(['find', '/var/www/analysis', '-type', 'd', '-mmin', '-60'])

timestamp = time.strftime('%Y%m%d.%H%M%S', time.localtime())
def FindNewRun():
    if len(directories)==0:
        print "==== No new Run Folder, all run has been processed ==== {t}".format(t=timestamp)
    else:
        print "==== Found a new run directory ===={t}".format(t=timestamp), directories.splitlines()[1]




def CheckRunComplete():
    if os.path.exists(os.path.join(directories+"completed.1"))==False:
        print "==== Waiting for New Run ==== {t}".format(t=timestamp)
    else:
        print "==== New Run Completed!!! ==== {t}".format(t=timestamp), os.path.isfile(os.path.join(directories[1],"completed.1"))



#directories = subprocess.check_output(['find', '/var/www/analysis', '-type', 'd', '-mmin', '-1000']).splitlines()

#os.path.isfile(os.path.join("/var/www/analysis/4667","completed.1"))
#os.path.isfile(os.path.join(directories[1],"completed.1"))

# directories content: ['/data1/realtime/dir1000', ...]

#if not os.path.exists(directory):
#    os.makedirs(directory)