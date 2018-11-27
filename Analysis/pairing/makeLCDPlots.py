import re
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
from DisplacedDimuons.Common.Utilities import SPStr, SPLumiStr
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
import DisplacedDimuons.Analysis.HistogramGetter as HistogramGetter
import DisplacedDimuons.Analysis.PlotterParser as PlotterParser

ARGS = PlotterParser.PARSER.parse_args()
f = R.TFile.Open('roots/Main/LCDPlots_Trig{}_HTo2XTo4Mu.root'.format(ARGS.CUTSTRING))

#QUANTITIES = ('GLxy', 'GpT1', 'Gmass', 'RLxy', 'RpT1', 'Rmass')
QUANTITIES = ('GLxy', 'RLxy')
CRITERIA = []
for fillWhen in ('', '-4'):
    for oppCharge in ('', '-OC'):
        CRITERIA.append('Chi2'+oppCharge+fillWhen)
        for criteria in ('-LCD', '-C2S', '-AMD'):
            fullName = 'HPD'+oppCharge+criteria+fillWhen
            if fillWhen == '-4' or (fillWhen == '' and criteria != '-AMD'):
                CRITERIA.append(fullName)

def makeDistPlot(quantity, criteria, fs, sp=None):
    # configy type stuff
    legs = ('All', 'Matched', 'NotMatched')
    tags = [quantity+'_'+('All'+('-4' if '-4' in criteria else '') if 'All' in leg else criteria+'_'+leg) for leg in legs]
    cols = (R.kBlack, R.kBlue, R.kRed)

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
    if 'Lxy' in quantity:
        canvas.firstPlot.GetXaxis().SetRangeUser(0., 330.)

    # colors
    for i,tag in enumerate(tags):
        p[tag].SetLineColor(cols[i])

    # legend, cleanup
    canvas.makeLegend(lWidth=.2, pos='tr')
    canvas.legend.resizeHeight()

    canvas.cleanup('pdfs/LCD_{}Dist_{}{}_HTo2XTo{}_{}.pdf'.format(quantity, criteria, ARGS.CUTSTRING, fs, SPStr(sp) if sp is not None else 'Global'))

def makeEffPlot(quantity, criteria, fs, sp=None):
    # configy type stuff
    legs = ('All', 'Matched', 'NotMatched')
    tags = [quantity+'_'+('All'+('-4' if '-4' in criteria else '') if 'All' in leg else criteria+'_'+leg) for leg in legs]
    cols = (R.kBlack, R.kBlue, R.kRed)

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

    for tag in tags:
        h[tag].Rebin(5)

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
    if 'Lxy' in quantity:
        canvas.firstPlot.GetXaxis().SetRangeUser(0., 330.)

    # set titles
    canvas.firstPlot.setTitles(X=clones[tags[0]].GetXaxis().GetTitle(), Y='Efficiency')

    # colors
    for i,tag in enumerate(tags):
        p[tag].setColor(cols[i])

    # legend, cleanup
    canvas.makeLegend(lWidth=.2, pos='tr')
    canvas.legend.resizeHeight()

    if not (criteria in ('HPD-OC-C2S', 'HPD-C2S') and ARGS.CUTSTRING in ('', '_5GeV')):
        canvas.legend.moveLegend(Y=-.3)

    canvas.cleanup('pdfs/LCD_{}Eff_{}{}_HTo2XTo{}_{}.pdf'.format(quantity, criteria, ARGS.CUTSTRING, fs, SPStr(sp) if sp is not None else 'Global'))

for fs in ('4Mu',):
    for sp in [None] + SIGNALPOINTS:
        for quantity in QUANTITIES:
            for criteria in CRITERIA:
                makeDistPlot(quantity, criteria, fs, sp)
                makeEffPlot(quantity, criteria, fs, sp)
