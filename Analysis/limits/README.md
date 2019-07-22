# Instructions for making limit plots

  * Set up the `combine` environment and compile; see [here](http://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/). A `cmsenv` should place the location of the compiled `combine` in `$PATH` so that just typing `combine` should work.
  * Run `getCounts.py`
      * This is a standard `runAll`; make sure that `logs/` exists
      * This runs the full selection, given by the string at the top of the file
      * This also determines the grid points for weighting, e.g. `div_2`. Currently there are `div_{1..10}` and `mul_{2..5}`, meaning 14 points per signal sample.
      * The output (`cat *.out`) should be saved as `text/datcardRawInput.txt`
      * TODO: When we decide how to do the final selection, e.g. different L<sub>xy</sub> significance cuts for different lifetimes, then handling data should also be done by this script.
  * Run `generateDatacards.py`
      * Make sure that `cards/` exists
      * TODO: When systematics, observations, etc. are determined, then this script will accomodate them.
  * Run `combine`
      * Make sure that `combineOutput/` exists
      * Run `runCombine.py`, which is a modified `runAll.py`. It runs over all datacards found in `cards/`. It is simpler; currently the only real parameter is the `--method`, which is probably either 
          * `AsymptoticLimits` (default) or
          * `HybridNew` (toys, takes longer, suggest changing the `--flavour`)
      * If running toys, `hadd` the output together with `haddHybridNew.sh`
  * Run `makeLimitPlots.py`
      * Make sure `pdfs/` exists; plots will be written there
      * Specify the method with `--method`; ROOT files with different methods can coexist
      * This will also print all the limits to the screen for each point
