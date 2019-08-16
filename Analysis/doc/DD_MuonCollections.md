# Summary of Muon Collections for Displaced Dimuons Studies

## Introduction
Information here is taken from

* Indico talks by Marco de Mattia
* Published CMS papers
* CMS Analysis Notes
* an informal discussion with Juliette Alimena, who developed the `displacedStandAloneMuons` collection for her analysis

## References

* **CMS AN-2011/487**: *Studies of Stand-Alone Muon Reconstruction for Displaced Muons* ([link](http://cms.cern.ch/iCMS/jsp/db_notes/noteInfo.jsp?cmsnoteid=CMS%20AN-2011/487))
* **EXO-12/037**: *Search for long-lived particles that decay into final states containing two electrons or two muons in proton-proton collisions at \\(\sqrt{s} = 8\;\mathrm{TeV}\\)* ([link](http://cms.cern.ch/iCMS/analysisadmin/cadilines?line=EXO-12-037))
* **Approval Talk for EXO-14/012** ([link](https://indico.cern.ch/event/381449/))
* **EXO-14/012**: *Search for long-lived particles that decay into final states containing two muons reconstructed using only the CMS muon chambers* ([link](http://cms.cern.ch/iCMS/analysisadmin/cadilines?line=EXO-14-012))
* **CMS AN-2015/035**: *A Study of Displaced Standalone Muon Reconstruction* ([link](http://cms.cern.ch/iCMS/jsp/db_notes/noteInfo.jsp?cmsnoteid=CMS%20AN-2015/035))

## List of Muon Collections
Papers make clear that it is important to use standalone muons in the analysis so as to be sensitive to displaced vertices outside the tracker. There are global versions of most of these.

***
#### `standAloneMuons`
These are muons reconstructed from **chamber hits only**. No final refit is performed due to a small reconstruction efficiency loss.

***
#### `standAloneMuons_UpdatedAtVtx`
These are standalone muons **with beamspot constraint**. The same lack of final refit probably applies.

* [x] ==Question==: why does *AN-2011/487* only talk about "stand-alone muons (without the update at the vertex)" as having a beamspot bias? What exactly does "updated at vertex" mean, then?
	* Slava answered this


***
#### `refittedStandAloneMuons`
These are standalone muons **with final refit activated** with standalone trajectory builder. From [RecoMuonPPonly_cff.py](https://github.com/cms-sw/cmssw/blob/master/RecoMuon/Configuration/python/RecoMuonPPonly_cff.py):

```python
refittedStandAloneMuons = standAloneMuons.clone()
refittedStandAloneMuons.STATrajBuilderParameters.DoRefit = True
```
There is also a `refittedStandAloneMuons_UpdatedAtVtx` collection which I assume is the same as above except it starts with cloning the `standAloneMuons_UpdatedAtVtx`.

##### Purpose:
Reduce beamspot constraint bias resulting in \\(d_0\!\\) being closer to zero

***
#### `displacedStandAloneMuons`
These are standalone muons with the following modifications:

* uses cosmic seeds instead of regular muon seeds
* segments are not forced to point downwards
* muon trajectory builder (see also [standAloneMuons_cfi.py](https://github.com/cms-sw/cmssw/blob/master/RecoMuon/StandAloneMuonProducer/python/standAloneMuons_cfi.py)) is `StandAloneMuonTrajectoryBuilder` instead of `Exhaustive`
* a vertex constraint was set `False`
* no final refit (was "not observed to be necessary")

```python
displacedMuonSeeds = CosmicMuonSeed.clone()
displacedMuonSeeds.ForcePointDown = False
displacedStandAloneMuons = standAloneMuons.clone()
displacedStandAloneMuons.InputObjects = cms.InputTag("displacedMuonSeeds")
displacedStandAloneMuons.MuonTrajectoryBuilder = cms.string("StandAloneMuonTrajectoryBuilder")
displacedStandAloneMuons.TrackLoaderParameters.VertexConstraint = cms.bool(False) 
```

##### Purpose:
Improve \\(p_\text{T}\!\\) reconstruction for highly displaced vertices, which was previously much lower than the generated \\(p_\text{T}\!\\). This improvement was specific to Juliette's model and selection.

## Additional Notes

* DSA muons also benefited from a "mean timer algorithm" in local DT reconstruction
* A few comments from Juliette:
	* Emphasized: \\(p_\text{T}\\) bias change was an improvement, but by no means perfect
	* We can also go to Daniele Trocino, who helped Juliette develop the collection, for information
	* DSA might only be most appropriate for _really_ displaced muons. Suggested we look at many collections to see effects.
	* RSA has not been used by anyone in the past few years; it's still part of AOD, but only minimally, i.e. has not been developed further