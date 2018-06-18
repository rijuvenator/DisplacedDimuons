# Displaced Dimuons

Last updated: **13 June 2017**

This is the framework for studying displaced dimuons at CMS. The code base contains Pythia fragments for generating signal Monte Carlo samples, code to produce PAT Tuples from AOD or AODSIM, EDAnalyzer code to produce ROOT trees from PAT Tuples, and analysis code for making plots from trees.

  * [Installation Instructions](#installation-instructions)
    * [Prerequisites](#prerequisites)
    * [Installation](#installation)
  * [Package Overview](#package-overview)
    * [PATFilter](#patfilter)
    * [Tupler](#tupler)
    * [Analysis](#analysis)
    * [Common](#common)
    * [GenStudies](#genstudies)
    * [SignalSamples](#signalsamples)
    * [Viewer](#viewer)

<a name="installation-instructions"></a>
## Installation Instructions
<a name="prerequisites"></a>
### Prerequisites
  * Be a CMS member with a NICE account.
  * Email Riju, who will add you to the project and give you permissions.
  * Set up an SSH key and add it to your GitLab account.
    * [Generate an SSH key](https://help.github.com/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent/), if you don't have one
    * Copy the text of the public key
    * [Add your SSH key to GitLab](https://docs.gitlab.com/ee/ssh/). From the link:

    > Navigate to the 'SSH Keys' tab in your 'Profile Settings'. Paste your key in the 'Key' section and give it a relevant 'Title'. Use an identifiable title like 'Work Laptop - Windows 7' or 'Home MacBook Pro 15'.
    >
    > If you manually copied your public SSH key make sure you copied the entire key starting with ssh-rsa and ending with your email.
  * [Set up your VOMS proxy](https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookStartingGrid#ObtainingCert).

<a name="installation"></a>
### Installation
We are currently using `CMSSW_8_0_31` for analysis of 2016 data.

To install the package, run each of these commands. It's mostly the basic workflow: check out a CMSSW release, set up the environment, clone the repository, compile. However, there is one very important detail:

**You must run `git cms-init`.**

If you do not do this, you will not be able to check out the `RecoVertex/VertexTools` package from CMSSW. This is required because we need to set two of the values to different values.

```bash
source /cvmfs/cms.cern.ch/cmsset_default.sh
cmsrel CMSSW_8_0_31
cd CMSSW_8_0_31/src/
cmsenv
git cms-init
git clone ssh://git@gitlab.cern.ch:7999/DisplacedDimuons/DisplacedDimuons.git
git cms-addpkg RecoVertex/VertexTools
pushd RecoVertex/VertexTools/src/
sed -i '/TrackerBoundsRadius = /s/112/500/' SequentialVertexFitter.cc
sed -i '/TrackerBoundsHalfLength = /s/273\.5/1000\./' SequentialVertexFitter.cc
popd
scram b -j8
```

#### Explanation by line number

1. Gives access to `scram`, `cmsrel`, `cmsenv`, etc. Not needed for LXPLUS.
2. Creates a CMSSW working directory.
3. Changes to the `src/` subdirectory of CMSSW.
4. Sets up CMSSW environment.
5. Initializes environment for checking out CMSSW packages. **VERY IMPORTANT.**
6. Clones this repository.
7. Checks out the `RecoVertex/VertexTools` package from CMSSW.
8. Changes to the `RecoVertex/VertexTools/src/` subdirectory.
9. Changes hardcoded value of `TrackerBoundsRadius`.
10. Changes hardcoded value of `TrackerBoundsHalfLength`.
11. Returns to the `src/` subdirectory of CMSSW.
12. Builds, compiles, and links all the code.

<a name="package-overview"></a>
## Package Overview

This is a general overview of each folder in the top level directory of the Displaced Dimuons analysis package. Each subpackage contains additional detailed documentation. Loosely speaking, each folder corresponds to a high-level "step" of the analysis. These steps and the folders are described in a little more detail below.

  * **Step 0**: Produce or begin with official AODSIM samples.
  * **Step 1**: Produce PAT Tuples using the _PATFilter_ subpackage.
  * **Step 2**: Produce ROOT trees, a.k.a. nTuples, using the _Tupler_ subpackage.
  * **Step 3**: Produce plots using the _Analysis_ subpackage.

<a name="patfilter"></a>
### PATFilter
This subpackage takes AOD or AODSIM files, centrally produced or privately produced, and produces PAT Tuples. These are a subset of the original AOD files containing only the necessary branches. _PATFilter_ also performs some very basic filtering and pruning, e.g. of `genParticles`, requiring that the displaced muon collections not be empty, etc.

One produces PAT Tuples by running the `tuple_mc.py` and `tuple_data.py` scripts in the `test/` directory.

<a name="tupler"></a>
### Tupler
This subpackage takes PAT Tuples produced by _PATFilter_ and produces flat ROOT trees, a.k.a. nTuples.

The main engine is the _SimpleNTupler_ plugin, an EDAnalyzer written for the CMSSW framework. The different quantities are organized into subclasses. The `python/` directory contains the necessary scripts to run and submit jobs for producing trees.

<a name="analysis"></a>
### Analysis
This subpackage takes nTuples produced by _Tupler_ and produces plots.

Loosely speaking, it is organized into four directories:

  * _analyzers_ contains scripts to run over trees and produce ROOT files with plots
  * _plotters_ contains scripts to combine, stack, and style plots into PDFs
  * _python_ contains libraries and modules to assist with making plots and doing analysis
  * _test_ contains scripts to test various functionalities of the rest of the subpackage

<a name="common"></a>
### Common

This subpackage contains a few common constants and modules that are used by other subpackages that don't necessarily belong in dedicated libraries of their own. For example, things like hard-coded lists, file paths, common string functions, etc.

<a name="genstudies"></a>
### GenStudies

This subpackage contains standalone Python code to make quick histograms from GEN-SIM samples. Much of its functionality has been integrated into _Analysis_.

<a name="signalsamples"></a>
### SignalSamples

This folder contains the Pythia fragments used to generate the different signal samples used in the analysis.

<a name="viewer"></a>
### Viewer

This folder contains a toy JavaScript-based viewer for looking at plots in an interactive way.
