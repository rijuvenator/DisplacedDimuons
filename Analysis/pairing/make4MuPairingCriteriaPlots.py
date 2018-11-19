import re
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
from DisplacedDimuons.Common.Utilities import SPStr, SPLumiStr
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
import DisplacedDimuons.Analysis.HistogramGetter as HistogramGetter
import DisplacedDimuons.Analysis.PlotterParser as PlotterParser

f = R.TFile.Open('roots/4MuPairingCriteriaPlots_Trig_HTo2XTo4Mu.root')

def makePlot(fs, sp, quantity):
    # configy type stuff
    tags = ('Matched', 'Junk')
    legs = {'Matched':'Matched', 'Junk':'Incorrect Pair'}
    cols = {'Matched':R.kBlue, 'Junk':R.kRed}

    # get/add histograms
    if sp is None:
        h = {}
        for tag in tags:
            h[tag] = HistogramGetter.getHistogram(f, (fs, SIGNALPOINTS[0]), quantity+'_'+tag).Clone()
        for SP in SIGNALPOINTS[1:]:
            for tag in tags:
                h[tag].Add(HistogramGetter.getHistogram(f, (fs, SP), quantity+'_'+tag))
    else:
        h = {}
        for tag in tags:
            h[tag] = HistogramGetter.getHistogram(f, (fs, sp), quantity+'_'+tag).Clone()

    # make plots
    p = {}
    for tag in tags:
        p[tag] = Plotter.Plot(h[tag], legs[tag], 'l', 'hist')

    # canvas, plots, min max
    canvas = Plotter.Canvas(lumi=SPLumiStr(fs, sp) if sp is not None else fs, logy=True)
    for tag in tags:
        canvas.addMainPlot(p[tag])
    canvas.setMaximum()

    # colors
    for tag in tags:
        p[tag].SetLineColor(cols[tag])

    # legend, cleanup
    canvas.makeLegend(lWidth=.2, pos='tr')
    canvas.legend.resizeHeight()

    canvas.cleanup('pdfs/4MuPC_{}_HTo2XTo{}_{}.pdf'.format(quantity, fs, SPStr(sp) if sp is not None else 'Global'))

for fs in ('4Mu',):
    for sp in [None] + SIGNALPOINTS:
        for quantity in ('vtxChi2', 'deltaR', 'cosAlpha', 'deltaM'):
            makePlot(fs, sp, quantity)