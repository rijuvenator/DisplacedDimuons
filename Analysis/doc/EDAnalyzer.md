# CMSSW EDAnalyzer Notes

## Plugin file

This `.cc` file goes in the `src/Subsystem/Package/plugins/` folder in a CMSSW package.

Bare minimum includes:

```c++
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDAnalyzer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
```

This lets you also put at the end

```c++
DEFINE_FWK_MODULE(PLUGINNAME);
```

See [SWGuideDeclarePlugins](https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideDeclarePlugins) for some more information.

For `TFileService`:

```c++
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"
```

Class definition requires:

* public inheritance from `edm::EDAnalyzer`
* constructor taking `const edm::ParameterSet&`
* virtual void functions `beginJob()` and `endJob()`
* virtual void function `analyze(const edm::Event&, const edm::EventSetup&)`
* probably `edm::Service<TFileService>` and `TTree` members
* probably `edm::EDGetTokenT<TYPE>` token members

```c++
class PLUGINNAME : public edm::EDAnalyzer
{
	PLUGINNAME(const edm::ParameterSet&);
	~PLUGINNAME() {};
	
	virtual void beginJob() {};
	virtual void endJob() {};
	virtual void analyze(const edm::Event&, const edm::EventSetup&);
	
	edm::Service<TFileService> fs;
	TTree *tree;
	
	edm::EDGetTokenT<TYPE> token_;
};
```
Class constructor initializes the tokens and tree, as in the following:

```c++
CLASSNAME::CLASSNAME(const edm::ParameterSet& iConfig) :
	token_(consumes<TYPE>(iConfig.getParameter<edm::InputTag>("NAME")))
{
	tree = fs->make<TTree>(TREENAME, TREETITLE);
}	
```

Remember that the Python Config defines

```python
process.module = cms.EDAnalyzer('PLUGINNAME', NAME = cms.inputTag('TAG'))
```

where `TAG` is the module from the EDM file.

The `analyze` function runs once per event with an event object as input.  
Tokens are used as keys to access the tag in the event, as in the following:

```c++
CLASSNAME::::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
	edm::Handle<TYPE> token;
	iEvent.getByToken(token_, token);
}	
```
Then the exposed `token` collection can be looped over.

## BuildFile.xml
BuildFiles define what packages produce and external dependencies.

See more at

* [WorkbookBuildFilesIntro](https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookBuildFilesIntro): contains template BuildFile examples for different situations
* [SWGuideBuildFile](https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideBuildFile): contains organized documentation about directory structure and BuildFile tags

As a minimal working example I required two `BuildFile.xml` files:

* one in `src/Subsystem/Package/plugins/`
* one in `src/Subsystem/Package/`

### `plugins/BuildFile.xml`
EDM plugins are defined with the `<library>` tag.

```xml
<library file="PLUGINNAME.cc" name="PLUGINNAME">
    <use name="Subsystem/Package"/>
</library>
```

### Main `BuildFile.xml`
The `<use>` tag defines external dependencies.  
The `<export>` tag defines the shared libraries the package will produce.

```xml
<use name="root"/>
<use name="FWCore/Framework"/>
<use name="FWCore/ParameterSet"/>
<use name="FWCore/ServiceRegistry"/>
<use name="CommonTools/UtilAlgos"/>
<export>
    <lib name="1"/>
</export>
```

Other package dependencies should be included here similarly.

## Workflow for making an nTuple

Typically one

1. declares the tree branch variables (as members in a class)
* initializes/resets the branch variables (probably in the constructor)
* assigns to the branch variables once per event (probably in `analyze()`)
* calls `TTree::Fill()` to store the assigned data
* resets the branch variables again
* calls `TTree::Write()` when complete (probably in `endJob()`)

## Custom Classes for TTrees
Probably won't be doing this much anymore since analyses like flat TTrees, but just in case.

The problem is that declaring a TTree branch to be some custom class – or even some non-trivial combination of STL templates like ``std::vector<std::map<std::string,float>>`` – doesn't play well with ROOT because ROOT has to generate some dictionaries for the class types.

Fortunately, the solution is relatively simple, although poorly documented.
In essence,

* the class must be instantiated somewhere
* the class must be declared to an LCG dictionary
* the `rootrflx` dependency must be added

So first, add ROOT Reflex to `Subsystem/Package/BuildFile.xml`

```xml
<use name="rootrflx"/>
```
Then, two files are required.
 
### `Subsystem/Package/src/classes.h`
This instantiates the class somewhere.

```c++
#include "Subsystem/Package/interface/ClassName.h"

namespace {
	struct dictionary {
		ClassName dummy;
	};
}
```

### `Subsystem/Package/src/classes_def.xml`
This declares the class to the LCG dictionary.

```xml
<lcgdict>
	<class name="ClassName"/>
</lcgdict>
```
After this, ROOT in the CMSSW context will automatically generate whatever dictionaries it needs to be able to add classes to TTrees.