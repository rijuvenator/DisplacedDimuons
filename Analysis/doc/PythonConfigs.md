# CMSSW Python Config Notes
Reference: [SWGuideAboutPythonConfigFile](https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideAboutPythonConfigFile)

## Annotated Python Config Example

### Top Level
```python
import FWCore.ParameterSet.Config as cms
process = cms.Process('NAME')
```

### Max Events
```python
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(-1))
```

### Global Tag
```python
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag.globaltag = ''
```

### Message Logger
```python
process.load('FWCore.MessageLogger.MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = 1000
```

#### `process.load()` vs. `import`
`import` is Python's standard import; the objects can be imported into the current namespace, or whatever. `process.load()` _adds the objects to the `process` namespace_ as attributes. So although they are similar, they are not the same!

Also, neither the `import` nor the `process.load()` will attach variables that start with `_`.

### Define Process
`TAG` is obtained from an `edmDumpEventContent` on the EDM file

```python
INPUTFILES = cms.untracked.vstring()
process.source = cms.Source('PoolSource', fileNames = INPUTFILES)
process.name = cms.EDAnalyzer('PLUGINNAME', arg = cms.InputTag('TAG'))
process.TFileService = cms.Service('TFileService',
	fileName = cms.string('OUTPUTFILE'))
process.p = cms.Path(name1 * name2)
```

## Message Logger
Reference: [SWGuideMessageLogger](https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideMessageLogger)

C++ files need 

```c++
#include "FWCore/MessageLogger/interface/MessageLogger.h"
```

MessageLogger arguments:

```python
process.MessageLogger = cms.Service('MessageLogger',
	destinations = cms.untracked.vstring('dest'), # output files, cerr, cout
	categories = cms.untracked.vstring(''), # LogVerbatim tags, for example
	dest = cms.untracked.PSet(
		extension = cms.untracked.string('.txt'),
		threshold = cms.untracked.string('DEBUG'),
		limit = cms.untracked.int32(1000)
	)
)
```

See [GIF-CSC REDIGITIZE.py](https://gitlab.cern.ch/CSC-GIF/Gif/blob/Neutron/Production/digi/redigi/REDIGITIZE.py#L107) for an example

## Process Attributes
Reference: [Process Attributes](https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideAboutPythonConfigFile#Attribute_Declarations_for_the_P)  
Reference: [SWGuideEDMParametersForModules](https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideEDMParametersForModules)

* **Source** : data input
* **Modules** : EDProducer, EDFilter, EDAnalyzer, or OutputModule
* **Services** : TFileService
* **Path** : specify modules to execute
* **Task** : specify a group of unscheduled modules
* **Schedule** : specify a group of scheduled modules
* **EndPath** : specify modules to execute after _Path_ modules

## ParameterSets
Reference: [Parameters](https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideAboutPythonConfigFile#Parameters)  
Reference: [PSet Objects](https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideAboutPythonConfigFile#Parameter_Set_PSet_Objects)

`cms.PSet` objects are parameter sets used to configure modules. The parameter sets are passed to the C++ module constructors; see the EDAnalyzer constructor for an example.

Untracked means the parameter values are not saved; tracked means that parameter values were used to create and process the data, and are kept track of... somewhere.

## OutputModule
Reference: [OutputModule Parameters](https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideEDMParametersForModules#OutputModules)

Looks like

```python
process.out = cms.OutputModule('PoolOutputModule',
	fileName = cms.untracked.string('output.root'),
	SelectEvents = cms.untracked.PSet(SelectEvents = cms.vstring('*')),
	outputCommands = cms.untracked.vstring('drop *')
)
```

The important arguments are `fileName` (obvious), `outputCommands`, and `SelectEvents`.

### outputCommands

Reference: [SWGuideSelectingBranchesForOutput](https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideSelectingBranchesForOutput)

`outputCommands` is an untracked vstring of `keep` and `drop` statements. These are either a single `*`, or something of the exact form `*_*_*_*`, or **Type\_Module\_Instance\_Process**. Example:

```python
outputCommands = cms.untracked.vstring('drop *', 'keep *_*_*_*'),
```

### SelectEvents

Reference: [SWGuideEDMPathsAndTriggerBits](https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideEDMPathsAndTriggerBits)

`SelectEvents` is an untracked PSet with the parameter `SelectEvents` which is a vstring (tracked, I assume) of Path _names_ with a special syntax. Events only appear in the output if they pass the selection criteria. Example:

```python
SelectEvents = cms.untracked.PSet(
	SelectEvents = cms.vstring('p1', 'm*')
)
```

where there were previously defined Paths like

```python
process.p1 = cms.Path(process.A + process.B)
process.m1 = cms.Path(process.C * process.D)
process.m2 = cms.Path(process.E + process.F)
```
