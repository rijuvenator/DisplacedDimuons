import ROOT as R
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.HistogramGetter as HG
import DisplacedDimuons.Analysis.RootTools as RT
import itertools

FILES = {
    'Signal' : R.TFile.Open('roots/SegMatchPlots_2Mu2J_Lxy.root'),
    'Data'   : R.TFile.Open('roots/SegMatchPlots_DATA.root'),
}

TAGS = {
        '00':{'leg':'#DeltaR < 0.00', 'col':R.kBlack},
        '05':{'leg':'#DeltaR < 0.05', 'col':R.kRed  },
        '10':{'leg':'#DeltaR < 0.10', 'col':R.kRed+1},
        '15':{'leg':'#DeltaR < 0.15', 'col':R.kRed+2},
}
def makeLxyPlot():
    hkeys = ['Lxy_{}'.format(tag) for tag in TAGS]
    HISTS = HG.getAddedSignalHistograms(FILES['Signal'], '2Mu2J', hkeys)

    for key in hkeys:
        HISTS[key].Rebin(10)

    for tag in TAGS:
        zz = 'Lxy_{}'.format(tag)
        print zz, HISTS[zz].Integral(HISTS[zz].GetXaxis().FindBin(100.), HISTS[zz].GetNbinsX()+1), HISTS['Lxy_00'].Integral(HISTS['Lxy_00'].GetXaxis().FindBin(100.), HISTS['Lxy_00'].GetNbinsX()+1)

    g = {}
    for tag in TAGS:
        #g[tag] = R.TGraphAsymmErrors(HISTS['Lxy_{}'.format(tag)], HISTS['Lxy_00'], 'cp')
        g[tag] = HISTS['Lxy_{}'.format(tag)].Clone()
        g[tag].Divide(HISTS['Lxy_00'])

    #p = {tag:Plotter.Plot(g[tag], TAGS[tag]['leg'], 'lp', 'p') for tag in TAGS}
    p = {tag:Plotter.Plot(g[tag], TAGS[tag]['leg'], 'lp', 'hist p') for tag in TAGS}

    c = Plotter.Canvas()
    for tag in ('00', '05', '10', '15'):
        c.addMainPlot(p[tag])
        p[tag].setColor(TAGS[tag]['col'])

    c.makeLegend(lWidth=0.2, pos='bl')

    c.firstPlot.setTitles(X='', Y='', copy=HISTS[hkeys[0]])
    c.firstPlot.SetMinimum(0.8)
    c.firstPlot.SetMaximum(1.01)

    c.firstPlot.GetXaxis().SetRangeUser(0., 400.)

    c.cleanup('Lxy_deltaR_PD.pdf')

makeLxyPlot()
