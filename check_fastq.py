import time
import os
import sys
import subprocess

# from subprocess import Popen, PIPE

# directories = "/var/www/analysis"

# find /var/www/analysis -mmin -60 -mmin +5 -type d

## create the global variable directoryies

os.chdir('/media/fs02/NextSeq2017')

## INPUT & OUTPUT FOLDERS
HCP_PIPELINE_DATA_DIR = '/media/fs02/NextSeq2017'
HCP_PIPELINE_OUTPUT_DIR = '/home/lee/workspace/HCP_pipeline'
TEST_RUN_DIR = '/media/fs02/NextSeq2017/170501_NB501920_0016_AHJJ7TAFXX/'
TARGET_DIR = 'root@10.10.11.23:/var/www/analysis/watched/Lee.Szkotnicki@cgix.com/HCP_FASTQ_queue'

directories_list = subprocess.check_output(['find',HCP_PIPELINE_DATA_DIR, '-type', 'd', '-mmin', '-60'])
new_run = directories_list.splitlines()[0]

timestamp = time.strftime('%Y%m%d.%H%M%S', time.localtime())



if len(new_run) == 0:
    print "==== No new Run Folder, all run has been processed ==== {t}".format(t=timestamp)
else:
    ## 1. find new run folder
    print "==== Found a new run directory ===={t}".format(t=timestamp), new_run

    ## 2. find runcompletion.xml
    if os.path.exists(os.path.join(TEST_RUN_DIR+"RunCompletionStatus.xml"))==False:
        print "==== Waiting for New Run ==== {t}".format(t=timestamp)
    else:
        print "==== New Run  <%s>  Completed!!! at {t} ====".format(t=timestamp) %(new_run.split('/')[4])


        ## 3. copy FASTQ
        copy_cmd = [''"sshpass -p password123"+' '+'scp -r *fastq.gz'+' '+new_run+' '+TARGET_DIR]
        with open('fastq_transfer.log',"w") as outfile:
            subprocess.call(copy_cmd,stdout=outfile,stdin=outfile,shell=True)
            #subprocess.call(copy_cmd,shell=True)
        print ('==== copy FASTQ to Archer COMPLETED !!! ====')
        outfile.close()

        ## 4. make a completed file
        if os.path.exists(new_run,new_run.completed):
            print 'completed file already exist'
        else:
            open(os.path.joing(new_run,new_run.completed),'w')








