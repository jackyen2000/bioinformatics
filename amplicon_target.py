##===========================================================================##
## amplicon_target.py
##
## This is the script to parse snp target and search against the bed file to see
## if target is within amplicon region
##
## CGI Bioinformatics
## Jack Yen
## April 20th, 2017
##===========================================================================##
##===========================================================================##
## All of the general library calls and PATH
##===========================================================================##
import time
import os
import sys
import glob
from pandas import *
import numpy as np
import csv


## define datapath at local
datapath = r"/Users/chiyuyen/workspace/data_amplicon"
os.chdir(datapath)

## read files
target_file = pandas.read_csv('19.csv',skipinitialspace=True, index_col=None)
target_file.columns = ["snp_id","chrom","location","gene","TSCA","genotyping_assay"]
target_location = target_file['location']

bed_file = pandas.read_table('New_19_122175_Amplicons_Export.bed',index_col=None,names = ["chrom", "start", "end", "gene","score","strand"])
#range = bed_file['end'] - bed_file['start']

#pandas.DataFrame = (bed_file.start.values <= target_location.values) & (bed_file.end.values >= target_location.values)


#for i in target_location.values:
#for i in target_file.location.values:
for index1, row1 in target_file.iterrows():
    for index2, row2 in bed_file.iterrows():
        if (row2.start <= row1.location ) & (row2.end >= row1.location):
            print 'SNP ID that is within target amplicon region',row1.snp_id,',','This is the location', ':',row1.location,\
                ',','Gene',':',row1.gene,',','genotyping_assay',row1.genotyping_assay



# #    if (bed_file.start <= i) & (bed_file.end >= i):
#
#         print i
#
# for index, row in bed_file.iterrows():
#     print row.start, row.end
# #df = target_file[target_file['location'].between(bed_file.start, bed_file.end, inclusive=True)]
#
#
#
# target_file.sort_index(inplace=True)
# bed_file.sort_index(inplace=True)
# target_file[target_file['location'].between(bed_file.start, bed_file.end, inclusive=True)]
#
#
#
# for index, row in bed_file.iterrows():
#     for i, row in target_location.iteritems():
#         if bed_file['start'] <= row & row <= bed_file['end']:
#             print row
#
#
#
#
# target_location.isin(bed_file)