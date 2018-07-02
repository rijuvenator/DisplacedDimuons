#!/bin/bash

rm testTuplerOutput.txt 2>/dev/null
pushd $CMSSW_BASE/src/DisplacedDimuons/Tupler/python
echo "Running: HTo2XTo2Mu2J PAT"
python runNTupler.py HTo2XTo2Mu2J                         --test --maxevents 10 >> ~1/testTuplerOutput.txt 2>&1; mv test.root ~1/Signal_PAT.root
echo "Running: DY50toInf PAT"
python runNTupler.py DY50toInf                            --test --maxevents 10 >> ~1/testTuplerOutput.txt 2>&1; mv test.root ~1/BG_PAT.root
echo "Running: DoubleMuonRun2016D-07Aug17 PAT"
python runNTupler.py DoubleMuonRun2016D-07Aug17           --test --maxevents 10 >> ~1/testTuplerOutput.txt 2>&1; mv test.root ~1/DATA_PAT.root
popd
