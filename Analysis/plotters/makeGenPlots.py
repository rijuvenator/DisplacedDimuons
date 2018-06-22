import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
from DisplacedDimuons.Common.Utilities import SPStr
import HistogramGetter

# get histograms
HISTS = HistogramGetter.getHistograms('../analyzers/roots/GenPlots.root')
f = R.TFile.Open('../analyzers/roots/GenPlots.root')

# make plots using Plotter class per signal point
def makePerSignalPlots(fs):
    for sp in SIGNALPOINTS:
        for key in HISTS[(fs, sp)]:
            h = HISTS[(fs, sp)][key]
            p = Plotter.Plot(h, '', 'p', 'hist')
            canvas = Plotter.Canvas(lumi='{} ({}, {}, {})'.format(fs, *sp))
            canvas.addMainPlot(p)
            p.SetLineColor(R.kBlue)
            pave = canvas.makeStatsBox(p, color=R.kBlue)
            canvas.cleanup('pdfs/Gen_{}_HTo2XTo{}_{}.pdf'.format(key, fs, SPStr(sp)))

for fs in ('4Mu', '2Mu2J'):
    makePerSignalPlots(fs)
