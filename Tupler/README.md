# Displaced Dimuons Tupler

Last updated: **14 June 2018**

This subpackage contains code to produce nTuples from PAT Tuples created from the PATFilter package.

  * [Plugins](#plugins)
  * [Tree and Branch Code](#tree)
  * [Python](#python)
  * [Scripts](#scripts)
  * [Test](#test)

<a name="plugins"></a>
## Plugins

There is one plugin in `plugins/`:

  * **SimpleNTupler** is a fairly standard _EDAnalyzer_-based nTupler, running over an EDM format ROOT file and writing a tree, called _SimpleNTupler/DDTree_, to a ROOT file. It uses wrapper classes, including _TreeContainer_ and _*Branches_ classes, and has the _EDTokens_ as members. _SimpleNTupler_ can take one of three different input sources:
    * `SOURCE == "PAT"`: a PAT Tuple produced by the PATFilter package. This will write the full collection of branches available to the nTupler.
    * `SOURCE == "AOD"`: an AOD or AODSIM file in EDM format. This will ignore the PAT collections, e.g. trigger, MET, and pat::Muons.
    * `SOURCE == "GEN"`: a GEN-SIM file in EDM format. This will only write EventBranches and GenBranches to the output nTuple.

<a name="tree"></a>
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
  * **TriggerBranches**: for trigger data (`patTrigger`, etc.)
  * **BeamspotBranches**: for beamspot data (`offlineBeamSpot`)
  * **METBranches**: for MET data (`patMETs`)
  * **VertexBranches**: for vertex data (`offlinePrimaryVertices`)
  * **GenBranches**: for gen particle data (`prunedGenParticles`, `GEIP`)
  * **MuonBranches**: for `pat::Muon` data (`selectedPatMuons`)
  * **DSAMuonBranches**: for `reco::Track` data (`displacedStandAloneMuons`)
  * **RSAMuonBranches**: for `reco::Track` data (`refittedStandAloneMuons`)
  * **DimuonBranches**: for dimuon data (composite DSA muons)

The _TreeContainer_ and each of these _BranchCollection_ classes are added as members of the EDAnalyzer nTupler. The nTupler calls the `Fill()` method on the object, passing the appropriate CMSSW collections, obtained from tokens or tags.

  * **DisplacedMuon** is a data structure for any (displaced) reco muon. It simplifies filling the branches for DSA muons, RSA muons, and the refitted tracks that are part of the Dimuon branches. An object of this type is the output of the _DisplacedMuonFiller_'s `Fill()` method, and the relevant tree branches simply copy the information over.
  * **DisplacedMuonFiller** is the class that computes all displaced reco muon quantities. It does all the heavy lifting and returns a _DisplacedMuon_ object. Any reco muon object should call this method to get all the quantities, and tree branches that fill reco muon quantities should simply copy the resulting information over.
  
<a name="python"></a>
## Python

See [README](python/README.md) in `python/`.

<a name="scripts"></a>
## Scripts

The `scripts/` directory contains a few useful scripts, and also serve as examples of how to use the `dataHandler` library:

  * **dumpOne.py** runs the DAS client and dumps information about one specified `HTo2LongLivedTo4mu` signal point sample.
  * **dumpEvents.py** runs the DAS client and dumps the number of events in each dataset.
  * **printBranches.py** takes the output of `edmDumpEventContent` on an AOD file and prints it in a neater format.

An actually important script in this folder, however, is

  * **generateSignalDATFile.py**, which runs the DAS client and creates the signal .dat file found in `dat/`.

This file is vital for the correct operation of `runNTupler.py`, `dataHandler.py`, and `CFGParser.py`, because it contains the dataset information for all signal samples.

<a name="test"></a>
## Test

`test/` contains a couple test configuration scripts, when I was trying to figure out why the PATTupler wasn't running.

It also contains a real test script, `testTupler.sh`, which runs all types of nTupler inputs and writes the output to a file. This should be run whenever testing to ensure that everything is running properly.
