import vcf
import sys
from StringIO import StringIO
import allel
import os
import glob
from pandas import *
from pandas import ExcelWriter
import argparse
from cyvcf2 import VCF
import numpy

work_dir = r"/Users/chiyuyen/Desktop/"
os.chdir(work_dir)
### parse arguments
#parser = argparse.ArgumentParser()
#parser.add_argument('-r',dest='run_dir',help=('full path of running directory wit data'))
#parser.add_argument('-n',dest='file_name',help=('output file name'))


#args = parser.parse_args()

#data = r"/Volumes/NGS_data/scratch/vcf"
#data = args.run_dir
#file_name = args.file_name




#data = r"/Volumes/NGS_data/scratch/vcf/new_vcf"
data = r"/Volumes/NGS_data/scratch/vcf/new_vcf"

#data = r"/Users/chiyuyen/Desktop/new_vcf"

df_vf = pandas.DataFrame()
df = pandas.DataFrame()
df_2 = pandas.DataFrame()

big_dataframe = pandas.DataFrame()


writer = pandas.ExcelWriter('test1.xlsx',engine='xlsxwriter')
count = 0

data_string = ''
for file in  glob.glob(os.path.join(data,"*.vcf")):
    count += 1
    # print os.path.splitext(file)[0].split('/')[-1].split('.')[0]
    sheet = os.path.splitext(file)[0].split('/')[-1].split('.')[0]
    # print count
    # for i in len(file):
    # df = allel.vcf_to_dataframe(file,fields=['CHROM','POS','ID','REF','ALT','QUAL','FILTER','INFO','FORMAT'])

    ## print file name
    print sheet
    df = allel.vcf_to_dataframe(file, fields=['*'])
    callset = allel.read_vcf(file, fields=['*'])

    # basedf_final['project_id'] = Series(self.project_id, index=basedf_final.index)
    df_2 = DataFrame.from_dict(callset, orient='index')
    df_2_t = df_2.transpose()

    ## split string by space and grab last column
    for variant in VCF(file):


        FORMAT =  str(variant).split('	')[-1].replace('./.','0').replace('\n','').split(':')

        #VF = FORMAT[-1]

        #print variant
        #print variant.format('VF')

        VF = variant.format('VF')
        if type(VF) is numpy.ndarray:
            VF = str(VF).replace(" ","").replace("[","").replace("]","")
        else:
            VF = 'NA'
        #print len(FORMAT)
        print VF


        data_string += ''.join(VF) + '\n'+';'

        ## remove last ';' element using [:-1]
        DATA = StringIO('VF'+'\n'+';'+data_string[:-1])
    df_vf = pandas.read_csv(DATA,sep=';')
    df_vf.to_csv("/Users/chiyuyen/Desktop/test.csv")
    #df_vf.index = df.index


    df['AD'] = df_2_t['calldata/AD']
    df['GT'] = df_2_t['calldata/GT']
    df['VF'] = df_vf['VF']
    #big_dataframe = df_2_t.append(df_vf)

    df.to_excel(writer, sheet_name=sheet, header=True, index=False)
writer.save()

print '==== Done !!! ======'







#
#
#
#
#
#
#         TESTDATA = StringIO("""col1;col2;col3
#             1;4.4;99
#             2;4.5;200
#             3;4.7;65
#             4;3.2;140
#             """)
#
#         df = pandas.read_csv(TESTDATA, sep=";")
#
#
#         df = df.append(DataFrame())
#
#         df['VF'] = Series(VF).append(Series(VF))
#         df = pandas.DataFrame
#
#         dict = ['GT', 'AD', 'DP', 'GQ', 'PL', 'MQ', 'GQX', 'VF',FORMAT]
#         print dict
#
#         se = pandas.Series(INFO)
#         if len(se.values) > 6:
#             df['INFO'] = se
#
#         df['INFO'] = DataFrame.from_records(INFO)
#
#
#
#
#         df['VF'] = DataFrame([VF]).append(df['VF'])
#
#         #df = DataFrame([row])
#
#
#         df = DataFrame.from_csv(str(variant))
#
#         #print str(variant)
#
#
#
#
#
#         print variant.INFO.get('GT')
#
#
#         df = DataFrame.from_items(variant.INFO.get('VF'))
#
# for file in  glob.glob(os.path.join(data,"*.vcf")):
#     vcf_reader = vcf.Reader(open(file),'r')
#     for record in vcf_reader:
#         print record
#
#
#
# for file in  glob.glob(os.path.join(data,"*.vcf")):
#     count +=1
#     #print os.path.splitext(file)[0].split('/')[-1].split('.')[0]
#     sheet = os.path.splitext(file)[0].split('/')[-1].split('.')[0]
#     #print count
#     #for i in len(file):
#     #df = allel.vcf_to_dataframe(file,fields=['CHROM','POS','ID','REF','ALT','QUAL','FILTER','INFO','FORMAT'])
