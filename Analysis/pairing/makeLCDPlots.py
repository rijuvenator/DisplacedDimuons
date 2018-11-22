import re
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
from DisplacedDimuons.Common.Utilities import SPStr, SPLumiStr
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
import DisplacedDimuons.Analysis.HistogramGetter as HistogramGetter
import DisplacedDimuons.Analysis.PlotterParser as PlotterParser

ARGS = PlotterParser.PARSER.parse_args()
f = R.TFile.Open('roots/LCDPlots_Trig{}_HTo2XTo4Mu.root'.format(ARGS.CUTSTRING))

def makeLxyPlot(fs, sp=None):
    # configy type stuff
    legs=('All', 'Matched', 'NotMatched')
    tags=['Lxy_'+tag for tag in legs]
    cols=(R.kBlack, R.kBlue, R.kRed)

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
    logy = True
    canvas = Plotter.Canvas(lumi=SPLumiStr(fs, sp) if sp is not None else fs, logy=logy)
    for tag in tags:
        canvas.addMainPlot(p[tag])
    canvas.setMaximum()
    if not logy:
        canvas.firstPlot.SetMinimum(0)
    else:
        canvas.firstPlot.SetMinimum(1.)
    canvas.firstPlot.GetXaxis().SetRangeUser(0., 330.)

    # colors
    for i,tag in enumerate(tags):
        p[tag].SetLineColor(cols[i])

    # legend, cleanup
    canvas.makeLegend(lWidth=.2, pos='tr')
    canvas.legend.resizeHeight()

    canvas.cleanup('pdfs/LCD_LxyDist{}_HTo2XTo{}_{}.pdf'.format(ARGS.CUTSTRING, fs, SPStr(sp) if sp is not None else 'Global'))

def makeEffPlot(fs, sp=None):
    # configy type stuff
    legs=('All', 'Matched', 'NotMatched')
    tags=['Lxy_'+tag for tag in legs]
    cols=(R.kBlack, R.kBlue, R.kRed)

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

    clones = {tag:h[tag].Clone() for tag in tags}
    for tag in tags[1:]:
        h[tag] = R.TGraphAsymmErrors(clones[tag], clones[tags[0]], 'cp')

    # make plots
    p = {}
    for i,tag in enumerate(tags):
        p[tag] = Plotter.Plot(h[tag], legs[i], 'l', 'px')

    # canvas, plots, min max
    canvas = Plotter.Canvas(lumi=SPLumiStr(fs, sp) if sp is not None else fs)
    for tag in tags:
        if 'All' in tag: continue
        canvas.addMainPlot(p[tag])
    canvas.setMaximum()
    canvas.firstPlot.SetMinimum(0)
    canvas.firstPlot.GetXaxis().SetRangeUser(0., 330.)

    # colors
    for i,tag in enumerate(tags):
        p[tag].setColor(cols[i])

    # legend, cleanup
    canvas.makeLegend(lWidth=.2, pos='tr')
    canvas.legend.resizeHeight()

    canvas.cleanup('pdfs/LCD_LxyEff{}_HTo2XTo{}_{}.pdf'.format(ARGS.CUTSTRING, fs, SPStr(sp) if sp is not None else 'Global'))

for fs in ('4Mu',):
    for sp in [None] + SIGNALPOINTS:
        makeLxyPlot(fs, sp)
    makeEffPlot(fs, None)
