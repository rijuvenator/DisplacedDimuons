#!/bin/bash

for script in recoMuon dimuon nMinusOne nMinusOneEff
do
    python runAll.py ${script}Plots.py --samples S2B
done

for script in signalMatchEff signalMatchRes signalVertexFitEff
do
    python runAll.py ${script}Plots.py --samples S2
done

# Gen plots runs very quickly locally
# python runAll.py genPlots.py --samples S2 --local &

# For when nMinusOnePlots are complete (locally works very quickly)
# python runAll.py tailCumulativePlots.py --samples S2B --local &

# For rehadding
# for i in Dimuon Gen RecoMuon SignalMatchEff SignalMatchRes nMinusOne TailCumulative; do ./rehadd ${i}Plots; done
