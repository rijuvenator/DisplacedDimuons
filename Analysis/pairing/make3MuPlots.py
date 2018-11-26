import re
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
from DisplacedDimuons.Common.Utilities import SPStr, SPLumiStr
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
import DisplacedDimuons.Analysis.HistogramGetter as HistogramGetter
import DisplacedDimuons.Analysis.PlotterParser as PlotterParser

ARGS = PlotterParser.PARSER.parse_args()
f = R.TFile.Open('roots/Main/3MuPlots_Trig{}_HTo2XTo4Mu.root'.format(ARGS.CUTSTRING))

QUANTITIES = ('GLxy', 'RLxy')

def makeEffPlot(quantity, criteria, fs, sp=None):
    tags = (quantity+'_MSD', quantity+'_LCD')

    effTag = quantity+'_LCD'
    effCol = R.kBlue
    effLeg = ''

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
    p[effTag] = Plotter.Plot(h[effTag], effLeg, 'l', 'px')

    # canvas, plots, min max
    canvas = Plotter.Canvas(lumi=SPLumiStr(fs, sp) if sp is not None else fs)
    canvas.addMainPlot(p[effTag])
    canvas.setMaximum()
    canvas.firstPlot.SetMinimum(0)

    # set titles
    canvas.firstPlot.setTitles(X=clones[tags[0]].GetXaxis().GetTitle(), Y='Efficiency')

    # colors
    p[effTag] = effCol

    # legend, cleanup
    canvas.makeLegend(lWidth=.2, pos='tr')
    canvas.legend.resizeHeight()

    canvas.cleanup('pdfs/3Mu_{}Eff_{}{}_HTo2XTo{}_{}.pdf'.format(quantity, criteria, ARGS.CUTSTRING, fs, SPStr(sp) if sp is not None else 'Global'))

for fs in ('4Mu',):
    #for sp in [None] + SIGNALPOINTS:
    for sp in [None]:
        for quantity in QUANTITIES:
            for criteria in CRITERIA:
                makeDistPlot(quantity, criteria, fs, sp)
                makeEffPlot(quantity, criteria, fs, sp)
