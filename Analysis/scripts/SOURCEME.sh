#!/bin/bash

if [ "$CMSSW_BASE" == "" ]
then
    echo "CMS environment not set, exiting now"
    return 0
fi

PATH=$CMSSW_BASE/src/DisplacedDimuons/Analysis/scripts/:$PATH
MCSAMPLES="DY10to50 DY50toInf ttbar tbarW tW WZ ZZ WW WJets QCD20toInf-ME"
