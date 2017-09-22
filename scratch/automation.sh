#!/bin/sh

for samplename in $(comm -23 <(bs list runs -f csv --quote none) old_list.txt | cut -d, -f3); do echo ${samplename}