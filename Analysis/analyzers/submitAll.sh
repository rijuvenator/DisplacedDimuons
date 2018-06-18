#!/bin/bash

for script in recoMuon dimuon nMinusOne
do
    python runAll.py ${script}Plots.py --samples S2BD
done

for script in gen signalMatchEff signalMatchRes signalMisc
do
    python runAll.py ${script}Plots.py --samples S2
done

# For when nMinusOnePlots are complete (locally works very quickly)
# python runAll.py tailCumulativePlots.py --samples S2BD --local &

# For rehadding
# for i in Dimuon Gen RecoMuon SignalMatchEff SignalMatchRes SignalMisc nMinusOne TailCumulative; do ./rehadd ${i}Plots; done
