# #===========================================================================##
# # parser_vcf.py
# #
# # find vcf files and parse to pandas, write to excel by sheet
# #
# # Jack Yen
# # Aug 23rd, 2017
# # how to run it:
# # python parser_vcf.py -r run_directory -n file_name.xlsx
# #===========================================================================##
# #===========================================================================##
# # All of the general library calls and PATH
# #===========================================================================##


import allel
import os
import glob
from pandas import *
from pandas import ExcelWriter
import argparse
import numpy


parser = argparse.ArgumentParser()
parser.add_argument('-r',dest='run_dir',help=('full path of running directory wit data'))
parser.add_argument('-n',dest='file_name',help=('output file name'))


args = parser.parse_args()

#data = r"/Volumes/NGS_data/scratch/vcf"
data = r"/Volumes/NGS_data/RA/filtered_vcf"

data = args.run_dir
file_name = args.file_name

df = pandas.DataFrame()
writer = pandas.ExcelWriter(file_name,engine='xlsxwriter')
writer = pandas.ExcelWriter("test.xlsx",engine='xlsxwriter')

count = 0

for file in  glob.glob(os.path.join(data,"*.vcf")):
    print '======= Reading vcf files to dataframe ========'
    count +=1
    sheet = os.path.splitext(file)[0].split('/')[-1].split('.')[0]
    #print count
    callset = allel.read_vcf(file,fields='*')
    #print sorted(callset.keys())
    #df['GT'] = callset['calldata/GT']
    #print callset['calldata/AD']
    #df = allel.vcf_to_dataframe(file,fields=['CHROM','POS','ID','REF','ALT','DP'])
    df = Series(callset['calldata/GT'])

    #df.to_excel(writer,sheet_name='Sheet'+str(count),header=True,index=False)
    print df
    print '======= Writing to excel files ========'
    df.to_excel(writer, sheet_name=sheet, header=True, index=False)
writer.save()

print '======Done !!! ======='





