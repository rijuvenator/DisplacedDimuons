#!/bin/bash

cd combineOutput

for j in $(for i in higgsCombineLimits_2Mu_*HybridNew*; do x=${i/.HybridNew*/}; echo $x; done | sort | uniq)
do
    if [ "$1" == "--hadd" ]
    then
        hadd ${j}.HybridNew-hadded.mH120.root ${j}.HybridNew*
    else
        echo ${j}.HybridNew-hadded.mH120.root ${j}.HybridNew* >> ARGS
        if [ "$(ls *${j}.H* | wc -l)" != "6" ]
        then
            echo "Didn't find 6 files for "$j
        fi
    fi
done

if [ "$1" != "--hadd" ]
then
    echo "Args written to combineOutput/ARGS; now do:"
    echo "cd combineOutput; parallel --colsep \" \" -a ARGS hadd"
fi
