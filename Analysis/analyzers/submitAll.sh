#!/bin/bash

for script in genPlots recoMuonPlots dimuonPlots nMinusOnePlots
do
    python runAll.py ${script}.py --samples S2BD
done

for script in signalMatchEffPlots signalMatchResPlots signalMiscPlots
do
    python runAll.py ${script}.py --samples S2
done

# For when nMinusOnePlots are complete
# python runAll.py tailCumulativePlots.py --samples S2BD
