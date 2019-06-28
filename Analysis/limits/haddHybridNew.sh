#!/bin/bash

cd combineOutput

for j in $(for i in higgsCombineLimits_2Mu_*HybridNew*; do x=${i/.HybridNew*/}; echo $x; done | sort | uniq)
do
    hadd ${j}.HybridNew-hadded.mH120.root ${j}.HybridNew*
done
