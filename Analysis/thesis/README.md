# Thesis

I made mini versions of almost all the analyzer scripts, standalone, dependent on very little else

## Luminosities by era

Instructions are inside the script, this let me make Table 4.1

## Figures in this folder
Here they are, enumerated:

  * **Figure 4.3 and 4.5**: DSA and RSA pT resolutions and efficiencies, charge difference, etc. are made by
    * analyzeDSAvsRSAPlots.py
    * makeDSAvsRSAPlots.py
    * analyzeQualityCutResolutions.py
    * makeQualityCutResolutionsAndReplacementEffectPlots.py
  * **Figure 4.7, 4.8, 4.9**: Effect of PAT replacement are made by
    * analyzeReplacementEffect.py
    * analyzeReplacementEffectSignal.py
    * makeQualityCutResolutionsAndReplacementEffectPlots.py
    * makeReplacementEffectSignalPlots.py
  * **Figure 4.10**: Vertex fit efficiency are made by
    * analyzeVertexFitPlots.py
    * makeVertexFitPlots.py
  * **Figure 4.13, 4.14**: Pairing criteria efficiencies, made by
    * analyzePairingCriteria.py
    * makePairingCriteriaPlots.py
  * **Figure 4.16 and 4.25-4.32** are made by
    * analyzeNMinusOneDistributions.py
    * makeNMinusOnePlots.py
  * **Figure 4.24** is made by
    * analyzeMassDistributions.py
    * makeMassDistributions.py

HLTRecoPlots are't terribly illuminating so I just put in the efficiency, which is high
The associated script here will tell you what that efficiency is

## Figures not in this folder
Things not in this folder:

  * **Figure 4.17, 4.19, 4.20-4.22**: Made by various scripts in bgest/
  * **Figure 4.23**: Made by optimizeCut in optimizers/
  * **Figure 4.34**: Made by the scripts in pileup/
  * **Figure 4.33-4.36**: Made by makeLimitsPlots in limits/

## Event displays

Get Fireworks [WorkBookFireworks Twiki](https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookFireworks) and run it with

```
./cmsShow FILE.root -r -c dataBig.fwc --no-version-check
```

`dataBig.fwc` is my Fireworks config file for viewing on a bigger screen with DSA muons, jets, muons, etc. and some of the simpler cuts.

Then ROOT prompt is enabled, dump these in for DSA muons outside the tracker:

```
p = fireworks::Context::getInstance()->getTrackPropagator();
p->SetMaxR(900);
p->ElementChanged(1,1);
```

Save images using the menus. I found these coordinates to work well (using ImageMagick):

```
for i in unnamed-*_RhoPhi.png; do x=${i/unnamed/event}; convert $i -crop 1000x960+0+900 $x; done
for i in unnamed-*_RhoZ.png;   do x=${i/unnamed/event}; convert $i -crop  600x934+0+460 $x; done
```

