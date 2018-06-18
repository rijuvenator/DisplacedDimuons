#!/bin/bash

# Just in case you don't want to run the last few (SMR takes time, TCUM depends on NM1, CutTable is special)
#for script in Dimuon Gen NMinusOne RecoMuon SignalMatchEff SignalMatchRes SignalMisc

for script in Dimuon Gen NMinusOne RecoMuon SignalMatchEff SignalMisc SignalMatchRes TailCumulative CutTable
do
    python make${script}Plots.py
done

# Prefixes
# Dim Gen NM1 DSA RSA SME SMP SMR TCUM CutTable

# with commas for brace expansion e.g. ls pdfs/{}*.pdf
# {Dim,Gen,NM1,DSA,RSA,SME,SMP,SMR,TCUM,CutTable}
