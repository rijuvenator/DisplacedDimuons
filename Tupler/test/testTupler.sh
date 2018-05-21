#!/bin/bash

rm testTuplerOutput.txt 2>/dev/null
pushd $CMSSW_BASE/src/DisplacedDimuons/Tupler/python
echo "Running: HTo2XTo4Mu gen only"
python runNTupler.py HTo2XTo4Mu                 --genonly --test --maxevents 10 >> ~1/testTuplerOutput.txt 2>&1; mv test.root ~1/Signal_GEN.root
echo "Running: HTo2XTo4Mu AOD only"
python runNTupler.py HTo2XTo4Mu                 --aodonly --test --maxevents 10 >> ~1/testTuplerOutput.txt 2>&1; mv test.root ~1/Signal_AOD.root
echo "Running: HTo2XTo4Mu PAT"
python runNTupler.py HTo2XTo4Mu                           --test --maxevents 10 >> ~1/testTuplerOutput.txt 2>&1; mv test.root ~1/Signal_PAT.root
echo "Running: DY100to200 gen only"
python runNTupler.py DY100to200                 --genonly --test --maxevents 10 >> ~1/testTuplerOutput.txt 2>&1; mv test.root ~1/BG_GEN.root
echo "Running: DY100to200 AOD only"
python runNTupler.py DY100to200                 --aodonly --test --maxevents 10 >> ~1/testTuplerOutput.txt 2>&1; mv test.root ~1/BG_AOD.root
echo "Running: DY100to200 PAT"
python runNTupler.py DY100to200                           --test --maxevents 10 >> ~1/testTuplerOutput.txt 2>&1; mv test.root ~1/BG_PAT.root
echo "Running: DoubleMuonRun2016D-07Aug17 gen only"
python runNTupler.py DoubleMuonRun2016D-07Aug17 --genonly --test --maxevents 10 >> ~1/testTuplerOutput.txt 2>&1; mv test.root ~1/DATA_GEN.root
echo "Running: DoubleMuonRun2016D-07Aug17 AOD only"
python runNTupler.py DoubleMuonRun2016D-07Aug17 --aodonly --test --maxevents 10 >> ~1/testTuplerOutput.txt 2>&1; mv test.root ~1/DATA_AOD.root
echo "Running: DoubleMuonRun2016D-07Aug17 PAT"
python runNTupler.py DoubleMuonRun2016D-07Aug17           --test --maxevents 10 >> ~1/testTuplerOutput.txt 2>&1; mv test.root ~1/DATA_PAT.root
popd
