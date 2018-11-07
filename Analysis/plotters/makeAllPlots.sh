#!/bin/bash

# Just in case you don't want to run the last few (SRR takes time, TCUM depends on NM1, CutTable is special)
#for script in Dimuon Gen NMinusOne NMinusOneEff RecoMuon SignalRecoEff SignalVertexFitEff SignalRecoRes

for script in Dimuon Gen NMinusOne NMinusOneEff RecoMuon SignalRecoEff SignalVertexFitEff SignalRecoRes TailCumulative CutTable
do
    python make${script}Plots.py
done

# Prefixes
# Dim Gen NM1 NM1E DSA RSA SRE SVFE SRR TCUM CutTable

# with commas for brace expansion e.g. ls pdfs/{}*.pdf
# {Dim,Gen,NM1,NM1E,DSA,RSA,SRE,SVFE,SRR,TCUM,CutTable}
