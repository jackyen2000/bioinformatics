# #===========================================================================##
# # align_bwa.py
# #
# # Version 1.0
# # Find FASTQ file in runFolder and execute BWA and PICARD sortSAM
# # This script will continue to evolve and integrate with luigi and
# # additional task will be added
# #
# # Jack Yen
# # May 31st, 2017
# #===========================================================================##
# #===========================================================================##
# # All of the general library calls and PATH
# #===========================================================================##


import sys,re,os,argparse,glob,errno
import logging as log
from subprocess import Popen, PIPE

import subprocess

## working directory
#os.chdir(r'/Volumes/lab data/Rutherford_data/HCP_data/161130_NB501330_0059_AHGWVLAFXX/Data/Intensities/BaseCalls')
os.chdir(r'/media/fs02/Rutherford_data/HCP_data/test')

parser = argparse.ArgumentParser()
parser.add_argument('-r',dest='runName', required=True)
#parser.add_argument('-s',dest='sampleId',required=False)
#
args = parser.parse_args()
runName = args.runName
#sampleID = args.sampleId

work_dir = r'/media/fs02/Rutherford_data/HCP_data/'
#fastq_dir_test = os.path.join(r'/Volumes/lab data/Rutherford_data/HCP_data/test')
fastq_dir = os.path.join(work_dir,runName,'Data/Intensities/BaseCalls')

print 'the FASTQ directory is at: ',fastq_dir
## reference
#reference_test = r'/Volumes/lab data/reference/hg19/hg19.fasta'
reference = r'/media/fs02/reference/hg19/hg19.fasta'

#software BWA, samtools
PICARD_JAR = '/home/lee/NGS/picard.jar'
picard              = 'java -jar '+ PICARD_JAR
picard_more_memory  = 'java -jar -Xmx20g ' + PICARD_JAR

#FASTQ - checking FASTQ file format
if not os.path.exists(fastq_dir):
    log.error("FASTQ_Dir does not exist: %s" % fastq_dir)
    sys.exit(1)

read1_lanes = []
read2_lanes = []
#r1_pattern = re.compile(r'.*L\d{3}_R1_\d{3}_001.fastq\.gz')
r1_pattern = re.compile(r'.*_R1_001.fastq.gz')
#r2_pattern = re.compile(r'.*L\d{3}_R2_\d{3}_001.fastq\.gz')
r2_pattern = re.compile(r'.*_R2_001.fastq.gz')

for fastq in glob.glob(os.path.join(fastq_dir, '*.fastq.gz')):
    #print fastq
    if r1_pattern.match(fastq):
        read1_lanes.append(fastq)
    elif r2_pattern.match(fastq):
        read2_lanes.append(fastq)
    else:
        log.warn("FASTQ File %s did not match pattern", fastq)

log.info("Found %d lanes for sample %s", len(read1_lanes))
print 'FASTQ files: ',read1_lanes, read2_lanes

## create sam file list
sam_file_list = []
output_dir    = os.path.join(fastq_dir,'pipeline_output')
try:
    os.makedirs(output_dir)
except OSError as exception:
    if exception.errno != errno.EEXIST:
        raise


# Align FASTQ
for index,file in enumerate(read1_lanes):
    # Alignment inputs
    read1 = read1_lanes[index]
    read2 = read2_lanes[index]

    # Alignment outputs
    #lane = index + 1
    #sam        = os.path.join(output_dir,'lane' + str(lane) + '.sam')

    samplename = os.path.basename(read1).split("_R1_001")[0]
    sam        = os.path.join(output_dir,samplename + '.sam')

    print samplename
    #print type(read1)
    #print read2
    #print sam

    ## BWA align
    ## Step 1. Run bwa mem, FASTQ --> SAM
    ## Step 2. samtools to convert SAM --> BAM
    ## Step 3. samtools BAM --> sorted_BAM
    #RG_Tag = '"@RG\tID:' + runName + '\tPU:' + str(lane) + '\tSM:' + sampleId + '"'
    RG_Tag = '"@RG\tID:' + runName + '\tPU:' + '\tSM:' + samplename + '"'
    bwa_cmd = 'bwa mem' + ' -t 20' + ' -v 3 '+ ' -R '+ RG_Tag + ' '+'"' +reference+ '"' + ' ' + '"' +read1 + '"' +' ' + '"'+read2 + '"' + ' > ' + sam
    samtools_convert = 'samtools view -S -b'
    samtools_sort    = 'samtools sort -o '+ ' ' +'>'+ ' ' + samplename+'_sorted.bam'
    print bwa_cmd
    #print samtools_sort
    ## use subprocess to execute the bash commands
    #outfile = open(samplename + '_sorted.bam','w')
    log.info(bwa_cmd)
    bwa_process     = subprocess.call(bwa_cmd,shell=True)
    sam_file_list.append(sam)
    print sam


# Merge SAM Files and Sort

# Create a list of files to merge
#merge_input_string = ''
#for file in sam_file_list:
#    merge_input_string = merge_input_string + ' I='+ file

# Picard SortSam can convert SAM to BAM and sort
for file in sam_file_list:
    BAM = os.path.join(output_dir, os.path.basename(file).split('.')[0]+ '_sorted.bam')
    sort_cmd = picard + ' SortSam VALIDATION_STRINGENCY=SILENT Sort_Order=coordinate'+ ' I=' + file + ' O=' + BAM
    print sort_cmd
    log.info(sort_cmd)
    subprocess.call(sort_cmd,shell=True)
    os.remove(os.path.abspath(file))
#convert_process = subprocess.Popen(samtools_convert, stdin=bwa_process.stdout, stdout=subprocess.PIPE,shell=True)
#sort_process    = subprocess.Popen(samtools_sort, stdin=convert_process.stdout,stdout=subprocess.PIPE,shell=True)


print ('==== bwa pipeline finished!!!====')


