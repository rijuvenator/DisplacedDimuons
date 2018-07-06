# How to run the nTupler

Last updated: **6 July 2018**

A VOMS proxy is required for using pretty much any of the files in this directory:
```bash
voms-proxy-init -voms cms
```

This directory contains three top-level files.

## NTupler_cfg.py

**NTupler_cfg.py** is the `cmsRun` configuration file to run the _SimpleNTupler_. It is a plain configuration file, loading only CMSSW Python modules and fragments, as well as the initialization files in `Modules/`. The lines at the top indicate the external parameters. They may be set manually, however, **runNTupler.py** and **submitAll.py** set all of these parameters automatically and handle submitting of jobs.
  * `MAXEVENTS` is the maximum number of events to process
  * `INPUTFILES` is a list of filenames, the input to `cms.Source`
  * `OUTPUTFILE` is the name of the output file
  * `ISMC` is whether or not the input files are MC
  * `ISSIGNAL` is whether or not the input files are signal
  * `FINALSTATE` is either `'4Mu'` or `'2Mu2J'`, when running on signal
  * `GENS_TAG` is either `('prunedGenParticles', '', 'PAT')` or `('genParticles',)`; the former if the input file is a PAT Tuple, the latter if not
  * `SOURCE` is either `'PAT'`, `'AOD'`, or `'GEN'`, depending on the type of the input source and the branches desired

## runNTupler.py

**runNTupler.py** is the main atomic submitter script. The basic usage is

```bash
python runNTupler.py NAME [OPTIONS]
```

This script opens **NTupler_cfg.py**, sets the external parameters, writes a new cmsRun file, and submits the job, either locally, to the LXBATCH system, or to CRAB (automatically creating and cleaning up a submissions script in both cases).

The behavior of the options can be found in `Utilities/CFGParser.py`. Some documentation of some of the most important options follows.

Exactly one of the following options may be passed:
  * `--crab`: submits the desired dataset job to CRAB, using the CRAB configuration script embedded within
  * `--batch`: submits the desired dataset job to LXBATCH, using the LXBATCH submission script embedded within
  * `--test`: submits the desired dataset job *locally* for 1000 events and only the first file
  * no option: submits the desired dataset job *locally* for the entire dataset

If running on signal (e.g. `HTo2XTo4Mu`), parameterized by (m<sub>H</sub>, m<sub>X</sub>, c&tau;), the `--signalpoint` option specifies which signal point to run on. For example:

```bash
python runNTupler.py HTo2XTo4Mu --signalpoint 125 20 13
```

Exactly one of the following options may be passed:
  * `--genonly`: specifies that the input source is GEN-SIM, and that the nTupler is only to access and write GenBranches, such as genParticles and GenEventInfoProduct. **Deprecated but still works for now**.
  * `--aodonly`: specifies that the input source is AOD, and that the nTupler should write everything except the branches that involve the PAT collections, such as trigger, MET, and pat::Muons.
  * no option: specifies that the input source is a PAT Tuple created by PATFilter, and that the nTupler should write everything.

The `--verbose` option prints the arguments, the configuration object, the newly created cmsRun file, and the grid submission script, if any. The `--nosubmit` option is a final flag to prevent any submission, useful if, say, checking the content of the submission scripts is desired.

Some examples of usage:

```bash
python runNTupler.py DY50toInf --crab
python runNTupler.py HTo2XTo4Mu --signalpoint 125 20 13 --batch --outdir /afs/cern.ch/user/a/adasgupt/
python runNTupler.py HTo2XTo4Mu --signalpoint 200 20 7 --genonly --crab
python runNTupler.py DoubleMuonRun2016D-07Aug17 --test --verbose
```

## submitAll.py

Finally, **submitAll.py** submits the full suite of jobs; all that is needed is to change the `MODE` variable inside the script as desired. If desired, each of the submission blocks can be turned off with the `Do_*` booleans, and the user is free to place additional restrictions on which samples will be run (for example, by adding a conditional statement inside the loop).

Currently, the script will submit 84 jobs, all running on PAT Tuples, corresponding to
  * 33 jobs for all HTo2XTo4Mu signal points
  * 33 jobs for all HTo2XTo2Mu2J signal points
  * 11 jobs for most background MC samples
  * 7 jobs for data DoubleMuon Run2016 B-H

Note that the WZ and ZZ samples have an extra dataset which will be merged afterwards, resulting in 82 total nTuples.

## Utilities/

The `Utilities/` directory contains one important library.

  * **CFGParser.py**: a Python library for configuring and running cmsRun jobs with crab, batch systems, or locally, with several command line options for setting test modes, printing output, changing output file patterns, and more. It uses the full *DataHandler* machinery.
