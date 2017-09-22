import allel
import os
import glob
from pandas import *
from pandas import ExcelWriter
import argparse


#os.chdir(r'/Volumes/NGS_data/scratch/vcf')

#vcf_reader = vcf.Reader(filename='CS395373_S20_R1_001.molbar.trimmed.deduped.hotspot.ann.vcf')
#callset = allel.read_vcf('CS395373_S20_R1_001.molbar.trimmed.deduped.hotspot.ann.vcf')



args = parser.parse_args()

data = r"/Volumes/NGS_data/scratch/vcf/new_vcf"
#data = args.run_dir
#file_name = args.file_name

#print file_name
df = pandas.DataFrame()
df_2 = pandas.DataFrame()
writer = pandas.ExcelWriter('test2.xlsx',engine='xlsxwriter')
count = 0
for file in  glob.glob(os.path.join(data,"*.vcf")):
    count +=1
    #print os.path.splitext(file)[0].split('/')[-1].split('.')[0]
    sheet = os.path.splitext(file)[0].split('/')[-1].split('.')[0]
    #print count
    #for i in len(file):
    #df = allel.vcf_to_dataframe(file,fields=['CHROM','POS','ID','REF','ALT','QUAL','FILTER','INFO','FORMAT'])

    df = allel.vcf_to_dataframe(file,fields=['*'])

    callset = allel.read_vcf(file,fields=['*'],chunk_length=10000,types={'variants/VF':'f8'})

    #basedf_final['project_id'] = Series(self.project_id, index=basedf_final.index)
    df_2 = DataFrame.from_dict(callset,orient='index')
    df_2_t = df_2.transpose()
    #df['AD'] = df_2_t['calldata/AD']
    #df['GT'] = df_2_t['calldata/GT']
    df['VF'] = df_2_t['calldata/VF']
    #print df
    #df.to_excel(writer,sheet_name='Sheet'+str(count),header=True,index=False)
    df.to_excel(writer, sheet_name=sheet, header=True, index=False)
writer.save()





