# Instructions for making limit plots

  * Set up the `combine` environment and compile; see [here](http://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/). A `cmsenv` should place the location of the compiled `combine` in `$PATH` so that just typing `combine` should work.
  * Run `getCounts.py`
      * This is a standard `runAll`; make sure that `logs/` exists, and use `--extra __trigger`
      * This runs the full selection, given by the string at the top of the file
      * This also determines the grid points for weighting, e.g. `div_2`. Currently there are `div_{1..10}` and `mul_{2..5} + mul_{10,15..50}`, meaning 23 points per signal sample.
      * The output (`cat *.out`) should be saved as `text/datcardRawInput.txt`
      * TODO: When we decide how to do the final selection, e.g. different L<sub>xy</sub> significance cuts for different lifetimes, then handling data should also be done by this script.
  * Make sure `text/realDataCounts.txt` exists, with 4 lines of the format `<mass> <CRDY> <CRQCD> <OBS>`
  * Run `generateDatacards.py`
      * Make sure that `cards/` exists
      * TODO: When systematics, observations, etc. are determined, then this script will accomodate them.
      * Cards with 0 expected signal or signal statistical uncertainty > 50% will be skipped
  * Run `combine`
      * Make sure that `combineOutput/` exists
      * Run `runCombine.py`, which is a modified `runAll.py`. It runs over all datacards found in `cards/`. The parameters are
        * `--method`
            * `AsymptoticLimits` (default) or
            * `HybridNew` (toys, takes longer, suggest changing the `--flavour`)
        * `--splitting`
            * One number 0-5 representing which of 6 jobs to do: 0 = observed, 1-5 = quantiles -2S -1S MED +1S +2S
            * So for any number of datacards, `for i in {0..5}; do python runCombine.py --method HybridNew --splitting $i; done`
            * Also useful for NOT running some quantiles, e.g. the -2S and +2S cards!
      * If running toys, `hadd` the output together with `haddHybridNew.sh`.
        * By default, this script will make a file with the relevant arguments and print a command to run, and also informs you if there are missing files. It is currently configured for 4 files per point: observed, expected, +1S, and -1S.
  * Run `makeLimitPlots.py`
      * Make sure `pdfs/` exists; plots will be written there
      * Specify the method with `--method`; ROOT files with different methods can coexist
      * This will also print all the limits to the screen for each point
