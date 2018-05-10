# Displaced Dimuons Common

Last updated: 10 May 2018

This subpackage contains common libraries that are used in multiple places.

## Python

The `python/` directory contains the following libraries:

  * **Constants.py** contains common literals: file paths and lists of signal points. It's better to import these from a central location so that they don't have to changed in multiple places.
  * **Utilities.py** at the moment contains a single function: `SPStr()`, "signal point string", which takes in a tuple or 3 arguments and returns `'mH_mX_cTau'`. For example, `SPStr(125, 20, 13)` returns `'125_20_13'`. I have found use of this underscore-separated string to be so common that it needed its own function. Additionally, there is a SignalPoint class, for doing things in an object-oriented way, given that a signal point is a specific tuple that has some context associated with the values.
