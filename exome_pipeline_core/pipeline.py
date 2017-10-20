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
# #
# # Sep 25th, 2017
# # EDIT: test trimming options
# #
# # Sep26th, 2017
# # EDIT: add surecalltrimmer instead of Trimmomatic
# #===========================================================================##
# #===========================================================================##
# # All of the general library calls and PATH
# #===========================================================================##
'''

'''
USAGE:
python pipeline.py -w <work_dir> -r <runName> -s <sampleId> -t <tmp_dir> <optional:--trimming/--no-trimming>
'''



#!/usr/bin/python
'''
import packages
'''
import sys,re,os,argparse,glob,errno
import shutil
import logging as log
from subprocess import Popen, PIPE
import subprocess
from slackclient import SlackClient
from pandas import *
import glob
from qc_metrics import *

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
work_dir = args.work_dir
trimming = args.trimming

#### Slack authentication
slack_client = SlackClient(SLACK_TOKEN)

def send_message(channel_id, message):
   slack_client.api_call(
         "chat.postMessage",
         channel=channel_id,
         text=message,
         username='pipeline',
         icon_emoji=':bulb:',
   )

DATA_DIR   = '/media/NGS_data'
fastq_dir  = os.path.join(work_dir,runName,sampleId)

## TODO change output_dir to NGS_data ...
output_dir = os.path.join(work_dir,runName,sampleId,'pipeline_output')
#output_dir = os.path.join(DATA_DIR,runName,sampleId,'pipeline_output')

print 'the FASTQ directory is at: ',fastq_dir
## reference
#reference_test = r'/Volumes/lab data/reference/hg19/hg19.fasta'
reference = r'/media/fs02/reference/hg19/hg19.fasta'
adapter = 'ILLUMINACLIP:/home/lee/NGS/Trimmomatic-0.36/adapters/TruSeq3-PE.fa:2:30:10'

# this is the QXT
#adapter = 'ILLUMINACLIP:/home/lee/NGS/Trimmomatic-0.36/adapters/QXTIllumina-PE.fa:2:30:10'

'''
Define reference and software BWA, samtools, PICARD, GATK, Trimmomatic
'''


PICARD_JAR = '/home/lee/NGS/picard.jar'
picard              = 'java -jar '+ PICARD_JAR
picard_more_memory  = 'java -jar -Xmx20g ' + PICARD_JAR

TRIMMOMATIC_JAR = '/home/lee/NGS/Trimmomatic-0.36/trimmomatic-0.36.jar'
trimmomatic     = 'java -jar '+TRIMMOMATIC_JAR

SURECALLTRIMMER_JAR = '/home/lee/NGS/AGeNT/SurecallTrimmer_v4.0.1.jar'
surecalltrimmer     = 'java -jar '+SURECALLTRIMMER_JAR

GATK_JAR = '/home/lee/NGS/GenomeAnalysisTK.jar'
gatk     = 'java -jar -Xmx2g '+GATK_JAR
gatk_more_memory = 'java -jar -Xmx10g '+GATK_JAR


## FASTQ - checking FASTQ file format & Perform FASTQC
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
    #print FASTQC
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

try:
    os.makedirs(output_dir)
except OSError as exception:
    if exception.errno != errno.EEXIST:
        raise


## Agilent SurecallTrimmer
### if not batch, execute by individual sampleID
if trimming:
    for index,file in enumerate(read1_lanes):
        # surecall inputs
        read1 = read1_lanes[index]
        read2 = read2_lanes[index]

        # surecalltrimmer outputs
        lane = index + 1

        # surecalltrimmer command
        trim_option1 = ' -fq1 '
        trim_option2 = ' -fq2 '
        trim_option3 = ' -qxt'
        trim_option4 = ' -qualityTrimming 20 -minFractionRead 50 -idee_fixe'
        trim_option5 = ' -out_loc '

        trim_cmd = surecalltrimmer + trim_option1 + read1 + trim_option2 + read2 + trim_option3 + trim_option4 + trim_option5 + fastq_dir
        #cmd += 'CROP:' + str(crop)
        os.chdir(fastq_dir)
        #log.info(cmd)
        print "====== Running SureCall Trimmer ======="
        subprocess.call(trim_cmd, shell=True,
                                      stdout=open(os.path.join(output_dir, sampleId + '_trim_pipeline_log.txt'), 'wt'),
                                      stderr=subprocess.STDOUT)

        #os.system(cmd)
    read1_lanes_trimmed = []
    read2_lanes_trimmed = []
    r1_pattern = re.compile(r'.*\_R1_001.*\_Cut\_0\.fastq\.gz')
    r2_pattern = re.compile(r'.*\_R2_001.*\_Cut\_0\.fastq\.gz')


    for fastq in glob.glob(os.path.join(fastq_dir,'*.fastq.gz')):
        print fastq
        #print fastq
        if r1_pattern.match(fastq):
            read1_lanes_trimmed.append(fastq)

        elif r2_pattern.match(fastq):
            read2_lanes_trimmed.append(fastq)
        else:
            log.warn("FASTQ File %s did not match pattern", fastq)

    read1_lanes = read1_lanes_trimmed
    read2_lanes = read2_lanes_trimmed

    log.info("Found %d lanes for sample %s", len(read1_lanes))
    print 'Trimmed FASTQ files: ',read1_lanes, read2_lanes


## Run FASTQC
#fastqc_cmd = 'fastqc ' + read1_lanes + ' '+ read2_lanes +' -o ' + output_dir
fastqc_cmd = 'fastqc ' + ''.join(map(str, read1_lanes)) + ' '+ ''.join(map(str, read2_lanes)) +' -o ' + output_dir

print "====== Running FASTQC ======="
subprocess.call(fastqc_cmd, shell=True,
                stdout=open(os.path.join(output_dir, sampleId + '_fastqc_pipeline_log.txt'), 'wt'),
                stderr=subprocess.STDOUT)


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
    subprocess.call(bwa_cmd,shell=True,stdout=open(os.path.join(output_dir,sampleId+'_bwa_pipeline_log.txt'),'wt'),stderr=subprocess.STDOUT)
    #bwa_process = subprocess.Popen(bwa_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True)
    #stdout, stderr = bwa_process.communicate()
    sam_file_list.append(sam)
    print 'sam files: ',sam


## Merge SAM Files and Sort

## Create a list of files to merge
## Picard SortSam can convert SAM to BAM and sort
dedup_bam_list = []
for file in sam_file_list:
    #samplename = os.path.basename(file).split('.')[0]
    BAM = os.path.join(output_dir, sampleId + '_sorted.bam')
    BAI = os.path.join(output_dir, sampleId + '_sorted.bai')
    DEDUP_BAM = os.path.join(output_dir, sampleId + '_sorted_dedup.bam')
    DEDUP_METRICS = os.path.join(output_dir,sampleId+'_sorted_dedup_metrics.txt')
    HS_METRICS    = os.path.join(output_dir,sampleId+'_HSmetrics.txt')

    ALIGNMENT_METRICS = os.path.join(output_dir,sampleId+'_aligment_metrics.txt')
    option1 = ' R=/media/fs02/reference/hg19/hg19.fasta'
    option2 = ' I='
    option3 = ' O='
    option4 = ' CREATE_INDEX=TRUE'
    option5 = ' M='

    HS_option1 = ' CollectHsMetrics VALIDATION_STRINGENCY=SILENT'
    HS_option2 = ' REFERENCE_SEQUENCE=/media/fs02/reference/hg19/hg19.fasta'
    HS_option3 = ' BI=/media/fs02/reference/hg19/bait.list.interval_list'
    HS_option4 = ' TI=/media/fs02/reference/hg19/target.list.interval_list'

    #merge_input_string = merge_input_string + ' I=' + file
    tmp_dir = '`pwd`/pipeline_output/tmp'
    sort_cmd = picard_more_memory +' SortSam VALIDATION_STRINGENCY=SILENT Sort_Order=coordinate'+ option2 + file + option3 + BAM + ' TMP_DIR=' + tmp_dir + option4
    print sort_cmd
    log.info(sort_cmd)

    print ('======= sorted BAM Running =======')
    subprocess.call(sort_cmd,shell=True,stdout=open(os.path.join(output_dir,sampleId+'_sortSam_pipeline_log.txt'),'wt'),stderr=subprocess.STDOUT)

    ## markDuplication
    dedup_cmd = picard_more_memory +' MarkDuplicates REMOVE_DUPLICATES=TRUE VALIDATION_STRINGENCY=SILENT'+option4+option2+BAM+option3+DEDUP_BAM+option5+DEDUP_METRICS
    print ('======= markDuplicates Running =======')
    subprocess.call(dedup_cmd,shell=True,stdout=open(os.path.join(output_dir,sampleId+'_deDup_pipeline_log.txt'),'wt'),stderr=subprocess.STDOUT)

    ## Generate Alignment summary metrics
    align_summary_cmd = picard_more_memory+' CollectAlignmentSummaryMetrics' + option1 + option2 + DEDUP_BAM + option3 + ALIGNMENT_METRICS
    print ('======= picard alignment_summary_metrics =======')
    subprocess.call(align_summary_cmd,shell=True,stdout=open(os.path.join(output_dir,sampleId+'_alignment_summary_pipeline_log.txt'),'wt'),stderr=subprocess.STDOUT)

    ## Generate HSMetrics
    HS_Metrics_cmd = picard_more_memory+HS_option1+HS_option2+HS_option3+HS_option4+option2+DEDUP_BAM+option3+HS_METRICS
    print ('======= picard HS_metrics =======')
    subprocess.call(HS_Metrics_cmd,shell=True,stdout=open(os.path.join(output_dir,sampleId+'_HSmetrics_pipeline_log.txt'),'wt'),stderr=subprocess.STDOUT)

    ## remove sorted_BAM file and _sorted_BAI index
    os.remove(os.path.abspath(BAM))
    os.remove(os.path.abspath(BAI))

    ## remove PICARD tmp directory
    shutil.rmtree(tmp_dir, ignore_errors=False, onerror=None)
    dedup_bam_list.append(DEDUP_BAM)
    print 'dedup BAM: ',DEDUP_BAM

## RUN GATK on dedup BAM
for bam in glob.glob(os.path.join(output_dir,'*_sorted_dedup.bam')):
    print "Input BAM file is: ",bam
    #samplename = os.path.basename(bam).split('_sorted.')[0]
    VCF = os.path.join(output_dir,sampleId+'.vcf')
    option1 = ' -R /media/fs02/reference/hg19/hg19.fasta'
    option2 = ' -I '
    option3 = ' -o '
    option4 = ' -glm BOTH'
    option5 = ' -nct 10 '
    option6 = ' -nt 10 '
    option7 = ' -stand_call_conf 20'
    print ('======= GATK unifiedGenotyper Running =======')
    GATK_cmd =gatk_more_memory + ' -T UnifiedGenotyper' + option5 + option6 + option1 + option2 + bam + option3 + VCF + option4 + option7
    subprocess.call(GATK_cmd, shell=True,
                    stdout=open(os.path.join(output_dir, sampleId + '_GATK_pipeline_log.txt'), 'wt'),
                    stderr=subprocess.STDOUT)
    print GATK_cmd
    print ('======= pipeline finished!!!=======')

## remove sam file
for file in sam_file_list:
    ## remover sam file to save space
    os.remove(os.path.abspath(file))


## Generating QC metrics report\
## Step 1. Convert BAM to BED, make coverage depth file
## Step 2. Collect all QC metrics and put together to csv file
print ('======= Calculating QC_metrics Report =======')
collect_Bedtools_coverage(work_dir,runName,sampleId)
collect_Final_QCMetrics(work_dir,runName)


## send slack message
message = 'Congratulations! Analysis for Run: '+runName+' Sample: '+sampleId+' is Finished! :beers: :thumbsup: :facepunch:'
send_message('exome-pipeline', message)
print 'Slack Message has been sent'

