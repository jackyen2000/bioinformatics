'''
# #===========================================================================##
# # vcf_parser_V3.py
# # EDIT: LATEST THE GREATEST VCF PARSER
# # EDIT: WITH PASS FILTER
# #===========================================================================##
# #===========================================================================##
# # All of the general library calls and PATH
# #===========================================================================##
'''

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

#work_dir = r"/Users/chiyuyen/Desktop/"
#os.chdir(work_dir)
### parse arguments
#parser = argparse.ArgumentParser()
#parser.add_argument('-r',dest='run_dir',help=('full path of running directory wit data'))
#parser.add_argument('-n',dest='file_name',help=('output file name'))


#args = parser.parse_args()

#data = r"/Volumes/NGS_data/scratch/vcf"
#data = args.run_dir
#file_name = args.file_name


data = r"/Users/chiyuyen/Desktop/new_vcf/10_17_2017"

df_vf = pandas.DataFrame()
df_variants = pandas.DataFrame()
df = pandas.DataFrame()
df_2 = pandas.DataFrame()
big_data_frame = pandas.DataFrame()

writer = pandas.ExcelWriter('/Users/chiyuyen/Desktop/new_vcf/10_17_2017/genome_10_17_2017.xlsx',engine='xlsxwriter')
#writer = pandas.ExcelWriter(file_name,engine='xlsxwriter')
count = 0

#data_string = ''
for file in glob.glob(os.path.join(data,"*.vcf.gz")):
    count += 1
    # print os.path.splitext(file)[0].split('/')[-1].split('.')[0]
    sheet = os.path.splitext(file)[0].split('/')[-1].split('.')[0]
    # print count
    # for i in len(file):
    # df = allel.vcf_to_dataframe(file,fields=['CHROM','POS','ID','REF','ALT','QUAL','FILTER','INFO','FORMAT'])

    ## print file name
    df = allel.vcf_to_dataframe(file, fields=['*'])
    callset = allel.read_vcf(file, fields=['*'])

    # basedf_final['project_id'] = Series(self.project_id, index=basedf_final.index)
    df_2 = DataFrame.from_dict(callset, orient='index')
    df_2_t = df_2.transpose()

    ## make new empty string for new dataframe
    data_string = ''
    data_string_value = ''
    for variant in VCF(file):
        #$print variant
        FORMAT_value = str(variant).split('	')[-1]
        data_string_value += ''.join(FORMAT_value) + '\n'+';'
        #print data_string_value
        DATA_value = StringIO('GT:AD:DP:GQ:MQ:GQX:VF'+'\n'+';'+data_string_value)
        #print DATA_value

    #print type(str(variant).split(('\t'))[-2])
        if str(variant).split('\t')[-2].find('VF') != -1:
            #print 'yes'
            ## split string by space and grab last column
            FORMAT =  str(variant).split('	')[-1].replace('./.','0').replace('\n','').split(':')
            VF = FORMAT[-1]
        else:
            VF = 'NA'
        print VF
        data_string += ''.join(VF) + '\n'+';'
        ## remove last ';' element using [:-1]
        DATA = StringIO('VF'+'\n'+';'+data_string[:-1])

    df_vf = pandas.read_csv(DATA,sep=';').reset_index(drop=True)
    df_variants = pandas.read_csv(DATA_value, sep=';').reset_index(drop=True)
    ## drop last row
    df_variants = df_variants[:-1]

    df['GT:AD:DP:GQ:MQ:GQX:VF'] = df_variants.values
    df['VF'] = df_vf.values
    #df_vf.index = df.index


    #df[df.FILTER_PASS == True].to_excel(writer, sheet_name=sheet, header=True, index=False)

    ## filter pass == True and DP >= 20
    df[(df.FILTER_PASS) == True & (df.DP >= 20)].to_excel(writer, sheet_name=sheet, header=True, index=False)
    #df_vf.to_csv('/Users/chiyuyen/Desktop/test.csv')
    #df['AD'] = df_2_t['calldata/AD'].values
    #df['GT'] = df_2_t['calldata/GT'].values
    #df['MQ'] = df_2_t['variants/MQ']
    #df['VF'] = df_vf.values
    #df['VF'].to_csv('/Users/chiyuyen/Desktop/test2.csv')
    df.to_excel(writer, sheet_name=sheet, header=True, index=False)

writer.save()

print '==== Done !!! ======'


