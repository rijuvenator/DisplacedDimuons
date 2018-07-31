import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
from DisplacedDimuons.Common.Utilities import SPStr
import HistogramGetter

TRIGGER = False

# get histograms
HISTS = HistogramGetter.getHistograms('../analyzers/roots/Main/GenPlots.root')
f = R.TFile.Open('../analyzers/roots/Main/GenPlots.root')

# make plots using Plotter class per signal point
def makePerSignalPlots(fs):
    for sp in SIGNALPOINTS:
        for key in HISTS[(fs, sp)]:
            h = HISTS[(fs, sp)][key]
            RT.addFlows(h)
            p = Plotter.Plot(h, '', 'p', 'hist')
            canvas = Plotter.Canvas(lumi='{} ({} GeV, {} GeV, {} mm)'.format(fs, *sp))
            canvas.addMainPlot(p)
            p.SetLineColor(R.kBlue)
            RT.addBinWidth(p)
            pave = canvas.makeStatsBox(p, color=R.kBlue)
            canvas.cleanup('pdfs/Gen_{}_{}HTo2XTo{}_{}.pdf'.format(key, 'Trig-' if TRIGGER else '', fs, SPStr(sp)))

for fs in ('4Mu', '2Mu2J'):
    makePerSignalPlots(fs)
