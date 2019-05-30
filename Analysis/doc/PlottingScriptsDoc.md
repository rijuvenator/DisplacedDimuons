# Using the plotting scripts in `plotters/`

Last updated: **10 May 2019**

This documents, not how to use _Plotter_ (see `PlotterDoc.md` for that), but rather some notes on specifics of the particular scripts in `plotters/`.

## HistogramGetter
This is a simple python module for getting histograms made with the analyzers. It parses the keys and organizes them into a `HISTS` dictionary. The code is

```python
import HistogramGetter

HISTS = HistogramGetter.getHistograms('FILE.root')
f = R.TFile.Open('FILE.root')
```

That last line is for getting the file handle again, since _HistogramGetter_ closes the file that is passed. Maybe some of the plotters want to re-clone the histogram or something.

`HISTS` is a dictionary with two layers: `HISTS[sample][key]`. `sample` is either a string -- for data and background MC -- or a tuple of length two, of format `(FS, SP)`, where `FS` is a string (either `'2Mu2J'` or `'4Mu'`) and `SP` is a signalpoint tuple (e.g. `(125, 20, 13)`). So you can tell whether this sample is signal or not by whether the sample (reference) is of type string or of type tuple.

_HistogramGetter_ also saves some useful constants related to plotting. It saves the integrated luminosity. It defines some standard LaTeX names for each sample, and some associated colors. And it saves the overall weight to be used for relative weighting of MC background samples, for example. This is all stored in `PLOTCONFIG` under the sample name as a dictionary.

Finally, _HistogramGetter_ contains some scripts for getting sums of signal sample plots, getting the weighted MC histograms, and getting sums of data plots.

## Structure and booleans
### Structure
Generally, the plotters have several functions, one of which is general purpose and just plots everything, and others which may plot 2D plots or stack plots or do extra Gaussian fitting or other things. Usually I use `SPStr` and `SPLumiStr` for convenience in formatting signal sample names as strings.

At the bottom the functions are actually called. Some functions run over all the relevant samples, others take them as input.

The general 1D function usually skips 2D plots, which have `VS` in them. I also recently skip most of the per-MC-background plots, since we usually only care about the stack.

I get or clone the histogram, add the overflow and underflow (see _RootTools_) with

```python
RT.addFlows(h)
```

rebin if necessary and then make the plots using _Plotter_.

The functions are then called at the bottom of the script.

#### Note about file names

Note that usually, I do not change the file name. It's different for each plotter, but I don't laboriously change the names. Instead, I keep separate versions of ROOT files and symbolically link to the "main" file. So I need to do this in between runs of the plotter, and change the `TRIGGER` and `CUTSTRING` and etc. as appropriate; see below.

### Parameters
There were starting to be several configuration parameters at the top. I've kept the explanation below for the other scripts.

  * `TRIGGER`: whether or not a signal sample was run with the trigger event selection. Setting this to true automatically adds `Trig-` to the beginning of the `HTo2XTo...` name that is usually used, and so the file name will have `Trig-HTo2XTo...` in it, as well.
  * `CUTSTRING`: similar to `TRIGGER`, it's the `--cuts` string from the analyzer, which is probably what the real ROOT file name is called, as well. This is usually automatically propagated to the file name. Don't forget the underscore -- it's usually at the beginning, so that you can do things like

```python
fname = 'Dim_{}{}_{}{}.pdf'.format(plotName, CUTSTRING, 'Trig-' if TRIGGER else '', sampleName)
```

  * `MCONLY`: I find myself needing to make MC stack plots with and without data. This is a global flag that tells everything in the file that the ROOT file has no data, or at least to ignore if it does. In the stack plot code, it does not add data histograms, and the resulting "sample name", instead of being something like _Stack_ or _Stack-Log-Rat_, is _StackMC_ or _StackMC-Log_. This is accounted for in the viewer as well.

_PlotterParser_ is an argument parser that a couple scripts (possibly more, soon) use to handle the parameters. Respectively,

  * `--trigger` sets `TRIGGER` to `True`
  * `--cutstring _XXX` sets `CUTSTRING` to `_XXX`
  * `--mconly` sets `MCONLY` to `True`
