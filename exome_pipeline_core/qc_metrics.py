'''
# #===========================================================================##
# # qc_metrics.py
# #
# # Version 1.0
# # 1. collect all metrics.txt file and extract the information needed
# #
# # Jack Yen
# # Oct, 11th, 2017
# # EDIT: 1. add function to perform BamTOBed and Bedtools coverage
# #       2. calculate (base > 0.2*mean target coverage) / total base on target = uniformity of coverage
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
    HS_METRICS_PATH = glob.glob(os.path.join(work_dir, runName, '*/pipeline_output/*_HSmetrics.txt'))
    DEDUP_METRICS_PATH = glob.glob(os.path.join(work_dir, runName, '*/pipeline_output/*_dedup_metrics.txt'))

    appended_HS_data = []
    for file in HS_METRICS_PATH:
        sample_id = file.split('/')[-1].split('_sorted_')[0]
        HS_METRICS_DF = pandas.read_csv(file, sep='\t', skiprows=range(0, 5), nrows=1, header=1)
        HS_METRICS_DF['SAMPLE_ID'] = file.split('/')[-1].split('_HSmetrics')[0]
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
    return total_select


### this function 1. convert BAM to BED
###               2. make coverage depth file in target region
def collect_Bedtools_coverage(work_dir,runName, sampleId):
    target_bed  = '/media/fs02/reference/hg19/sureselect_QXT_S07604514_Regions.bed'
    #bed_gz = os.path.join(work_dir,runName,'*/sorted_dedup.bed.gz')
    #coverage_gz = os.path.join(work_dir,runName,'*/pipeline_output/coverage.tsv.gz')
    bam = os.path.join(work_dir,runName,sampleId,'pipeline_output/*_sorted_dedup.bam')

    bed_gz = os.path.join(work_dir, runName, sampleId, 'pipeline_output', sampleId+'_sorted_dedup.bed.gz')
    coverage_gz = os.path.join(work_dir, runName, sampleId, 'pipeline_output', sampleId+'_coverage.tsv.gz')
    print 'sampleID: ', sampleId
    ## convert bam to bed
    bamtobed_cmd = 'bedtools bamtobed' + ' -i ' + bam + ' | gzip > ' + bed_gz
    print '==== convert bam to bed ====='
    subprocess.call(bamtobed_cmd, shell=True)

    ## make coverage file
    coverage_cmd = 'bedtools coverage' + ' -a ' + target_bed + ' -b ' + bed_gz + ' -d | gzip > ' + coverage_gz
    print '==== make coverage file ====='
    subprocess.call(coverage_cmd, shell=True)

    print '==== coverage file generated ===='
    return

def collect_Final_QCMetrics(work_dir,runName):
    target_base_df = pandas.DataFrame()
    total_target_base_df = pandas.DataFrame()
    final_qc_dataframe = pandas.DataFrame()
    ## coverage_gz = os.path.join(work_dir,runName,'*/pipeline_output/*_coverage.tsv.gz')

    ## calculate total base on target
    ## calculate the bases > 0.2*mean_target_coverage
    coverage_df = collect_QCMetrics(work_dir, runName)

    for sample in coverage_df:
        coverage_gz = os.path.join(work_dir, runName, sample, 'pipeline_output', sample + '_coverage.tsv.gz')
        print "==== calculate total target base ===="
        total_target_base_cmd = 'gunzip -c ' + coverage_gz + ' | wc -l'
        proc = subprocess.Popen(total_target_base_cmd, stdout=subprocess.PIPE, shell=True)

        print sample
        target_base_df['SAMPLE_ID'] = [sample]
        target_base_df['TOTAL_TARGET_BASE'] = pandas.Series(int(proc.stdout.read()))
        # total_target_base_df = total_target_base_df.append(target_base_df)
        ## transpose dataframe
        # total_target_base_df_t = total_target_base_df.set_index('SAMPLE_ID').T

        total_base_greater_mean_cov_cmd = "gunzip -c " + coverage_gz + " | awk '$6>" + str(
            coverage_df[sample].loc['0.2*MEAN_TARGET_COVERAGE']) + " {print}' | wc -l"
        print 'total base > 0.2*mean_cov_cmd: ', total_base_greater_mean_cov_cmd
        proc2 = subprocess.Popen(total_base_greater_mean_cov_cmd, stdout=subprocess.PIPE, shell=True)
        target_base_df['BASE_GREATER_0.2*MEAN_TARGET_COVERAGE'] = pandas.Series(int(proc2.stdout.read()))
        target_base_df['UNIFORMITY_OF_COVERAGE'] = '{:f}'.format(float( target_base_df['BASE_GREATER_0.2*MEAN_TARGET_COVERAGE'] / \
                                                   target_base_df['TOTAL_TARGET_BASE'] * 100))

        total_target_base_df = total_target_base_df.append(target_base_df)

    ## transpose dataframe
    total_target_base_df_t = total_target_base_df.set_index('SAMPLE_ID').T
    final_qc_dataframe = coverage_df.combine_first(total_target_base_df_t)
    final_qc_dataframe.drop(['TOTAL_TARGET_BASE']).to_csv(os.path.join(work_dir,runName,runName+'_QC_metrics_%s.txt') % (timestamp),sep='\t')

    print final_qc_dataframe

    return
