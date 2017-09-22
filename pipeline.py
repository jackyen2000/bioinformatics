'''
# #===========================================================================##
# # pipeline.py
# #
# # Version 2.0
# # 1. Find FASTQ file
# # 2. Check if FASTQ file has pairs
# # 3. and execute BWA-->convert SAM to BAM
# # 4. PICARD sortSAM
# # 5. Index BAM file
# # 6. GATK unifiedGenotype
# #
# # This script will continue to evolve and integrate with luigi and
# # additional task will be added
# #
# # Jack Yen
# # Sep 11th, 2017
# # EDIT: add trimming options, re-direct log into individual txt files for each steps.
# #===========================================================================##
# #===========================================================================##
# # All of the general library calls and PATH
# #===========================================================================##
'''

'''
USAGE: 
python align_bwa_v2.py -w <work_dir> -r <run_dir> -s <sampleId> -t <tmp_dir> <optional:--trimming/--no-trimming>
'''



#!/usr/bin/python
'''
import packages
'''
import sys,re,os,argparse,glob,errno
import logging as log
from subprocess import Popen, PIPE
import subprocess

## working directory
#os.chdir(r'/Volumes/lab data/Rutherford_data/HCP_data/161130_NB501330_0059_AHGWVLAFXX/Data/Intensities/BaseCalls')

## add parameter
parser = argparse.ArgumentParser()
parser.add_argument('-w',dest='work_dir',help=('full path of working directory'),required=True)
parser.add_argument('-r',dest='runName',help=('full path of running directory wit data'),required=True)
parser.add_argument('-s',dest='sampleId',help=('option to execute individually by sampleId'),required=True)
#parser.add_argument('-t',dest='tmp_dir', default='/scratch')

parser.add_argument('--trimming', dest='trimming', action='store_true')
parser.add_argument('--no-trimming', dest='trimming', action='store_false')
parser.set_defaults(trimming=False)


args = parser.parse_args()
runName = args.runName
sampleId = args.sampleId
#tmp_dir  = args.tmp_dir
work_dir = args.work_dir
trimming = args.trimming

#work_dir = r'/media/fs02/Rutherford_data/HCP_data/'
#fastq_dir_test = os.path.join(r'/Volumes/lab data/Rutherford_data/HCP_data/test')
#fastq_dir = os.path.join(work_dir,runName,'Data/Intensities/BaseCalls')
fastq_dir = os.path.join(work_dir,runName,sampleId)

print 'the FASTQ directory is at: ',fastq_dir
## reference
#reference_test = r'/Volumes/lab data/reference/hg19/hg19.fasta'
reference = r'/media/fs02/reference/hg19/hg19.fasta'


'''
Define reference and software BWA, samtools, PICARD, GATK, Trimmomatic
'''


PICARD_JAR = '/home/lee/NGS/picard.jar'
picard              = 'java -jar '+ PICARD_JAR
picard_more_memory  = 'java -jar -Xmx20g ' + PICARD_JAR

TRIMMOMATIC_JAR = '/home/lee/NGS/Trimmomatic-0.36/trimmomatic-0.36.jar'
trimmomatic     = 'java -jar '+TRIMMOMATIC_JAR

GATK_JAR = '/home/lee/NGS/GenomeAnalysisTK.jar'
gatk     = 'java -jar -Xmx2g '+GATK_JAR
gatk_more_memory = 'java -jar -Xmx10g '+GATK_JAR


## FASTQ - checking FASTQ file format
if not os.path.exists(fastq_dir):
    log.error("FASTQ_Dir does not exist: %s" % fastq_dir)
    sys.exit(1)

read1_lanes = []
read2_lanes = []
#r1_pattern = re.compile(r'.*L\d{3}_R1_\d{3}_001.fastq\.gz')
r1_pattern = re.compile(r'.*_R1_001.fastq.gz')
#r2_pattern = re.compile(r'.*L\d{3}_R2_\d{3}_001.fastq\.gz')
r2_pattern = re.compile(r'.*_R2_001.fastq.gz')


for fastq in glob.glob(os.path.join(fastq_dir,'*.fastq.gz')):
    print fastq
    #print fastq
    if r1_pattern.match(fastq):
        read1_lanes.append(fastq)
    elif r2_pattern.match(fastq):
        read2_lanes.append(fastq)
    else:
        log.warn("FASTQ File %s did not match pattern", fastq)

log.info("Found %d lanes for sample %s", len(read1_lanes), sampleId)
print 'FASTQ files: ',read1_lanes, read2_lanes

## create sam file list
sam_file_list = []

output_dir    = os.path.join(fastq_dir,'pipeline_output')
try:
    os.makedirs(output_dir)
except OSError as exception:
    if exception.errno != errno.EEXIST:
        raise


### if not batch, execute by individual sampleID
if trimming:
    for index,file in enumerate(read1_lanes):
        # Trimmomatic inputs
        read1 = read1_lanes[index]
        read2 = read2_lanes[index]

        # Trimmomatic outputs
        lane = index + 1

        # Trimmomatic command
        cmd = trimmomatic + ' ' + read1 + ' ' + read2  + ' ' + 'lane' + str(lane)
        cmd += '.paired.1.fastq.gz ' + 'lane' + str(lane) + '.unpaired.1.fastq.gz ' + 'lane' + str(lane) + '.paired.2.fastq.gz ' + 'lane' + str(lane) + '.unpaired.2.fastq.gz '
        #cmd += 'CROP:' + str(crop)
        os.chdir(fastq_dir)
        log.info(cmd)
        os.system(cmd)

    read1_lanes_trimmed = []
    read2_lanes_trimmed = []
    r1_pattern = re.compile(r'.*\.paired\.1\.fastq\.gz')
    r2_pattern = re.compile(r'.*\.paired\.2\.fastq\.gz')


    for fastq in glob.glob(os.path.join(fastq_dir,'*.fastq.gz')):
        print fastq
        #print fastq
        if r1_pattern.match(fastq):
            read1_lanes.append(fastq)
        elif r2_pattern.match(fastq):
            read2_lanes.append(fastq)
        else:
            log.warn("FASTQ File %s did not match pattern", fastq)

    read1_lanes = read1_lanes_trimmed
    read2_lanes = read2_lanes_trimmed

    log.info("Found %d lanes for sample %s", len(read1_lanes))
    print 'FASTQ files: ',read1_lanes, read2_lanes


## Align FASTQ
for index,file in enumerate(read1_lanes):
    # Alignment inputs
    read1 = read1_lanes[index]
    read2 = read2_lanes[index]

    # Alignment outputs
    lane = index + 1
    #sam        = os.path.join(output_dir,'lane' + str(lane) + '.sam')

    #samplename = os.path.basename(read1).split("_R1_001")[0]
    sam        = os.path.join(output_dir,sampleId + '.sam')

    print sampleId
    #print type(read1)
    #print read2
    #print sam

    ## BWA align
    ## Step 1. Run bwa mem, FASTQ --> SAM
    ## Step 2. samtools to convert SAM --> BAM

    RG_Tag = '"@RG\tID:' + runName + '\tPU:' + str(lane) + '\tSM:' + sampleId + '"'
    #RG_Tag = '"@RG\tID:' + runName + '\tPU:' + '\tSM:' + samplename + '"'
    bwa_cmd = 'bwa mem' + ' -t 20' + ' -v 3 '+ ' -R '+ RG_Tag + ' '+'"' +reference+ '"' + ' ' + '"' +read1 + '"' +' ' + '"'+read2 + '"' + ' > ' + sam
    #samtools_convert = 'samtools view -S -b'
    #samtools_sort    = 'samtools sort -o '+ ' ' +'>'+ ' ' + samplename+'_sorted.bam'
    print 'bwa comand: ',bwa_cmd
    ## use subprocess to execute the bash commands
    #outfile = open(samplename + '_sorted.bam','w')
    log.info(bwa_cmd)
    print "====== Running BWA Mem into memory ======="
    bwa_process     = subprocess.call(bwa_cmd,shell=True,stdout=open(os.path.join(output_dir,sampleId+'_bwa_pipeline_log.txt'),'wt'),stderr=subprocess.STDOUT)
    #bwa_process = subprocess.Popen(bwa_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True)
    #stdout, stderr = bwa_process.communicate()
    sam_file_list.append(sam)
    print 'sam files: ',sam


## Merge SAM Files and Sort

## Create a list of files to merge
## Picard SortSam can convert SAM to BAM and sort
#merge_input_string = ''
#BAM = os.path.join(output_dir,'*_sorted.bam')
for file in sam_file_list:
    #samplename = os.path.basename(file).split('.')[0]
    BAM = os.path.join(output_dir, sampleId + '_sorted.bam')
    METRICS = os.path.join(output_dir,sampleId+'_aligment_metrics.txt')
    option1 = ' R=/media/fs02/reference/hg19/hg19.fasta'
    option2 = ' I='
    option3 = ' O='

    #merge_input_string = merge_input_string + ' I=' + file
    tmp_dir = '`pwd`/'+sampleId+'/tmp'
    sort_cmd = picard_more_memory +' SortSam VALIDATION_STRINGENCY=SILENT Sort_Order=coordinate'+ option2 + file + option3 + BAM + ' TMP_DIR=' + tmp_dir
    print sort_cmd
    log.info(sort_cmd)

    print ('======= sorted BAM finished Running =======')
    subprocess.call(sort_cmd,shell=True,stdout=open(os.path.join(output_dir,sampleId+'_sortSam_pipeline_log.txt'),'wt'),stderr=subprocess.STDOUT)

    ## Generate Alignment summary metrics
    align_summary_cmd = picard + ' CollectAlignmentSummaryMetrics' + option1 + option2 + BAM + option3 + METRICS
    print ('======= picard alignment_summary_metrics =======')
    subprocess.call(align_summary_cmd,shell=True,stdout=open(os.path.join(output_dir,sampleId+'_alignment_summary_pipeline_log.txt'),'wt'),stderr=subprocess.STDOUT)

    ## index sorted_BAM
    #inedx_bam = 'samtools index '+BAM
    index_bam = picard +' BuildBamIndex' + option2 +BAM
    print ('======= BAM index Running =======')
    subprocess.call(index_bam,shell=True,stdout=open(os.path.join(output_dir,sampleId+'_indexBAM_pipeline_log.txt'),'wt'),stderr=subprocess.STDOUT)


## RUN GATK
for bam in glob.glob(os.path.join(output_dir,'*_sorted.bam')):
    print "Input BAM file is: ",bam
    #samplename = os.path.basename(bam).split('_sorted.')[0]
    VCF = os.path.join(output_dir,sampleId+'.vcf')
    option1 = ' -R /media/fs02/reference/hg19/hg19.fasta'
    option2 = ' -I '
    option3 = ' -o '
    option4 = ' -glm BOTH'
    print ('======= GATK unifiedGenotyper Running =======')
    GATK_cmd =gatk_more_memory + ' -T UnifiedGenotyper' + option1 + option2 + bam + option3 + VCF + option4
    subprocess.call(GATK_cmd, shell=True,
                    stdout=open(os.path.join(output_dir, sampleId + '_GATK_pipeline_log.txt'), 'wt'),
                    stderr=subprocess.STDOUT)
    print ('======= pipeline finished!!!=======')

## remove sam file
for file in sam_file_list:
    ## remover sam file to save space
    os.remove(os.path.abspath(file))
