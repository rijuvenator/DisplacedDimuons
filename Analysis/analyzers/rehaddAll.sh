#!/bin/bash

# This hadds together sample_0 ... sample_N
pushd roots
for i in RecoMuon Dimuon nMinusOne nMinusOneEff
do
    for s in DY50toInf ttbar
    do
        ./rehadd ${i}Plots_${s}
    done
done

# Move all the sample_* to a directory, so that they do not interfere with hadd
mkdir -p tmp
mv *DY50toInf_* *ttbar_* tmp

# now rehadd everything: the script_* glob will not match the script_sample_* files because they are in tmp
for i in RecoMuon Dimuon nMinusOne nMinusOneEff SignalMatchEff SignalVertexFitEff SignalMatchRes
do
    ./rehadd ${i}Plots
done
popd
