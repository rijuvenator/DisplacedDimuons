# PATFilter

Last updated: **5 Jul 2018**

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

The production of PAT Tuples is done by running the scripts
`tuple_mc.py` and `tuple_data.py` in the `test/` folder.


<a name='sampleselection'></a>
### Selection of data samples

The selection of data samples is to be done in `python/MCSamples.py` by
modifications of the variable `samples`.


<a name='crabconfig'></a>
### CRAB configuration

In the file `test/crab_cfg.json`, make the necessary changes and adapt the
dictionaries `config_mc` and `config_data` to your needs.

> Special care has to be taken with quotation marks: The "outer" layer of
> quotation marks will be removed in the final config file. (Examples: `"True"`
> becomes `True`, `"'crab'"` becomes `'crab'` etc.)

Some of the lines are dynamically modified in the main scripts
`test/tuple_mc.py` and `tuple_data.py`. However, before the actual submission,
the user is prompted and shown the final crab configuration and can then
decide to either continue submitting or abort the script.


<a name='cmdlineargs'></a>
### Command line arguments

The command line argument `submit` is required for all other arguments to take
effect. Apart from that, all arguments can be applied in any combination.

> The following examples assume the user to be in the `test/` folder.

- **`submit`**: submits the job(s) to CRAB

  > *Example:* `python tuple_mc.py submit`

- **`testing`**: prints the paths of the files that will be processed, but prevents
  submission to CRAB

  > *Example:* `python tuple_mc.py submit testing`

- **`dryrun`**: simulates running on CRAB (without actually submitting) and
  gives estimates of 1) the expected number of CRAB jobs (i.e., the splitting
  parameter) and 2) the run time of the production. (See the
  [twiki](https://twiki.cern.ch/twiki/bin/view/CMSPublic/CRAB3Commands#crab_submit_dryrun)
  for further information.)

  > *Example:* `python tuple_mc.py submit dryrun`

- **`disable_confirmation`**: per default, the user is shown the final CRAB
  configuration and has to invoke the actual CRAB submission by confirming it -
  this command line argument disables the confirmation prompt

  > *Example:* `python tuple_mc.py submit disable_confirmation`

- **`create_only`**

  > *Example:* `python tuple_mc.py submit create_only`

- **`limit_memory`**: limit the requested memory to the minimally-guaranteed 2.5 GB
  (per default, 8 GB of memory are requested upon CRAB submission)

  > *Example:* `python tuple_mc.py submit limit_memory`

- **`fix_units_per_job`** (only available for `tuple_mc.py`): invokes the use of a
  hardcoded number of units per CRAB job; this number is specified via
  `crab_cfg['config.Data.unitsPerJob'] = "15000"` in `tuple_mc.py` (per default,
  the number of CRAB jobs is determined from the number of events per sample
  according to the table below).

  > *Example:* `python tuple_mc.py submit fix_units_per_job`

| **number of events** | **intended number of CRAB jobs** |
| -------------------- | -------------------------------- |
| > 100M               | 1000                             |
| 50M - 100M           | 500                              |
| 40M - 50M            | 400                              |
| 30M - 40M            | 300                              |
| 10M - 30M            | 100                              |
| 1M - 10M             | 10                               |
| 0 - 1M               | 1                                |


## Documentation of CRAB productions

| **Date** | **Tag** | **Produced data samples** | **Produced MC samples** | **Comments / further details** |
| -------- | ------- | ------------------------- | ----------------------- | ------------------------------ |
| June 2018 | `_Jun2018-v1` | DoubleMuonRun2016[B-H] | see [MCSamples.py @ 99f079a2](https://gitlab.cern.ch/DisplacedDimuons/DisplacedDimuons/blob/99f079a27f1a7bf56284f09950a9a126f9b88b3e/PATFilter/python/MCSamples.py) | see [Dropbox paper](https://paper.dropbox.com/doc/DataMC-sample-production-on-CRAB-_Jun2018-v1--AG58Se6CYfWhvhEe48zMMTHsAQ-fBfzdJAQJskeXrdHaU7xq) |
