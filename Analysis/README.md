# Displaced Dimuons Analysis

Last updated: **14 December 2018**

This subpackage contains code to analyze nTuples produced by the _Tupler_ subpackage. It mostly produces histograms. The `python` folder contains several libraries for organizing and interacting with the nTuples and their data.

  * [Python](#python)
  * [Dumpers](#dumpers)
  * [Analyzers](#analyzers)
    * [runAll.py](#runall)
    * [rehaddAll.py](#rehaddall)
  * [Plotters](#plotters)
    * [HistogramGetter and PlotterParser](#histogramgetter)
    * [convertone.sh](#convertone)
  * [Special](#special)
  * [Test](#test)

<a name="python"></a>
## Python

The `python/` directory contains the following libraries:

  * **AnalysisTools.py** contains physics analysis functions, i.e. not related to dealing with ROOT nor to simplify working with Python
  * **Analyzer.py** is a general purpose module with classes for setting up the boilerplate for running over trees. The intent is that a specific analyzer (e.g. `nMinusOnePlots.py` will import `Analyzer` and define the relevant functions, such as `analyze()` or `declareHistograms()`, then instantiate the object, which will run the analysis. It is set up to take several parameters as command-line arguments:
    * `--name`: by default the _Analyzer_ will try to run over `HTo2XTo2Mu2J` signal samples; `--name` modifies this, e.g. `DY100to200`
    * `--signalpoint`: if `--name` is `HTo2XTo4Mu` or `HTo2XTo2Mu2J`, then use the signal point parameters for various purposes; defaults to `125 20 13`
    * `--splitting`: two numbers controlling splitting: the first is how many events per file, the second is what _job_ number this is (so that the _Analyzer_ knows which subset of the tree to run over)
    * `--test`: as in the _Tupler_, runs over 1000 events and creates `test.root` instead
    * `--maxevents`: if `--test` is set, run over this maximum number of events instead of 1000
    * `--trigger`: apply the trigger selection to signal samples
    * `--cuts`: a cut string, for potential use in filenames or for control flow logic within an _Analyzer_
  * **Plotter.py** is my general-purpose plot making and styling library, with plots based on standard TDR style and with a large number of useful functions and classes that I've found useful when creating and managing plots. See the _Plotter_ documentation ([PlotterDoc](python/PlotterDoc.md) in `python/`) for full details.
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

  The _Analyzer_ library declares the _ETree_ and makes it available to the `analyze()` function as `E`. Here documents how each of the current _Primitives_ objects are declared in analysis code:

```python
Event                                         = E.getPrimitives('EVENT')
HLTPaths, HLTMuons, L1TMuons                  = E.getPrimitives('TRIGGER')
MET                                           = E.getPrimitives('MET')
Filters                                       = E.getPrimitives('FILTER')
Beamspot                                      = E.getPrimitives('BEAMSPOT')
Vertex                                        = E.getPrimitives('VERTEX')
mu11, mu12, mu21, mu22, X1, X2, H, P, extramu = E.getPrimitives('GEN')
mu1, mu2, j1, j2, X, XP, H, P, extramu        = E.getPrimitives('GEN')
Muons                                         = E.getPrimitives('PATMUON')
DSAMuons                                      = E.getPrimitives('DSAMUON')
RSAMuons                                      = E.getPrimitives('RSAMUON')
Dimuons                                       = E.getPrimitives('DIMUON')
```

  The _Primitives_ library contains extensive printing functionality, so that at any time, any object or even the entire _ETree_ can be printed in with neatly formatted output. This output is colored by default; to turn it off, one only needs to add the following line to the analysis script:

```python
Primitives.COLORON = False
```

  * **RootTools.py** contains a few small ROOT-related additions.
    * The _TVector_ section improves the Python implementation of _TVector2_, _TVector3_, and _TLorentzVector_ by adding a few functions and fixing the interface so as to be a bit more uniform.
    * The `setGenAliases()` function is a _TTree_ related function that sets gen particle aliases in the _TTree_. My current way of storing the gen particles in the tree is in a vector of size 8+, specifically **mu11, mu12, mu21, mu22, X1, X2, H, P** or **mu1, mu2, j1, j2, X, XP, H, P**. Rather than writing `t.gen_pt[4]`, I would rather write `t.X1.pt`. This is useful when the full machinery of _Primitives_ is not required and only simple selections need to be done, and the full speed of the `TTree::Draw()` function is desired.
    * The `addBinWidth` function takes in a plot and appends the bin width, with a "GeV" or "cm" as appropriate, to the *y*-axis. It has been added to all the plotters, so that it is now a standard part of all plots.
  * **Selections.py** is the central library for dealing with object and event selections. It defines _Cut_ objects, which are context-aware selections that take in objects and apply cuts; and _Selection_ objects, which are collections of _Cuts_ along with useful auxiliary functions. To apply the muon selection to a muon, one only needs to declare a _MuonSelection_ object, and all the booleans are automatically computed, along with functions to access any or all or none of them, and functions to increment counters in a systematic way. Any selections and cuts should be added here and imported to other functions.
  * **Selector.py** is a library for actually performing the object and event selections. It uses the _Selections_ library, but requires the context of the interior of an `analyze()` function of an _Analyzer_. This isn't in the _Selections_ library because it actually does the full process of the analysis selection, and is more than just a few cuts -- it combines functions from _AnalysisTools_, as well. This code used to live in an _Analyzer_ -- it is the meat of it, after all -- but it is quite similar for many purposes, so into a library it goes.
  * **SummaryPlotter.py** is a small library for making "summary plots". These are plots of a few numbers for entire signal points, e.g. the fitted &sigma; of the L<sub>xy</sub> distribution. Plotting them this way makes dependencies on the Higgs mass, the long-lived particle mass, and the lifetime more obvious, in a visual way.

For **HistogramGetter** and **PlotterParser** see the **Plotters** section.

<a name="dumpers"></a>
## Dumpers

`dumpers/` is my name for Python analysis scripts that print text to the screen, as opposed to making plots.

The following dumpers use the full _Primitives_ and _Analyzer_ machinery, using the _Selections_ library. They are derived from _Analyzer_ and work with `runAll.py`, which here is symbolically linked to the file in `../analyzers/`.

  * **cutEfficiencies.py** produces text output lines of _integrated_ selection efficiencies for muons and dimuons, in three "modes":
    * _Individual_ applies each cut individually, with no other selections
    * _Sequential_ applies each cut sequentially, in order (i.e. N&minus;1, N&minus;2, etc.)
    * _N&minus;1_ applies all cuts except for a given cut
  * **studyMatching.py** produces event dumps for studying multiple matches, i.e. when gen muons match multiple reco muons.
    * **studyMatchingMultipleGen.py** produces event dumps for studying multiple matches, i.e. when both gen muons match the same reco muon.
    * **reformatMatching.py** converts the single-line output of either of these scripts into a file with percentages instead of counts, without rerunning.
  * **studypTRes.py** produces event dumps for studying the poor p<sub>T</sub> resolution for some signal points.
  * **studyTrackerBounds.py** produces event dumps for studying the effects of changing the tracker bounds; see also _signalVertexFitEff_.
  * **studyDeltaR.py** produces event dumps for studying the effects of the proximity matching cut between gen and reco.
  * **studyPairingCriteria.py** produces output related to selecting a reconstructed dimuon pair.
  * **studyRefEfficiency.py** produces output related to a study of refitted muon reconstruction efficiency.

<a name="analyzers"></a>
## Analyzers

`analyzers/` is where I keep my analyzers: scripts that run over trees and create ROOT files containing histograms.

The following analyzers do not use the full _Primitives_ and _Analyzer_ machinery, but use parts of the interface from _Analyzer_ and take the same command line options, and hence work with `runAll.py`:

  * **genPlots.py** produces simple gen particle plots from the tree, calling `TTree::Draw()` directly and setting up some wrapper classes to do it neatly. It also sets _TTree_ aliases, for the same purpose. It writes histograms to ROOT files and runs quickly enough that a batch submission script is not necessary.

The following analyzers use the full _Primitives_ and _Analyzer_ machinery, using the _Selections_ library. They are derived from _Analyzer_ and work with `runAll.py`.

  * **recoMuonPlots.py** produces plots related to DSA, RSA, and refitted (REF) muon quantities.
  * **dimuonPlots.py** produces plots related to dimuon quantities.
  * **nMinusOnePlots.py** produces N-1 plots, distributions of the cut parameters.
  * **nMinusOneEffPlots.py** produces N-1 efficiency plots as a function of various variables.
  * **tailCumulativePlots.py** produces tail cumulative plots based on the histograms produced by **nMinusOnePlots.py**.
  * **signalRecoEffPlots.py** produces plots parametrizing the reco-gen efficiency as a function of various quantities, for signal samples.
  * **signalRecoResPlots.py** produces reco-gen resolution plots for various quantities, for signal samples.
  * **signalVertexFitEffPlots.py** produces plots parametrizing the common vertex fit efficiency as a function of various quantities, for signal samples.
  * **signalTriggerEffPlots.py** produces plots parametrizing the trigger efficiency as a function of various quantities, for signal samples.

<a name="runall"></a>
### runAll.py
**runAll.py** is a general batch/parallel submitter script for analyzers derived from _Analyzer.py_. It manages the command line arguments for the python script given as the first argument, and submits either

  * to the CONDOR submission system (default, or with `--condor`)
  * to the LXPLUS batch system, LSF (given the optional parameter `--lxbatch`)
  * to the HEPHY batch system (given the optional parameter `--hephy`)
  * locally with GNU `parallel` (given the optional parameter `--local`)

#### **Additional parameters**
`--flavour <FLAVOUR>` specifies a CONDOR queue name ("flavour") representing the maximally-allowed _wall clock_ time per job. Can be one of
  * `espresso` (20min),
  * `microcentury` (1h) -- **default**
  * `longlunch` (2h)
  * `workday` (8h)
  * `tomorrow` (1d)
  * `testmatch` (3d)
  * `nextweek` (1w)

`--queue <QUEUE>` specifies an LSF queue name representing the maximally-allowed _CPU_ time per job. Can be one of the following, corresponding in order to the CONDOR flavours above:
  * `8nm`
  * `1nh`
  * `8nh`
  * `1nd`
  * `2nd`
  * `1nw`
  * `2nw`

`--samples` is a string subset of `S2BD`, controlling whether this particular instance should run on
  * **S**ignal (`4Mu`)
  * Signal **2** (`2Mu2J`)
  * **B**ackground, or
  * **D**ata.

For example, at the moment, `signalRecoEffPlots.py` only runs on signal samples, so one would produce the appropriate plots with

```python
python runAll.py signalRecoEffPlots.py --samples S2
```

while `nMinusOnePlots.py` runs on all types of samples, so one could accept the default value for this script: explicitly,

```python
python runAll.py nMinusOnePlots.py --samples S2BD
```

At the top of _runAll.py_ are some configuration parameters defining exactly which background and data samples to run. If one desires to run over fewer samples, one can simply comment them out before calling _runAll.py_.

Additionally, there is a variable `SplittingVetoList`. This is a fixed list of scripts that should ignore the splitting parameter, as defined in the `BGSampleList` and `DataSampleList`. For example, `tailCumulativePlots.py` runs on a ROOT file of histograms, rather than as an event-by-event analyzer. It should not split jobs at all.

By default, _runAll.py_ detects the current folder. If one wishes to submit an analyzer from some other folder (I don't know why you would do this), the `--folder` parameter can specify some other folder name, relative to _Analysis/_.

`--one` is for testing batch submissions by just submitting one job of the given sample types.

`--file` allows you to specify a specific file of job arguments. This is useful if, say, a few jobs fail. You extract the argument lists, put them in a file, and submit using `--file`.

The `--extra` parameter should be passed last, if at all. It is for passing any additional arguments to the _Analyzer_ script, e.g. `--trigger` or `--cuts`. Everything after `--extra` will be passed directly to the given _Analyzer_, except that all instances of `__` will be replaced with `--`. This is necessary because if they are passed with `--`, the parser in _runAll.py_ will interpret them as options for itself, rather than additional options for the _Analyzer_. To do: this can probably be improved by requiring that the parameter be a single quoted string, but it works for now.

### CONDOR submission workflow for analyzers

CONDOR mode will write all its log files to a folder `logs/`, organized in a useful way. Each call to `condor_submit` produces a new folder with the executable, the submission script, and all the log files. `getFailedCondorJobs.py` looks through these log files and reports useful information.

Also useful is the command `condor_q -format "%s\n" Args`, which prints all the currently running jobs' arguments to the screen. It is suitable for, say,

```bash
condor_q -format "%s\n" Args > submitFile
python runAll.py . --file submitFile --local &
```

The following example suggests a workflow that can be used to run _Analyzers_ on samples using CONDOR. It demonstrates the combined use of many of the parameters described in this section.

```bash
# Run your own analysis script ("myAnalyzer.py") on signal, background and data
# samples on CONDOR (using the "longlunch" queue) and passing custom arguments
# to the analyzer
python runAll.py myAnalyzer.py --samples S2BD --condor --flavour longlunch \
  --extra __cutstring MySelectionString

# monitor the submission status with `condor_q` and wait until all jobs have finished

# Check which jobs have failed due to exceeding CPU wall time
# and which jobs have produced non-empty error files
./getFailedCondorJobs.py

# If there are failed jobs, the output might look like this:
# 1 overtime jobs found:
#  run1/myAnalyzer_496
#
#  myAnalyzer.py --name DoubleMuonRun2016H-07Aug17 --splitting 50000 63

# Run the failed job again locally before hadding all the new output files
python myAnalyzer.py --name DoubleMuonRun2016H-07Aug17 --splitting 50000 63
```

<a name="rehaddall"></a>
### rehaddAll.py
This script assists with hadding and organizing the many ROOT files that the various analyzers produce.

<a name="plotters"></a>
## Plotters

`plotters/` is where I keep my plotting scripts. Mostly, they take root files from `../analyzers/roots/` and create PDFs.

The following plotters open the `hadd`-ed ROOT files produced by their respective analyzer and produce actual styled `.pdf` plot files, using the _Plotter_ library.

  * **makeGenPlots.py** makes plots from ROOT files produced by **genPlots.py**
  * **makeRecoMuonPlots.py** makes plots from ROOT files produced by **recoMuonPlots.py**
  * **makeDimuonPlots.py** makes plots from ROOT files produced by **dimuonPlots.py**
  * **makeNMinusOnePlots.py** makes plots from ROOT files produced by **nMinusOnePlots.py**
  * **makeNMinusOneEffPlots.py** makes plots from ROOT files produced by **nMinusOneEffPlots.py**
  * **makeTailCumulativePlots.py** makes plots from ROOT files produced by **tailCumulativePlots.py**
  * **makeSignalRecoEffPlots.py** makes plots from ROOT files produced by **signalRecoEffPlots.py**
  * **makeSignalRecoResPlots.py** makes plots from ROOT files produced by **signalRecoResPlots.py**
  * **makeSignalVertexFitEffPlots.py** makes plots from ROOT files produced by **signalVertexFitEffPlots.py**
  * **makeSignalTriggerEffPlots.py** makes plots from ROOT files produced by **signalTriggerEffPlots.py**

The following plotters open a text file produced by a dumper and produce actual styled `.pdf` plot files, using the _Plotter_ library.

  * **makeCutTablePlots.py** makes plots from the text file output of **cutEfficiencies.py**

<a name="histogramgetter"></a>
### HistogramGetter and PlotterParser

`HistogramGetter.py` is a small module designed for getting histograms from files in a systematic way (given the same naming convention), and for storing information about plotting (such as styles, e.g. colors and pretty TLatex names, as well as the relative sample weights).

In other words, it's a simple Python module, but really important so that code is not duplicated and spread across several plotting scripts!

`PlotterParser.py` is an even smaller module that contains a few common parameters, such as the cut string and whether this runs over trigger root files. They can be used to run a _Plotter_ in a programmatic way, and its functionality is used in `pilotPlotters.py`, which runs sets of plotters in a loop.

<a name="convertone"></a>
### convertone.sh
  
For the purposes of the Javascript-based _Viewer_, I have a script, **convertone.sh**, that converts the `.pdf` files into `.png` files. I recommend the following for multiple conversions:

```bash
parallel ./convertone.sh ::: $(ls pdfs/*.pdf)
```

or for a list of files:

```bash
parallel -a FILE ./convertone.sh
```

*convertone.sh* takes three possible options, which are slight tweaks to the PNG output based on what the input PDF is:
  * `--normal` (or nothing): for normal 800&times;600 plots
  * `--ratioSquash`: for plots with a ratio plot that are 800&times;600 (it cuts off otherwise)
  * `--ratioFull`: for plots with a ratio plot that are 800&times;800

<a name="printintegrals"></a>
### printIntegrals.py

`printIntegrals.py` is a dedicated script for printing histogram integrals. It assumes a structure, i.e. where the ROOT files are located and named.

This formalizes some functionality previously in a few scripts, but which was handled somewhat clunkily since certain visual functions needed to be turned off, requiring a special flag.

Generally the usage is something like

```bash
python printIntegrals.py -c D -s Prompt_NoSignal -k Dim_pT -b1 0 -b2 N
```

<a name="special"></a>
## Special

`special/` is where I keep some very special-purpose analyzers. They were written for one-time checks, using specific files.

  * **comparePATtoAOD.py** takes 2 nTuples, for two signal points, one produced from a PAT Tuple and the other produced directly from AOD, and produces a few histograms, comparing the contents bin by bin, and printing to the screen if anything is different. This script served as a proof that _PATFilter_ did not change anything significant from AOD.

  * **compareBSGentoLinGen.py** takes new (September 2018) nTuples and compares the effect of using the old (SV-reference point) gen quantities to the new (BS-reference point) quantities when matching to reco. The behavior is understood, and the effects have been observed and documented. Its plotter is also used for the next script.

  * **compareRefPoints.py** takes 2 nTuples, old and new, and compares the effect of changing the d<sub>0</sub> and L<sub>xy</sub> reference points from (0, 0, 0) to the beamspot. The effect is very small.

The following script is deprecated and has been removed, having been replaced by other analyzers and dumpers.

  * **compareTrackerTweak.py** takes 2 nTuples, for two signal points, one produced without a constraint forcing vertex refits to be within the tracker, and one with produced with it. For the purposes of this analysis, we need to _remove_ the constraint (namely, set it to something large). This script, and its corresponding plotter script **plotTrackerTweak.py**, produce gen L<sub>xy</sub> distributions and efficiency as a function of gen L<sub>xy</sub>, and show the efficiency gain from removing the constraint, as well as the difference in distributions for large L<sub>xy</sub>.

<a name="test"></a>
## Test
`test/` contains several important testing scripts. They are standalone python or shell scripts that are specifically aimed at testing various libraries: _Primitives_, _Selections_, all the _Analyzers_, and the dump functionality of _Primitives_. These scripts generally run successfully if there are no syntax errors or other issues in the whole analysis ecosystem.
