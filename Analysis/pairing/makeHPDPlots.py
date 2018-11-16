import re
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
from DisplacedDimuons.Common.Utilities import SPStr, SPLumiStr
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
import DisplacedDimuons.Analysis.HistogramGetter as HistogramGetter
import DisplacedDimuons.Analysis.PlotterParser as PlotterParser

f = R.TFile.Open('roots/HPDPlots_Trig_HTo2XTo2Mu2J.root')

def makePTCutPlot(fs, sp=None):
    # configy type stuff
    legs=('All', 'Matched', 'Wrong', 'Right', 'Hopeless', 'Lost')
    tags=['pT_'+tag for tag in legs]
    cols=(R.kBlack, R.kGreen, R.kOrange, R.kBlue, R.kRed, R.kMagenta)

    # get/add histograms
    if sp is None:
        h = {}
        for tag in tags:
            h[tag] = HistogramGetter.getHistogram(f, (fs, SIGNALPOINTS[0]), tag).Clone()
        for SP in SIGNALPOINTS[1:]:
            for tag in tags:
                h[tag].Add(HistogramGetter.getHistogram(f, (fs, SP), tag))
    else:
        h = {}
        for tag in tags:
            h[tag] = HistogramGetter.getHistogram(f, (fs, sp), tag).Clone()

    # make plots
    p = {}
    for i,tag in enumerate(tags):
        p[tag] = Plotter.Plot(h[tag], legs[i], 'l', 'hist')

    # canvas, plots, min max
    canvas = Plotter.Canvas(lumi=SPLumiStr(fs, sp) if sp is not None else fs, logy=True)
    for tag in tags:
        canvas.addMainPlot(p[tag])
    canvas.setMaximum()
    if False:
        canvas.firstPlot.SetMinimum(0)
    else:
        canvas.firstPlot.SetMinimum(1.)
    #canvas.firstPlot.GetXaxis().SetRangeUser(0., 200.)
    canvas.firstPlot.GetXaxis().SetRangeUser(0., 30.)

    # colors
    for i,tag in enumerate(tags):
        p[tag].SetLineColor(cols[i])

    # legend, cleanup
    canvas.makeLegend(lWidth=.2, pos='tr')
    canvas.legend.resizeHeight()

    canvas.cleanup('pdfs/HPD_PtDist_HTo2XTo{}_{}.pdf'.format(fs, SPStr(sp) if sp is not None else 'Global'))

for fs in ('2Mu2J',):
    for sp in [None] + SIGNALPOINTS:
        makePTCutPlot(fs, sp)
