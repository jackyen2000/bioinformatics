'''
# #===========================================================================##
# # sample_rename.py
# #
# # Version 1.0
# # 1. rename sample according to SampleSheet.xlsx
# #
# # Jack Yen
# # Oct, 20th, 2017
# #
# # Required: SampleSheet.xlsx ( follow the naming convention, first column is CS_ID, second column is client ID)
# # sample_name format is:  CSnumber_Snumber, e.g.'CS412635_S1'
# #===========================================================================##
# #===========================================================================##
# # All of the general library calls and PATH
# #===========================================================================##
'''

#!/usr/bin/python
'''
import packages
'''
import sys,re,os,argparse,glob,errno
import logging as log
from subprocess import Popen, PIPE
from pandas import *
import glob

'''
USAGE:
python sample_rename.py -s <send_out_path>
'''

# #===========================================================================##
#  Testing area....
#sample_sheet_path = r'/media/fs02/NextSeq2017/171012_NB501920_0030_AHNFYHAFXX/252-17-001-3-49864821/Sendout/SampleSheet.xlsx'
##send_out_path = '/Volumes/lab_data/NextSeq2017/171012_NB501920_0030_AHNFYHAFXX/252-17-001-3-49864821/Sendout/test'
#send_out_path = '/Volumes/lab_data/NextSeq2017/171012_NB501920_0030_AHNFYHAFXX/252-17-001-3-49864821/Sendout'
#sample_sheet_path = os.path.join(send_out_path, 'SampleSheet.xlsx')
#sample_sheet_df = pandas.read_excel(sample_sheet_path,header=None)

#for index, row in sample_sheet_df.iterrows():
#    print row[0]
# #===========================================================================##

parser = argparse.ArgumentParser()
parser.add_argument('-s',dest='send_out_path',help=('full path of sendout directory'),required=True)

args = parser.parse_args()
send_out_path = args.ssend_out_path


sample_sheet_path = os.path.join(send_out_path, 'SampleSheet.xlsx')
EXCEL_PATH = glob.glob(os.path.join(send_out_path, 'CS*'))

sample_sheet_df = pandas.read_excel(sample_sheet_path,header=None)

for file in EXCEL_PATH:
    sample_id = file.split('/')[-1].split('_')[0]
    for index, row in sample_sheet_df.iterrows():
        if sample_id == row[0]:
            new_filename = row[0]+'_'+row[1]+'.xlsx'
            print 'Rename:',file,' to ',new_filename
            os.rename(file,os.path.join(send_out_path,new_filename))
print 'Rename Completed !!!'






def rename(send_out_path):
    sample_sheet_path = os.path.join(send_out_path, 'SampleSheet.xlsx')
    EXCEL_PATH = glob.glob(os.path.join(send_out_path, 'CS*'))

    sample_sheet_df = pandas.read_excel(sample_sheet_path,header=None)

    for file in EXCEL_PATH:
        sample_id = file.split('/')[-1].split('_')[0]
        for index, row in sample_sheet_df.iterrows():
            print row[0]
            if sample_id == row[0]:
                new_filename = row[0]+'_'+row[1]+'.xlsx'
                print 'Rename:',file,' to ',new_filename
                os.rename(file,os.path.join(send_out_path,new_filename))
print 'Rename Completed !!!'