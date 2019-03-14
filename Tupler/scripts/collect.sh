#!/bin/bash

# cd to the CRAB directory and run this script
# automatically dives into a CRAB directory
# hadds things together stripping off the number
# and moves it to the destination directory
# should be mostly self explanatory except two things:
# 1) skip DY50toInf since it doesn't succeed normally (see hadd_DY50toInf.sh)
# 2) ls -1v sorts the files correctly by number, i.e. _1 _2 comes before _10 _11

shopt -s extglob

for dir in */*/*/*
do
    if [[ $dir =~ DY50toInf ]]
    then
        continue
    fi
    pushd $dir >/dev/null
    f1=$(ls -1 *.root | head -n 1)
    fa=$(ls -1v *.root)
    b=${f1%_*.root}
    hadd ${b}.root $fa
    mv ${b}.root ~/eos/DisplacedDimuons/
    echo
    popd >/dev/null
done

# for combining WZ-ext and ZZ-ext after the above has run

# mv ntuple_WZ{,-1}.root
# mv ntuple_ZZ{,-1}.root
# hadd ntuple_WZ.root ntuple_WZ-{1,ext}.root
# hadd ntuple_ZZ.root ntuple_ZZ-{1,ext}.root
# rm ntuple_WZ-{1,ext}.root
# rm ntuple_ZZ-{1,ext}.root

# or all in one line
# mv ntuple_WZ{,-1}.root; mv ntuple_ZZ{,-1}.root; hadd ntuple_WZ.root ntuple_WZ-{1,ext}.root; hadd ntuple_ZZ.root ntuple_ZZ-{1,ext}.root; rm ntuple_WZ-{1,ext}.root; rm ntuple_ZZ-{1,ext}.root;
