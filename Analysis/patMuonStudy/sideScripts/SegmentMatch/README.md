# Segment match study

## Analyzers
  * **Distributions** is for the deltaR and fSeg distributions for Prox and Seg matches. Most useful for looking at data to inform what sort of cuts are useful.
  * **SignalLxy** is for looking at the effect of various cuts on PAT matching on signal Lxy. Both require extra keywords in _AnalysisTools_ and consequently in _Selector_.
    * **fSeg** is for the fraction of matched segments
    * **deltaR** is for the proximity match deltaR


## Plotters
  * The plotters are straightforward mostly.
  * The segment match root files should be named a little more sensibly, but since currently a framework change is required to study any of these, maybe it is fine if it's quick and dirty.
  * For the deltaR plotter, the usual `TGraphAsymmErrors` is commented out because deltaR of 0.05 fluctuates the yield above 100%, so I just did a `TH1::Divide`
