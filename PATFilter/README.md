# PATFilter

Last updated: **27 Jun 2018**

This subpackage takes AOD or AODSIM files, centrally produced or privately
produced, and produces PAT Tuples. These are a subset of the original AOD files
containing only the necessary branches. PATFilter also performs some very basic
filtering and pruning, e.g. of `genParticles`, requiring that the displaced
muon collections not be empty, etc.

- [Plugins](#plugins)
- [Production of PAT Tuples](#production)
  - [Selection of data samples](#sampleselection)
  - [CRAB configuration](#crabconfig)
  - [Command line arguments](#cmdlineargs)


<a name='plugins'></a>
## Plugins

Plugins in `plugins/`:
- DimuonPreselector
- EventCounter

<a name='production'></a>
## Production of PAT Tuples

The production of PAT Tuples is done by configuring and running the scripts
`tuple_mc.py` and `tuple_data.py` in the `test/` folder.


<a name='sampleselection'></a>
### Selection of data samples

The selection of data samples is to be done in `python/MCSamples.py` by
modifications of the variable `samples`.


<a name='crabconfig'></a>
### CRAB configuration

In `tuple_mc.py` or `tuple_data.py`, adapt the variable `crab_cfg` to your
needs.

Specifically, before each job submission to CRAB, the settings of
`config.Data.publication` (`True` or `False`) and `custom_tag` (a name like
`_Jun2018-v1` or `_Jun2018-test-v1`, which makes the identification of the
submitted job much easier later on) should be provided.


<a name='cmdlineargs'></a>
### Command line arguments

- **`submit`**: submits the job(s) to CRAB
  > *Example:* `python tuple_mc.py submit`
- **`testing`**: prints the paths of the files that will be processed, but prevents
  submission to CRAB
  > *Example:* `python tuple_mc.py submit testing`
- **`create_only`**
  > *Example:* `python tuple_mc.py submit create_only`
- **`limit_memory`**: limit the requested memory to the minimally-guaranteed 2.5 GB
  (per default, 8 GB of memory are requested upon CRAB submission)
  > *Example:* `python tuple_mc.py submit limit_memory`
- **`fix_units_per_job`** (only available in `tuple_mc.py`): invokes the use of a
  hardcoded number of units per CRAB job; this number is specified via
  ```
  if not fix_units_per_job:
      cfg_val = optimize_units_per_job(sample)
  else:
      # define user-specific value here
      cfg_val = 15000
  ```
  in `tuple_mc.py` (per default, the number of CRAB jobs is determined from the
  number of events per sample according to the following table:

  | number of events | intended number of CRAB jobs |
  | ---------------- | ---------------------------- |
  | > 100M           | 1000                         |
  | 50M - 100M       | 500                          |
  | 40M - 50M        | 400                          |
  | 30M - 40M        | 300                          |
  | 10M - 30M        | 100                          |
  | 1M - 10M         | 10                           |
  | 0 - 1M           | 1                            |

  > *Example:* `python tuple_mc.py submit fix_units_per_job`

