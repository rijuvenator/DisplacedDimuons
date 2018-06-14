#!/bin/bash

for script in gen recoMuon dimuon nMinusOne
do
    python runAll.py ${script}Plots.py --samples S2BD
done

for script in signalMatchEff signalMatchRes signalMisc
do
    python runAll.py ${script}Plots.py --samples S2
done

# For when nMinusOnePlots are complete
# python runAll.py tailCumulativePlots.py --samples S2BD
