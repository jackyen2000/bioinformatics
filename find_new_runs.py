import sys,re,os,argparse,glob,errno,time,glob
import logging as log
import subprocess
import luigi

os.chdir(r'/media/fs02/Rutherford_data/HCP_data/test')

#parser = argparse.ArgumentParser()
#parser.add_argument('-r',dest='runName', required=True)
#parser.add_argument('-s',dest='sampleId',required=False)
#
#args = parser.parse_args()
#
# ## use runName as argument
#runName = args.runName
#sampleID = args.sampleId

#work_dir = r'/Volumes/lab data/Rutherford_data/HCP_data/'
WORK_DIR  = r'/media/fs02/Rutherford_data/HCP_data/'

## reference
REFERENCE = r'/media/fs02/reference/hg19/hg19.fasta'

#software BWA, samtools
PICARD_JAR = '/home/lee/NGS/picard.jar'
picard              = 'java -jar '+ PICARD_JAR
picard_more_memory  = 'java -jar -Xmx20g ' + PICARD_JAR


# FASTQ
read1_lanes = []
read2_lanes = []
# r1_pattern = re.compile(r'.*L\d{3}_R1_\d{3}_001.fastq\.gz')
r1_pattern = re.compile(r'.*_R1_001.fastq.gz')
# r2_pattern = re.compile(r'.*L\d{3}_R2_\d{3}_001.fastq\.gz')
r2_pattern = re.compile(r'.*_R2_001.fastq.gz')




class FindFASTQTask(luigi.Task):
    runName = luigi.Parameter()
    FASTQ_DIR = luigi.Parameter()
    OUTPUT_DIR = luigi.Parameter()

    def output(self):
        timestamp = time.strftime('%Y%m%d.%H%M%S', time.localtime())
        return luigi.LocalTarget('output/log_CheckFASTQTask_%s.txt' %(timestamp))

    def run(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-r', dest='runName', required=True)
        # parser.add_argument('-s',dest='sampleId',required=False)
        #
        args = parser.parse_args()
        #
        # ## use runName as argument
        runName = args.runName

        FASTQ_DIR = os.path.join(WORK_DIR, self.runName, 'Data/Intensities/BaseCalls')
        if not os.path.exists(FASTQ_DIR):
            log.error("FASTQ_Dir does not exist: %s" % FASTQ_DIR)
            sys.exit(1)

        print 'The FASTQ directory is at: ', FASTQ_DIR

        for fastq in glob.glob(os.path.join(FASTQ_DIR, '*.fastq.gz')):
            #print fastq
            if r1_pattern.match(fastq):
                read1_lanes.append(fastq)
            elif r2_pattern.match(fastq):
                read2_lanes.append(fastq)
            else:
                log.warn("FASTQ File %s did not match pattern", fastq)

        OUTPUT_DIR = os.path.join(FASTQ_DIR, 'pipeline_output')
        try:
            os.makedirs(OUTPUT_DIR)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

        with self.output().open('w') as outfile:
            outfile.write("Found %d lanes for sample %s", len(read1_lanes))
            #log.info("Found %d lanes for sample %s", len(read1_lanes))
        print 'FASTQ files: ',read1_lanes, read2_lanes
        print "======== Check FASTQ Files =========="



class RunBWATask(luigi.Task):
    runName = luigi.Parameter()
    FASTQ_DIR = luigi.Parameter()
    OUTPUT_DIR = luigi.Parameter()
    sampleName = luigi.Parameter()
    sam_file_list = luigi.Parameter()
    
    def output(self):
        timestamp = time.strftime('%Y%m%d.%H%M%S', time.localtime())
        return luigi.LocalTarget('output/log_RunBWATask_%s.txt' %(timestamp))

    def requires(self):
        return FindFASTQTask(self)

    def run(self):
        sam_file_list = []
        for index, file in enumerate(read1_lanes):
            # Alignment inputs
            read1 = read1_lanes[index]
            read2 = read2_lanes[index]

            # Alignment outputs
            # lane = index + 1
            # sam        = os.path.join(output_dir,'lane' + str(lane) + '.sam')

            sampleName = os.path.basename(read1).split("_R1_001")[0]
            sam = os.path.join(self.OUTPUT_DIR, self.sampleName + '.sam')

            print sampleName
        RG_Tag = '"@RG\tID:' + self.runName + '\tPU:' + '\tSM:' + self.sampleName + '"'
        bwa_cmd = 'bwa mem' + ' -t 20' + ' -v 3 ' + ' -R ' + RG_Tag + ' ' + '"' + REFERENCE + '"' + ' ' + '"' + read1 + '"' + ' ' + '"' + read2 + '"' + ' > ' + sam
        samtools_convert = 'samtools view -S -b'
        samtools_sort = 'samtools sort -o ' + ' ' + '>' + ' ' + self.sampleName + '_sorted.bam'
        print bwa_cmd
        # print samtools_sort
        ## use subprocess to execute the bash commands
        # outfile = open(samplename + '_sorted.bam','w')
        log.info(bwa_cmd)
        bwa_process = subprocess.call(bwa_cmd, shell=True)
        sam_file_list.append(sam)
        print sam

        print "======== Running BWA =========="

class ConvertSAMToSortedBAMTask(luigi.task):
    runName = luigi.Parameter()
    FASTQ_DIR = luigi.Parameter()
    OUTPUT_DIR = luigi.Parameter()
    sampleName = luigi.Parameter()
    sam_file_list = luigi.Parameter()

    def output(self):
        timestamp = time.strftime('%Y%m%d.%H%M%S', time.localtime())
        return luigi.LocalTarget('output/log_ConvertSamToSortBAMTask_%s.txt' %(timestamp))


    def run(self):
        for file in self.sam_file_list:
            BAM = os.path.join(self.OUTPUT_DIR, os.path.basename(file) + 'sorted_bam.bam')
            sort_cmd = picard + ' SortSam VALIDATION_STRINGENCY=SILENT Sort_Order=coordinate' + 'I=' + file + ' O=' + BAM
            print sort_cmd
            log.info(sort_cmd)
            subprocess.call(sort_cmd, shell=True)
        print "======== ConvertSAMtoSortedBAM =========="

if __name__=='__main__':
    luigi.run(main_task_cls=FindFASTQTask)
