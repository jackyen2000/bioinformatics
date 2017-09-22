from subprocess import check_output
import subprocess
import sys,re,os,glob,errno
import logging as log
import luigi
import os
import random
import argparse
import time

#faking the pipline for now

#sample_list = ["GP140-10A_S19","GP140-10B_S20","GP140-11A_S21","GP140-11B_S22","GP140-1A_S1","GP140-1B_S2","GP140-2A_S3","GP140-2B_S4","GP140-3A_S5","GP140-3B_S6","GP140-4A_S7","GP140-4B_S8","GP140-5A_S9","GP140-5B_S10","GP140-6A_S11","GP140-6B_S12","GP140-7A_S13","GP140-7B_S14","GP140-8A_S15","GP140-8B_S16","GP140-9A_S17","GP140-9B_S18"]


#WORK_DIR = '/media/NGS_data/BaseSpace_exome'


#parser = argparse.ArgumentParser()
#parser.add_argument('-w', dest='work_dir', help=('full path of working directory'), required=True)
#parser.add_argument('-r', dest='runName', help=('full path of running directory with data'), required=True)
#parser.add_argument('-s', dest='sample', help=('option to execute individually by sampleId'), required=False)

#parser.add_argument('--trimming', dest='trimming', action='store_true')
#parser.add_argument('--no-trimming', dest='trimming', action='store_false')
#parser.set_defaults(trimming=False)

# parser.add_argument('-d', dest='tmp_dir', default='/scratch')

#args = parser.parse_args()
#runName = args.runName
#sampleId = args.sampleId
# tmp_dir = args.tmp_dir
#work_dir = args.work_dir
#trimming = args.trimming

## definition
reference = r'/media/fs02/reference/hg19/hg19.fasta'
PICARD_JAR = '/home/lee/NGS/picard.jar'
picard              = 'java -jar '+ PICARD_JAR
picard_more_memory  = 'java -jar -Xmx20g ' + PICARD_JAR

TRIMMOMATIC_JAR = '/home/lee/NGS/Trimmomatic-0.36/trimmomatic-0.36.jar'
trimmomatic     = 'java -jar '+TRIMMOMATIC_JAR

GATK_JAR = '/home/lee/NGS/GenomeAnalysisTK.jar'
gatk     = 'java -jar -Xmx2g '+GATK_JAR
gatk_more_memory = 'java -jar -Xmx20g '+GATK_JAR
sam_file_list = []


data_dir = '/media/NGS_data/scratch/'
#fastq_dir = '/media/NGS_data/scratch/HiSeq_2500_v2_TruSeq_Exome_9_replicates_of_NA12878/NA12878_A014_S8'
runName = 'HiSeq_2500_v2_TruSeq_Exome_9_replicates_of_NA12878'
sample_list  = ['NA12878_A014_S8','NA12878_A005_S3']

fastq_dir = []
output_dir= []
for sample in sample_list:
    #print sample
    fastq_dir.append(os.path.join(data_dir,runName,sample))
    output_dir.append(os.path.join(data_dir,runName,sample,'pipeline_output'))

trimming = '--no-trimming'


## sample list
#sample_list = args.sampleId
#class TaskVariable(luigi.Task):
#    fastq_dir = luigi.Parameter()
#    output_dir = luigi.Parameter()
#    def output(self):
#        fastq_dir   = os.path.join(GlobalConfig().work_dir,GlobalConfig().runName,GlobalConfig().sampleId)
#        output_dir  = os.path.join(fastq_dir,'pipeline_output')
#        return fastq_dir,output_dir

#print GlobalConfig().work_dir,GlobalConfig().runName,GlobalConfig().sampleId

## FASTQ - checking FASTQ file format
for fastq_dir_item in fastq_dir:
    if not os.path.exists(fastq_dir_item):
        #print item
        log.error("FASTQ_Dir does not exist: %s" % fastq_dir_item)
        sys.exit(1)

    read1_lanes = []
    read2_lanes = []
    #r1_pattern = re.compile(r'.*L\d{3}_R1_\d{3}_001.fastq\.gz')
    r1_pattern = re.compile(r'.*_R1_001.fastq.gz')
    #r2_pattern = re.compile(r'.*L\d{3}_R2_\d{3}_001.fastq\.gz')
    r2_pattern = re.compile(r'.*_R2_001.fastq.gz')


    for fastq in glob.glob(os.path.join(fastq_dir_item,'*.fastq.gz')):
        print fastq
        #print fastq
        if r1_pattern.match(fastq):
            read1_lanes.append(fastq)
        elif r2_pattern.match(fastq):
            read2_lanes.append(fastq)
        else:
            log.warn("FASTQ File %s did not match pattern", fastq)

    log.info("Found %d lanes for sample %s", len(read1_lanes), sample_list)
    print 'FASTQ files: ',read1_lanes, read2_lanes

    try:
        os.makedirs(output_dir)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


#def run_cmd(cmd):
#    p = subprocess.call(cmd, shell=False, universal_newlines=True, stdout=subprocess.PIPE)
#    ret_code = p.wait()
#    output = p.communicate()[0]
#    return output

class BwaMemTask(luigi.ExternalTask):

    # Ideally we have to show this but for now I am gonna fake it by creating a list of sample IDs
    # fastq_path = luigi.Parameter()

    sample = luigi.Parameter()

    #genome = luigi.Parameter()

    #def requires(self):
    #    return [LoadFastq(sample) for sample in sample_list]

    def output(self):
        #return luigi.LocalTarget("sam/%s.sam" % self.sample)
        #timestamp = time.strftime('%Y%m%d.%H%M%S', time.localtime())
        return luigi.LocalTarget(os.path.join(output_dir,self.sample+'bwa_pipeline_log.txt' ))

    def run(self):
        ## FASTQ - checking FASTQ file format
        for index, file in enumerate(read1_lanes):
            read1 = read1_lanes[index]
            read2 = read2_lanes[index]

            # Alignment outputs
            lane = index + 1
            sam = os.path.join(output_dir, self.sample + '.sam')

        RG_Tag = '"@RG\tID:' + runName + '\tPU:' + str(lane) + '\tSM:' + self.sample + '"'
        bwa_cmd = 'bwa mem' + ' -t 20' + ' -v 3 ' + ' -R ' + RG_Tag + ' ' + '"' + reference + '"' + ' ' + '"' + read1 + '"' + ' ' + '"' + read2 + '"' + ' > ' + sam
        log.info(bwa_cmd)

        print "====== Running BWA ======"
        bwa_process = subprocess.call(bwa_cmd, shell=True,
                                      stdout=open(os.path.join(output_dir, self.sample + '_bwa_pipeline_log.txt'), 'wt'),
                                      stderr=subprocess.STDOUT)
        sam_file_list.append(sam)

        print 'SAM Files: ',sam
        #tmp = run_cmd(["bwa",
        #             "mem",
        #             reference,
        #             "fastq/"+self.sample+"_L001_R1_001.fastq",
        #             "fastq/"+self.sample+"_L001_R2_001.fastq"])
        #with self.output().open('w') as sam_out:
        #    sam_out.write(tmp)


class SortBamTask(luigi.ExternalTask):

    sample   = luigi.Parameter()
    BAM = luigi.Parameter()
    #genome = luigi.Parameter()

    def requires(self):
        return BwaMemTask(self.sample)

    def output(self):
        #timestamp = time.strftime('%Y%m%d.%H%M%S', time.localtime())
        return luigi.LocalTarget(os.path.join(output_dir, self.sample+'SortBAM_pipeline_log.txt' ))

    def run(self):
        for file in sam_file_list:
            # samplename = os.path.basename(file).split('.')[0]
            BAM = os.path.join(output_dir, self.sample + '_sorted.bam')
            METRICS = os.path.join(output_dir, self.sample + '_aligment_metrics.txt')
            option1 = ' R=/media/fs02/reference/hg19/hg19.fasta'
            option2 = ' I='
            option3 = ' O='

        tmp_dir = '`pwd`/' + self.sample + '/tmp'
        sort_cmd = picard_more_memory + ' SortSam VALIDATION_STRINGENCY=SILENT Sort_Order=coordinate' + option2 + file + option3 + BAM + ' TMP_DIR=' + tmp_dir
        print sort_cmd
        log.info(sort_cmd)

        print ('======= sorted BAM finished Running =======')
        subprocess.call(sort_cmd, shell=True,
                        stdout=open(os.path.join(output_dir, self.sample + '_sortSam_pipeline_log.txt'), 'wt'),
                        stderr=subprocess.STDOUT)

        ## Generate Alignment summary metrics
        align_summary_cmd = picard + ' CollectAlignmentSummaryMetrics' + option1 + option2 + BAM + option3 + METRICS
        print ('======= picard alignment_summary_metrics =======')
        subprocess.call(align_summary_cmd, shell=True,
                        stdout=open(os.path.join(output_dir, self.sample + '_alignment_summary_pipeline_log.txt'), 'wt'),
                        stderr=subprocess.STDOUT)

        #tmp = run_cmd(["samtools",
        #               "view",
        #               "-bS",
        #               "sam/"+self.sample+".sam"])
        #with self.output().open('w') as bam_out:
        #    bam_out.write(tmp)

class IndexBamTask(luigi.ExternalTask):


    sample   = luigi.Parameter()
    BAM = luigi.Parameter()


    def output(self):
        print "Indexing ... Done"
        #timestamp = time.strftime('%Y%m%d.%H%M%S', time.localtime())
        return luigi.LocalTarget(os.path.join(output_dir, self.sample+'IndexBAM_pipeline_log_%s.txt'))

    def requires(self):
        return SortBamTask(self.sample,self.BAM)
    def run(self):
        option2 = ' I='
        index_bam = picard + ' BuildBamIndex' + option2 + self.BAM
        print ('======= BAM index Running =======')
        subprocess.call(index_bam, shell=True,
                        stdout=open(os.path.join(output_dir, self.sample + '_indexBAM_pipeline_log.txt'), 'wt'),
                        stderr=subprocess.STDOUT)

        #tmp = run_cmd(["samtools",
        #               "index",
        #               "bam/"+self.sample+".sorted.bam"])


class CallVariantTask(luigi.ExternalTask):

    sample   = luigi.Parameter()
    BAM = luigi.Parameter()

    def requires(self):
        return IndexBamTask(self.sample,self.BAM)

    def output(self):
        #timestamp = time.strftime('%Y%m%d.%H%M%S', time.localtime())
        return luigi.LocalTarget(os.path.join(output_dir, self.sample+'GATK_pipeline_log_%s.txt'))

    def run(self):
        print "Input BAM file is: ", self.BAM
        # samplename = os.path.basename(bam).split('_sorted.')[0]
        VCF = os.path.join(output_dir, self.sample + '.vcf')
        option1 = ' -R /media/fs02/reference/hg19/hg19.fasta'
        option2 = ' -I '
        option3 = ' -o '
        option4 = ' -glm BOTH'
        print ('======= GATK unifiedGenotyper Running =======')
        GATK_cmd = gatk_more_memory + ' -T UnifiedGenotyper' + option1 + option2 + self.BAM + option3 + VCF + option4
        subprocess.call(GATK_cmd, shell=True,
                        stdout=open(os.path.join(output_dir, self.sample + '_GATK_pipeline_log.txt'), 'wt'),
                        stderr=subprocess.STDOUT)
        print ('======= pipeline finished!!!=======')

        for file in sam_file_list:
            os.remove(os.path.abspath(file))

        #tmp = run_cmd(["samtools",
        #               "mpileup",
        #               "-u",
        #               "-f",
        #               reference,
        #               "bam/"+self.sample+".sorted.bam"])
        #with self.output().open("w") as bcf_file:
        #    bcf_file.write(tmp)

class CustomGenomePipelineTask(luigi.Task):

    def requires(self):
        #return [Convert_Bcf_Vcf(sample) for sample in sample_list]
        #work_dir = WORK_DIR
        #tasks = [CallVariantTask(sample) for sample in sample_list]
        tasks = []
        for sample in sample_list:
            BAM = os.path.join(output_dir, sample + '_sorted.bam')
            tasks.append(CallVariantTask(sample = sample, BAM = BAM))
            tasks.append(IndexBamTask(sample=sample, BAM=BAM))
            tasks.append(SortBamTask(sample=sample, BAM=BAM))
            tasks.append(BwaMemTask(sample=sample))
        return tasks

    def output(self):
        #return luigi.LocalTarget("log.txt")

        timestamp = time.strftime('%Y%m%d.%H%M%S', time.localtime())
        return luigi.LocalTarget(os.path.join(output_dir, 'Exome_pipeline_log_%s.txt' % (timestamp)))

    def run(self):
        print "running..."
        #for sample in sample_list:
            #print sample+"\n"
            #return Convert_Bcf_Vcf(sample)

if __name__=='__main__':
    luigi.run()