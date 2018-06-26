# Displaced Dimuons Common

Last updated: **26 June 2018**

This subpackage contains common libraries that are used in multiple places.

  * [Python](#python)
  * [Scripts](#scripts)

<a name="python"></a>
## Python

The `python/` directory contains the following libraries:

  * **Constants.py** contains common literals: file paths and lists of signal points. It's better to import these from a central location so that they don't have to changed in multiple places.
  * **Utilities.py** at the moment contains a single function: `SPStr()`, "signal point string", which takes in a tuple or 3 arguments and returns `'mH_mX_cTau'`. For example, `SPStr(125, 20, 13)` returns `'125_20_13'`. I have found use of this underscore-separated string to be so common that it needed its own function. Additionally, there is a SignalPoint class, for doing things in an object-oriented way, given that a signal point is a specific tuple that has some context associated with the values.
  * **DataHandler.py** is a Python library for working with DAS and datasets. It will call the appropriate command-line DAS commands and get lists of datasets and files automatically, given the correct parameters. Other classes for other types of datasets should be added here, too, so that any file that deals with datasets has object-oriented information about the dataset, e.g. files, MC parameters, the dataset name, etc. Finally, it also stores information about nTuples (and soon, plotting styles).

<a name="scripts"></a>
## Scripts

The `scripts/` directory contains three important scripts which generate the .dat data files, critical for the operation of the `DataHandler` library, and therefore, for _CFGParser_ in _Tupler_ and for _Analyzer_ in _Analysis_.

  * **generateSignalDATFile.py** runs the DAS client and creates the signal .dat file found in `dat/`. It should be updated as we produce more signal PAT Tuples. The record format is known and parsed carefully by _DataHandler_.
  * **generateBackgroundDATFile.py** uses the background MC sample objects from _MCSamples.py_ in _PATFilter_ and creates the background MC .dat file found in `dat/`. At the moment, it relies on the fact that all the signal samples are last, and all the background samples are first. This can be made more robust at some other time. The record format is known and parsed carefully by _DataHandler_.
  * **generateNTupleDATFile.py** generates a list of known nTuples, keyed by sample name (see the .dat files and _DataHandler_). It should produce a file containing lines of one of the following four formats:

```
<NAME> <FILE>
<NAME> <FILE 1> <FILE 2> ...
<NAME> <FILE> <NFILES>
<NAME> <FILE> <NSTART> <NEND>
```

  where the `NAME` is the sample name string and `FILE` is a full path to a .root file or a _template_ root file. The datasets contain a `getNTuples()` method which will return paths to nTuples, used by _Analyzer_ in _Analysis_ for setting up files and trees and loops over trees.

  * If there are two quantities and the last is a .root file, _DataHandler_ will return the file name.
  * If there are more than two quantities and the third is a .root file, _DataHandler_ will return a list of strings `FILE1.root` onwards.
  * If there are three quantities and the last is an integer, _DataHandler_ will return a list of strings `FILE_1.root` through `FILE_N.root`.
  * If there are four quantities and the last two are integers, _DataHandler_ will return a list of strings `FILE_N1.root` through `FILE_N2.root`.

Note that the data .dat file is created by hand, as it only contains one sample at the moment.
