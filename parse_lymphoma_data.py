import os, sys
import csv
import glob
from pandas import *
from os.path import basename

data = r"/Volumes/lab_data/TMB/NGS_lymphoma_variance_data"
data_test = "/Volumes/lab_data/TMB/NGS_lymphoma_variance_data/variant_list_A_5PercJurkC12_S4_L001_R1_001_2.txt"

for file in glob.glob(os.path.join(data,"*.txt")):
    df = read_table(file,skiprows=9)
    #print df
    #print file

    print  "number of variants = " ,df['Chromosome'].count(), " for sample: ",basename(file).split(".")[0]

