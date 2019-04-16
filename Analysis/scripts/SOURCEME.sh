#!/bin/bash

if [ "$CMSSW_BASE" == "" ]
then
    echo "CMS environment not set, exiting now"
    return 0
fi

PATH=$CMSSW_BASE/src/DisplacedDimuons/Analysis/scripts/:$PATH
