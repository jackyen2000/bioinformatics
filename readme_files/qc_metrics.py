'''
# #===========================================================================##
# # qc_metrics.py
# #
# # Version 1.0
# # 1. collect all metrics.txt file and extract the information needed
# #
# # Jack Yen
# # Oct 3rd, 2017
# # EDIT: add trimming options, re-direct log into individual txt files for each steps.
# #===========================================================================##



# #===========================================================================##
# # All of the general library calls and PATH
# #===========================================================================##
'''
import os
from pandas import *
import glob
import time
import subprocess
timestamp = time.strftime('%Y%m%d.%H%M%S', time.localtime())

## this function makes the coverage metrics
def collect_QCMetrics(work_dir,runName):
    HS_METRICS_PATH = glob.glob(os.path.join(work_dir, runName, '*/pipeline_output/*_exomeHSmetrics.txt'))
    DEDUP_METRICS_PATH = glob.glob(os.path.join(work_dir, runName, '*/pipeline_output/*dedup_metrics.txt'))

    appended_HS_data = []
    for file in HS_METRICS_PATH:
        sample_id = file.split('/')[-1].split('_sorted_')[0]
        HS_METRICS_DF = pandas.read_csv(file, sep='\t', skiprows=range(0, 5), nrows=1, header=1)
        HS_METRICS_DF['SAMPLE_ID'] = file.split('/')[-1].split('_sorted_')[0]
        HS_METRICS_DF.index = HS_METRICS_DF['SAMPLE_ID']
        appended_HS_data.append(HS_METRICS_DF.transpose())
    appended_HS_data = pandas.concat(appended_HS_data, axis=1)

    appended_DEDUO_data = []
    for file2 in DEDUP_METRICS_PATH:
        sample_id = file2.split('/')[-1].split('_sorted_')[0]
        DEDUP_METRICS_DF = pandas.read_csv(file2, sep='\t', skiprows=range(0, 5), nrows=1, header=1)
        DEDUP_METRICS_DF['SAMPLE_ID'] = file2.split('/')[-1].split('_sorted_')[0]
        DEDUP_METRICS_DF.index = DEDUP_METRICS_DF['SAMPLE_ID']
        appended_DEDUO_data.append(DEDUP_METRICS_DF.transpose())
    appended_DEDUO_data = pandas.concat(appended_DEDUO_data, axis=1)

    total = []
    frames = [appended_HS_data,appended_DEDUO_data]
    total = pandas.concat(frames)
    total.loc['0.2*MEAN_TARGET_COVERAGE'] = 0.2 * total.loc['MEAN_TARGET_COVERAGE']
    total_select = total.loc[['TOTAL_READS','PF_UNIQUE_READS','ON_TARGET_BASES','MEAN_BAIT_COVERAGE','MEAN_TARGET_COVERAGE',
                                  'PCT_TARGET_BASES_1X','PCT_TARGET_BASES_2X','PCT_TARGET_BASES_10X','PCT_TARGET_BASES_20X',
                                  'PCT_TARGET_BASES_30X', 'PCT_TARGET_BASES_40X', 'PCT_TARGET_BASES_50X', 'PCT_TARGET_BASES_100X',
                                  'READ_PAIRS_EXAMINED','READ_PAIR_DUPLICATES','PERCENT_DUPLICATION','0.2*MEAN_TARGET_COVERAGE']]
    #total_select.to_csv(os.path.join(work_dir,runName,runName+'.txt'),sep='\t')
    #total_select.to_csv(os.path.join(work_dir, runName, runName + 'metrics_%s.txt') % (timestamp),sep='\t')

    return total_select


### this function 1. convert BAM to BED
###               2. make coverage depth file in target region
def collect_Bedtools_coverage(work_dir,runName):
    target_bed  = '/media/fs02/reference/hg19/sureselect_QXT_S07604514_Regions.bed'
    #bed_gz = os.path.join(work_dir,runName,'*/sorted_dedup.bed.gz')
    #coverage_gz = os.path.join(work_dir,runName,'*/pipeline_output/coverage.tsv.gz')
    bam = os.path.join(work_dir,runName,'*/pipeline_output/*_sorted_duplicates.bam')

    for dir in os.listdir(os.path.join(work_dir,runName)):
        if "CS" in dir:
            bed_gz = os.path.join(work_dir, runName, dir,'pipeline_output',dir+'_sorted_dedup.bed.gz')
            coverage_gz = os.path.join(work_dir, runName, dir,'pipeline_output',dir+'_coverage.tsv.gz')
            print 'sampleID: ',dir
            ## convert bam to bed
            bamtobed_cmd = 'bedtools bamtobed'+' -i '+bam+' | gzip > '+bed_gz
            print '==== convert bam to bed ====='
            subprocess.call(bamtobed_cmd, shell=True)

            ## make coverage file
            coverage_cmd = 'bedtools coverage'+' -a '+target_bed+' -b '+bed_gz+' -d | gzip > '+coverage_gz
            print '==== make coverage file ====='
            subprocess.call(coverage_cmd,shell=True)
    #collect_Total_Target_Base(work_dir,runName)
    return

total_target_base_int = int()
def collect_Total_Target_Base(work_dir,runName):

    coverage_gz = os.path.join(work_dir,runName,'*/pipeline_output/coverage.tsv.gz')
    ## calculate total base on target
    total_target_base_cmd = 'gunzip -c ' + coverage_gz + ' | wc -l'
    proc = subprocess.Popen(total_target_base_cmd, stdout=subprocess.PIPE, shell=True)
    total_target_base = proc.stdout.read()
    total_target_base_int = int(total_target_base)

    return total_target_base_int



def collect_Uniformity_metrics(work_dir,runName):
    target_bed  = '/media/fs02/reference/hg19/sureselect_QXT_S07604514_Regions.bed'
    bed_gz = 'sorted_dedup.bed.gz'
    coverage_gz = os.path.join(work_dir,runName,'*/pipeline_output/coverage.tsv.gz')
    bam = os.path.join(work_dir,runName,'*/pipeline_output/*sorted_duplicates.bam')

    for dir in os.listdir(os.path.join(work_dir,runName)):
        if "CS" in dir:

            ## calculate the bases > 0.2*mean_target_coverage
            coverage_df = collect_QCMetrics(work_dir,runName)

            df = pandas.DataFrame()
            for sample in coverage_df:
                if sample == dir:
                    total_base_greater_mean_cov_cmd = "gunzip -c "+coverage_gz+" | awk '$6>"+str(coverage_df[sample].loc['0.2*MEAN_TARGET_COVERAGE'])+" {print}' | wc -l"
                    print coverage_gz
                    task= subprocess.Popen(total_base_greater_mean_cov_cmd,stdout=subprocess.PIPE,shell=True)
                    for line in task.stdout:
                        print line
                        df.concat([df,line])
                    task.wait()

    return