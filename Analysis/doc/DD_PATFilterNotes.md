# Slava's PATFilter
### April 24, 2018

* `test` has 2 modules and a CRAB configuration
	* MC and data
* imports common PAT Tupler configuration
	* Embed tracks
	* `switchOnTrigger` tells you which L2 objects triggered each path
	* `allowUnscheduled` is required to run the trigger information
		* This is default in `CMSSW_9_1_X` onwards
	* `outputModule = ''` so that `switchOnTrigger` doesn't modify the output module
	* no need for match embedding -- do it by hand
	* kept the MET filters, and produced Type 1 corrected MET
* `tuple_mc`
	* redefine MC matching: requires matching charge, and p<sub>T</sub>
	* commented out: prune MC leptons used to trim Gen Particles
	* Main HLT Filter:
		* Save `HLT_L2DoubleMu*_NoVertex*`
		* HLT report outputs information about passes and fails for triggers
	* Dimuon Preselector
		* keep at least 2 muons, etc.
		* the p<sub>T</sub> cut is looser so if it runs after it does nothing
		* perhaps it's not useful -- just filter on the trigger except for signal
* `tuple_data`
	* similar to MC
	* PAT is designed to run on MC and then drop some modules from the process: the function removes modules one by one
* Don't want to run this PAT part too often
	* start with 1/3 of data or one period
* MC Samples
	* Mostly Drell Yan background: major 120M samples DYJetsToLL, 50-$\infty$
	* DY $\rightarrow \tau\tau$
* Branch Sizes
	* Biggest: patMuon
	* Then all the trigger information
	* Then all the tracks and track extras