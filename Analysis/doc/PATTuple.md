# PATTuple Notes

## PAT Workflow
Reference: [WorkBookPATWorkflow](https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookPATWorkflow)

A PAT Tuple begins from RECO or AOD. The `patDefaultSequence`, defined at [patSequences_cff.py](https://github.com/cms-sw/cmssw/blob/CMSSW_9_2_X/PhysicsTools/PatAlgos/python/patSequences_cff.py), performs the following steps:

* Create PAT candidates
	* Consists of EDProducers that make, by default:
		* `patPhotons`
		* `patElectrons`
		* `patMuons`
		* `patTaus`
		* `patJets`
		* `patMETs`
* Select PAT candidates
	* Consists of EDFilters applied to the PAT candidates
		* Nothing by default
		* The `pat*` collections are input to EDFilters which output `selectedPat*` collections
		* The user should modify the `pat*.cut` string parameter
		* See [SWGuidePhysicsCutParser](https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuidePhysicsCutParser) for cut string syntax
* Clean PAT candidates
	* Consists of EDProducers that find overlaps between objects and removes them
		* The `pat*` collections are input to EDProducers which output `cleanPat*` collections
		* These are a new collection of PAT Candidates that are pointers to overlaps.
* Count Clean PAT candidates
	* Consists of EDFilters that ... make sure the number of candidates is between 0 and 999999?

## PAT Templates and Tools
### PAT Template
The default [PAT Template](https://github.com/cms-sw/cmssw/blob/CMSSW_9_2_X/PhysicsTools/PatAlgos/python/patTemplate_cfg.py) does the following:

* Defines a process, a MessageLogger, a PoolSource, a maxEvents, and a PoolOutputModule
* Loads geometry and detector conditions: required to run PAT for some reason
* PoolOutputModule is given a filename, no SelectEvents argument, and an outputCommands list `patEventContentNoCleaning` imported from [patEventContent_cff](https://github.com/cms-sw/cmssw/blob/CMSSW_9_2_X/PhysicsTools/PatAlgos/python/patEventContent_cff.py)
* Runs a `patAlgoToolsTask`

The geometry and detector conditions boilerplate looks similar to this:

```python
process.load("Configuration.Geometry.GeometryRecoDB_cff")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:run2_mc')
process.load("Configuration.StandardSequences.MagneticField_cff")
``` 

The standard keeps and drops for the OutputModule are

```python
patEventContentNoCleaning = [
    'keep *_selectedPatPhotons*_*_*',
    'keep *_selectedPatOOTPhotons*_*_*',
    'keep *_selectedPatElectrons*_*_*',
    'keep *_selectedPatMuons*_*_*',
    'keep *_selectedPatTaus*_*_*',
    'keep *_selectedPatJets*_*_*',    
    'drop *_*PF_caloTowers_*',
    'drop *_*JPT_pfCandidates_*',
    'drop *_*Calo_pfCandidates_*',
    'keep *_patMETs*_*_*',
    'keep *_selectedPatPFParticles*_*_*',
    'keep *_selectedPatTrackCands*_*_*'
]
```

### PAT Tools
Reference: [SWGuidePATTools](https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuidePATTools)

These seem to be helper functions that turn things on and off, let you move things around, configure things, etc.

Reference: [WorkBookPATConfiguration](https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookPATConfiguration)

This seems to be documentation on how to configure the creation of PAT Candidates. 