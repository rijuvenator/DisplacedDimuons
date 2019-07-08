# Pileup Systematic Uncertainty

## Data Histograms

New: Pileup histograms for nominal, +4.6%, and -4.6% can be found here:  
`/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/PileUp/`

See here: [PileupJSONFileForData](https://twiki.cern.ch/twiki/bin/view/CMS/PileupJSONFileforData)

In CMSSW, do

```bash
pileupCalc.py                       \
  -i MyAnalysisJSON.txt             \
  --inputLumiJSON pileup_latest.txt \
  --calcMode true                   \
  --minBiasXsec 69200               \
  --maxPileupBin 100                \
  --numPileupBins 100               \
  MyDataPileupHistogram.root
```

where, for 2016 regular analysis,

  * ~~MyAnalysisJSON.txt is the Golden re-reco JSON from [PdmV](https://twiki.cern.ch/twiki/bin/view/CMS/PdmV2016Analysis)~~
  * **MyAnalysisJSON.txt** is the Muon re-reco JSON from [PdmV](https://twiki.cern.ch/twiki/bin/view/CMS/PdmV2016Analysis)
  * **pileup_latest.txt** is linked on the page at the top of this file for 2016

So the full command is

```bash
pileupCalc.py                       \
  -i /afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/Final/Cert_271036-284044_13TeV_PromptReco_Collisions16_JSON_MuonPhys.txt             \
  --inputLumiJSON /afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/PileUp/pileup_latest.txt \
  --calcMode true                   \
  --minBiasXsec 69200               \
  --maxPileupBin 100                \
  --numPileupBins 100               \
  MyDataPileupHistogram.root
```

5% up and down from `69200` are `65740` and `72660`, so

```bash
pileupCalc.py                       \
  -i /afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/Final/Cert_271036-284044_13TeV_PromptReco_Collisions16_JSON_MuonPhys.txt             \
  --inputLumiJSON /afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/PileUp/pileup_latest.txt \
  --calcMode true                   \
  --minBiasXsec 65740               \
  --maxPileupBin 100                \
  --numPileupBins 100               \
  MyDataPileupHistogram_Low.root
```

```bash
pileupCalc.py                       \
  -i /afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/Final/Cert_271036-284044_13TeV_PromptReco_Collisions16_JSON_MuonPhys.txt             \
  --inputLumiJSON /afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/PileUp/pileup_latest.txt \
  --calcMode true                   \
  --minBiasXsec 72660               \
  --maxPileupBin 100                \
  --numPileupBins 100               \
  MyDataPileupHistogram_High.root
```

## Signal Histograms

Run `signalPileupHistograms.py` with a standard `runAll`, i.e.

```bash
runAll.py signalPileupHistograms.py --samples 2 --extra __trigger
```

Make sure `roots/` and `logs/` exist!

Now run `makeSignalPileupHistograms.py`. This will make some plots of the pileup distributions and weights, and will also output a table in the format

```
.
.
.
 10 : 0.95201 1.52298 0.60303
.
.
.
```

Save this as `pileupWeights.txt`.

## Study Pileup Reweighting Systematic

Run `studyPileupSystematics.py` with a standard `runAll` and get the output.

Columns contain the signal point, the sum of the weights for the whole sample, and the sum of the weights for the events passing the selection.

**m<sub>H</sub> m<sub>X</sub> c&tau; :::
&Sigma;w<sub>None</sub> n<sub>None</sub> :::
&Sigma;w<sub>Nom</sub>  n<sub>Nom</sub>  :::
&Sigma;w<sub>Low</sub>  n<sub>Low</sub>  :::
&Sigma;w<sub>High</sub> n<sub>High</sub>**

`analyzePileupEfficiencies.py` computes the variations in signal efficiency.

```bash
python analyzePileupEfficiencies.py <(cat logs/run1/*_{0..32}.out)
```

This prints a table of the form

**m<sub>H</sub> m<sub>X</sub> c&tau; :::
&epsilon;<sub>Nom</sub>/&epsilon;<sub>None</sub> &nbsp;
&epsilon;<sub>Low</sub>/&epsilon;<sub>None</sub> &nbsp;
&epsilon;<sub>High</sub>/&epsilon;<sub>None</sub> &nbsp; :::
&epsilon;<sub>Low</sub>/&epsilon;<sub>Nom</sub> &nbsp;
&epsilon;<sub>High</sub>/&epsilon;<sub>Nom</sub>**

The rightmost columns are the systematic uncertainty due to pileup reweighting.
