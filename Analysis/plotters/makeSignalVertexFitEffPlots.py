import re
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
from DisplacedDimuons.Common.Utilities import SPStr
import HistogramGetter

# get histograms
HISTS = HistogramGetter.getHistograms('../analyzers/roots/SignalVertexFitEffPlots.root')
f = R.TFile.Open('../analyzers/roots/SignalVertexFitEffPlots.root')

# make overlaid plots that combine all signal points
def makeEffPlots(quantity, fs, SP=None):
    HKeys = {
        'Eff' : '{}Eff',
        'Den' : '{}Den',
    }
    for key in HKeys:
        HKeys[key] = HKeys[key].format(quantity)

    h = {}
    p = {}
    g = {}

    if SP is None:
        for i, sp in enumerate(SIGNALPOINTS):
            if i == 0:
                for key in HKeys:
                    h[key] = HISTS[(fs, sp)][HKeys[key]].Clone()
                    h[key].SetDirectory(0)
            else:
                for key in HKeys:
                    h[key].Add(HISTS[(fs, sp)][HKeys[key]])
    else:
        sp = SP
        for key in HKeys:
            h[key] = HISTS[(fs, sp)][HKeys[key]].Clone()
            h[key].SetDirectory(0)

    for key in HKeys:
        h[key].Rebin(10)

    g['Eff'] = R.TGraphAsymmErrors(h['Eff'], h['Den'], 'cp')
    g['Eff'].SetNameTitle('g_Eff', ';'+h['Eff'].GetXaxis().GetTitle()+';Vertex Fit Efficiency')
    p['Eff'] = Plotter.Plot(g['Eff'], '', 'elp', 'pe')

    canvas = Plotter.Canvas(lumi = fs if SP is None else '{} ({} GeV, {} GeV, {} mm)'.format(fs, *SP))
    canvas.addMainPlot(p['Eff'])
    p['Eff'].SetMarkerColor(R.kBlue)
    p['Eff'].SetLineColor(R.kBlue)
    canvas.firstPlot.SetMinimum(0.)
    canvas.firstPlot.SetMaximum(1.)
    canvas.cleanup('pdfs/SVFE_{}Eff_HTo2XTo{}_{}.pdf'.format(quantity, fs, 'Global' if SP is None else SPStr(SP)))

for quantity in ('pT', 'eta', 'phi', 'Lxy'):
    for fs in ('4Mu', '2Mu2J'):
        makeEffPlots(quantity, fs)
        for sp in SIGNALPOINTS:
            makeEffPlots(quantity, fs, sp)
