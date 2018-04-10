# Displaced Dimuons Tupler

Last updated: 10 April 2018

This subpackage contains code to produce tuples: PATTuples, nTuples, etc.

## Plugins

There are two plugins in `plugins/`:

  * **SimpleNTupler** is a fairly standard _EDAnalyzer_-based nTupler, running over an EDM format ROOT file and writing a tree, called _SimpleNTupler/DDTree_, to a ROOT file. It uses wrapper classes, including _TreeContainer_ and _*Branches_ classes, and has the _EDTokens_ as members. Currently, _SimpleNTupler_ expects collections from AODSIM (see configuration file)
  * **GenOnlyNTupler** is exactly the same as _SimpleNTupler_, except that it only requires the generated branches and only writes _EventBranches_ and _GenBranches_ to the tree. As such, _GenOnlyNTupler_ only expects collections from GEN-SIM (see configuration file)

## Tree and Branch Code

`interface/` contains `.h` header files for compiled class code, most of which have `.cc` implementation files in `src/`.

  * **TreeContainer** is a simple wrapper class around a _TTree_ that deals with the _TFileService_ boilerplate
  * **BranchCollection** is a base container class for a collection of _TTree_ branches. The intent is to make declaring branch variables, declaring _TTree_ branches, and resetting variables as clean as possible. I envision a collection of tree branches to have some semantic meaning: for example, all muon branches are grouped together; all vertex branches are grouped together; and so on. This gives the nTupler some structure and flexible organization. The intended use is to
    * derive a specific Branches class from _BranchCollection_
    * pass a _TreeContainer_ to the class
    * define the branch variables as class members
    * call the `Declare()` methods in the constructor, which declare _TTree_ branches
    * implement the `Reset()` method, which specifies reset/default values
    * implement a `Fill()` method, which takes as arguments the CMSSW collections and sets values for the branches. These are the methods implemented in the `.cc` files.
  
The current list of _BranchCollection_ classes are:
  
  * **EventBranches**: for event, run, lumi, bx (`edm::Event`)
  * **TriggerBranches**: for trigger data (`TriggerResults`)
  * **BeamspotBranches**: for beamspot data (`offlineBeamSpot`)
  * **VertexBranches**: for vertex data (`offlinePrimaryVertices`)
  * **GenBranches**: for gen particle data (`genParticles`, `GEIP`)
  * **MuonBranches**: for `pat::Muon` data (`selectedPatMuons`)
  * **DSAMuonBranches**: for `reco::Track` data (`displacedStandAloneMuons`)
  * **RSAMuonBranches**: for `reco::Track` data (`refittedStandAloneMuons`)
  * **DimuonBranches**: for dimuon data (composite DSA muons)

The _TreeContainer_ and each of these _BranchCollection_ classes are added as members of the EDAnalyzer nTupler. The nTupler calls the `Fill()` method on the object, passing the appropriate CMSSW collections, obtained from tokens or tags.
  
## Python

The `python/` directory contains three top-level `_cfg.py` files:

  * **PATTupler_cfg.py** is the `cmsRun` configuration file to produce PATTuples, based on the default PAT templates. It expects AODSIM as the Source, switches on the Trigger, and loads a few basic filters. It produces a PATTuple, which is what the SimpleNTupler expects. _Note:_ The SimpleNTupler can actually use mostly AOD collections, except for the `pat::Muons`, but it is much faster to create a stripped down PATTuple and run over that than it is to run over AODSIM every time you want to update your nTuple.
  * **SimpleNTupler_cfg.py** is the `cmsRun` configuration file to produce SimpleNTuples. The only non-obvious section in here is the part that loads the _TransientTrackBuilder_.
  * **GenOnlyNTupler_cfg.py** is the `cmsRun` configuration file to produce gen only nTuples. Otherwise, same as _SimpleNTupler_.

Each of these configuration files has a `runAll.py` file, which is just a Python script that submits jobs to the lxplus batch system.

I have tried to be organized with how the configuration files call modules by organizing some of the Python fragments into directories. So all the `_cfi.py` files are in `python/Modules/`, and they get loaded by the configuration files. There's also a `python/Filters/goodData_cff.py`.

`python/Utilities/` contains:

  * **dataHandler.py**: a Python library for working with DAS and datasets. It will call the appropriate command-line DAS commands and get lists of datasets and files automatically, given the correct parameters. Other classes for other types of datasets should be added here, too, so that any file that deals with datasets has object-oriented information about the dataset, e.g. files, MC parameters, the dataset name, etc.

## Scripts

The `scripts/` directory contains a few useful scripts, and also serve as examples of how to use the `dataHandler` library:

  * **dumpData.py** runs the DAS client and dumps information about all the `HTo2LongLivedTo4mu` samples.
  * **dumpOne.py** runs the DAS client and dumps information about one specified `HTo2LongLivedTo4mu` signal point sample.
  * **dumpEvents.py** runs the DAS client and dumps the number of events in each dataset.
  * **filterData.py** runs the DAS client dumps the datasets that match some condition.
  * **printBranches.py** takes the output of `edmDumpEventContent` on an AOD file and prints it in a neater format.

## Test

`test/` contains a couple test configuration scripts, when I was trying to figure out why the PATTupler wasn't running.
