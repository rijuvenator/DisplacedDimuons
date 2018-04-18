# Displaced Dimuons Analysis

Last updated: 10 April 2018

This subpackage contains code to analyze nTuples produced by the Tupler subpackage. It mostly produces histograms. The `python` folder contains several libraries for organizing and interacting with the nTuples and their data.

## Python

The `python/` directory contains the following libraries:

  * **Constants.py** contains common literals: file paths and lists of signal points. It's better to import these from a central location so that they don't have to changed in multiple places.
  * **Plotter.py** is my general-purpose plot making and styling library, with plots based on standard TDR style and with a large number of useful functions and classes that I've found useful when creating and managing plots. See the _Plotter_ documentation for full documentation.
  * **Primitives.py** is my starting point for creating Python objects from flat nTuples. The basic idea is that it's much easier to write code like

```python
for muon in muons:
	if muon.pt > 5:
		print muon.eta
```

  than
  
```python
for i in range(len(tree.muon_pdgID)):
	if tree.muon_pt[i] > 5:
		print tree.muon_eta[i]
  ```
  
  So the _Primitives_ library takes in an addressed _TTree_, creates an "_ETree_", which is a namespace structure with copied _TTree_ branches turned into Python lists, and defines several object structures that build a list of high-level objects, such as _Vertex_, _Muon_, _Particle_, and so on. The _ETree_ also presents a unified way of only turning on some branches in the _TTree_.
  
  The basic idiom for using the _Primitives_ library is as follows:
  
```python
import ROOT
import DisplacedDimuons.Analysis.Primitives as Primitives

f = ROOT.TFile.Open('test.root')
t = f.Get('DDTree')

for event in t:
	E = Primitives.ETree(t)
	muons = E.getPrimitives('MUON')

	for muon in muons:
		print muon.pt, muon.eta, muon.phi, muon.energy
```
  * **RootTools.py** contains a few small ROOT-related additions.
    * The _TVector_ section improves the Python implementation of _TVector2_, _TVector3_, and _TLorentzVector_ by adding a few functions and fixing the interface so as to be a bit more uniform.
    * The `setGenAliases()` function is a _TTree_ related function that sets gen particle aliases in the _TTree_. My current way of storing the gen particles in the tree is in a vector of size 8+, specifically **mu11, mu12, mu21, mu22, X1, X2, H, P**. Rather than writing `t.gen_pt[4]`, I would rather write `t.X1.pt`. This is useful when the full machinery of _Primitives_ is not required and only simple selections need to be done, and the full speed of the `TTree::Draw()` function is desired.
  * **Selections.py** is the central library for dealing with object and event selections. It defines _Cut_ objects, which are context-aware selections that take in objects and apply cuts; and _Selection_ objects, which are collections of _Cuts_ along with useful auxiliary functions. To apply the muon selection to a muon, one only needs to declare a _MuonSelection_ object, and all the booleans are automatically computed, along with functions to access any or all or none of them, and functions to increment counters in a systematic way. Any selections and cuts should be added here and imported to other functions.
  * **Utilities.py** at the moment contains a single function: `SPStr()`, "signal point string", which takes in a tuple or 3 arguments and returns `'mH_mX_cTau'`. For example, `SPStr(125, 20, 13)` returns `'125_20_13'`. I have found use of this underscore-separated string to be so common that it needed its own function.

## Dumpers

`dumpers/` is my name for Python analysis scripts that print text to the screen, as opposed to making plots. Currently, the only relevant dumper is `cutEfficiencies.py`, which is a sort of test script for computing selection efficiences. As always, `runAll` submits jobs to the batch system.

## Plotters

`plotters/` is where I keep my plotting scripts. 

  * **genPlots.py** produces simple gen particle plots from the tree, calling `TTree::Draw()` directly and setting up some wrapper classes to do it neatly. It also sets _TTree_ aliases, for the same purpose. This script produces `.pdf` files directly.
  * **analyzeReco.py** produces resolution and efficiency plots, and a few dimuon plots at the moment. Basically, any plots at reco level. It uses the full _Primitives_ machinery, uses _Selections_, and only writes histograms to ROOT files. As always, `runAll` submits jobs to the batch system.
  * **makeRecoPlots.py** opens the `hadd`-ed ROOT files produced by **analyzeReco.py** and produces actual styled `.pdf` plot files. It uses the _Plotter_ library.

  
For the purposes of the Javascript-based **Viewer**, I have a script, **convertone.sh**, that converts the `.pdf` files into `.png` files. I recommend the following for multiple conversions:

```bash
parallel ./convertone.sh ::: $(ls pdfs/*.pdf)
```
