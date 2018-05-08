# Displaced Dimuons Tupler

Last updated: 8 May 2018

This subpackage contains code to produce nTuples from PAT Tuples created from the PATFilter package.

## Plugins

There are two plugins in `plugins/`:

  * **SimpleNTupler** is a fairly standard _EDAnalyzer_-based nTupler, running over an EDM format ROOT file and writing a tree, called _SimpleNTupler/DDTree_, to a ROOT file. It uses wrapper classes, including _TreeContainer_ and _*Branches_ classes, and has the _EDTokens_ as members. Currently, _SimpleNTupler_ expects a PAT Tuple produced by PATFilter.
  * **GenOnlyNTupler** is exactly the same as _SimpleNTupler_, except that it only requires the generated branches and only writes _EventBranches_ and _GenBranches_ to the tree. As such, _GenOnlyNTupler_ only expects collections from GEN-SIM.

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
  * **TriggerBranches**: for trigger data (`TriggerResults`, etc.)
  * **BeamspotBranches**: for beamspot data (`offlineBeamSpot`)
  * **METBranches**: for MET data (`patMETs`)
  * **VertexBranches**: for vertex data (`offlinePrimaryVertices`)
  * **GenBranches**: for gen particle data (`prunedGenParticles`, `GEIP`)
  * **MuonBranches**: for `pat::Muon` data (`cleanPatMuons`)
  * **DSAMuonBranches**: for `reco::Track` data (`displacedStandAloneMuons`)
  * **RSAMuonBranches**: for `reco::Track` data (`refittedStandAloneMuons`)
  * **DimuonBranches**: for dimuon data (composite DSA muons)

The _TreeContainer_ and each of these _BranchCollection_ classes are added as members of the EDAnalyzer nTupler. The nTupler calls the `Fill()` method on the object, passing the appropriate CMSSW collections, obtained from tokens or tags.
  
## Python

A VOMS proxy is required for using pretty much any of the files in the `python/` directory.

The `python/` directory contains one top-level `_cfg.py` file: **NTupler_cfg.py**, which is the `cmsRun` configuration file to run the SimpleNTupler. With the `--genonly` option to a file that runs the configuration parser, e.g. *runNTupler.py*, the GenOnlyNTupler plugin will be run instead. The SimpleNTupler expects PAT Tuples created by the PATFilter package as its source, and the datasets are all defined in *dataHandler.py*. *NTupler_cfg.py* is a standalone `cmsRun` configuration file, only importing other `_cfi.py` files, both locally and centrally. However, one may prefer to use my submitter script...

**runNTupler.py** is the main atomic submitter script. The basic usage is
```python
python runNTupler.py [NAME] [OPTIONS]
```

The options can be found in `python/Utilities/CFGParser.py`. Exactly one of the following options may be passed:
  * `--crab`: submits the desired dataset job to CRAB, using the CRAB configuration script embedded within
  * `--batch`: submits the desired dataset job to LXBATCH, using the LXBATCH submission script embedded within
  * `--test`: submits the desired dataset job *locally* for 1000 events and only the first file
  * no option: submits the desired dataset job *locally* for the entire dataset

For convenience, **submitAll.py** submits the full suite of jobs; all that is needed is to change the `MODE` variable inside the script as desired.

As of May 8, 2018, this is not ready yet, because we don't have PAT Tuples for everything.

I have tried to be organized with how the configuration files call modules by organizing some of the Python fragments into directories. So all the `_cfi.py` files are in `python/Modules/`, and they get loaded by the configuration files. There's also a `python/Filters/goodData_cff.py`.

`python/Utilities/` contains:

  * **dataHandler.py**: a Python library for working with DAS and datasets. It will call the appropriate command-line DAS commands and get lists of datasets and files automatically, given the correct parameters. Other classes for other types of datasets should be added here, too, so that any file that deals with datasets has object-oriented information about the dataset, e.g. files, MC parameters, the dataset name, etc.
  * **CFGParser.py**: a Python library for configuring and running cmsRun jobs with crab, batch systems, or locally, with several command line options for setting test modes, printing output, changing output file patterns, and more. It uses the full *dataHandler* machinery.

## Scripts

The `scripts/` directory contains a few useful scripts, and also serve as examples of how to use the `dataHandler` library:

  * **dumpData.py** runs the DAS client and dumps information about all the `HTo2LongLivedTo4mu` samples.
  * **dumpOne.py** runs the DAS client and dumps information about one specified `HTo2LongLivedTo4mu` signal point sample.
  * **dumpEvents.py** runs the DAS client and dumps the number of events in each dataset.
  * **filterData.py** runs the DAS client dumps the datasets that match some condition.
  * **printBranches.py** takes the output of `edmDumpEventContent` on an AOD file and prints it in a neater format.
  * **generateSignalDATFile.py** runs the DAS client and creates the signal .dat file found in `dat/`.

## Test

`test/` contains a couple test configuration scripts, when I was trying to figure out why the PATTupler wasn't running.
