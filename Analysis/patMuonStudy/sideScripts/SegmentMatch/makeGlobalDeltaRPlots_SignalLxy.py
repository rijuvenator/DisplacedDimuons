import ROOT as R
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.HistogramGetter as HG
import DisplacedDimuons.Analysis.RootTools as RT
import itertools

FILES = {
    'Signal' : R.TFile.Open('roots/GlobalTestPlots_Trig_Signal.root'),
}

TAGS = ('before', 'after')

def makeLxyPlot():
    hkeys = ['Lxy_{}'.format(tag) for tag in TAGS]
    HISTS = HG.getAddedSignalHistograms(FILES['Signal'], '2Mu2J', hkeys)

    for key in hkeys:
        HISTS[key].Rebin(20)

    print HISTS['Lxy_before'].Integral(HISTS['Lxy_before'].GetXaxis().FindBin(100.), HISTS['Lxy_before'].GetNbinsX()+1), \
          HISTS['Lxy_after' ].Integral(HISTS['Lxy_after' ].GetXaxis().FindBin(100.), HISTS['Lxy_after' ].GetNbinsX()+1)

    g = {}
    g['plot'] = R.TGraphAsymmErrors(HISTS['Lxy_after'], HISTS['Lxy_before'], 'cp')

    p = {}
    p['plot'] = Plotter.Plot(g['plot'], '', '', 'p')

    #p = {tag:Plotter.Plot(g[tag], TAGS[tag]['leg'], 'lp', 'hist p') for tag in TAGS}

    c = Plotter.Canvas()
    c.addMainPlot(p['plot'])
    p['plot'].setColor(R.kBlue)

    c.firstPlot.setTitles(X='', Y='', copy=HISTS[hkeys[0]])
    c.firstPlot.SetMinimum(0.95)
    c.firstPlot.SetMaximum(1.01)

    c.firstPlot.GetXaxis().SetRangeUser(0., 400.)

    c.cleanup('Lxy_globalDeltaR.pdf')

makeLxyPlot()
