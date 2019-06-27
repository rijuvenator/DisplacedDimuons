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
        '1' :{'leg':'f_{Seg} = 1'     , 'col':R.kBlack},
        '34':{'leg':'f_{Seg} #geq 3/4', 'col':R.kRed  },
        '23':{'leg':'f_{Seg} #geq 2/3', 'col':R.kRed+1},
        '12':{'leg':'f_{Seg} #geq 1/2', 'col':R.kRed+2},
}
def makeLxyPlot():
    hkeys = ['Lxy_{}'.format(tag) for tag in TAGS]
    HISTS = HG.getAddedSignalHistograms(FILES['Signal'], '2Mu2J', hkeys)

    for key in hkeys:
        HISTS[key].Rebin(10)

    g = {}
    for tag in TAGS:
        g[tag] = R.TGraphAsymmErrors(HISTS['Lxy_{}'.format(tag)], HISTS['Lxy_1'], 'cp')

    p = {tag:Plotter.Plot(g[tag], TAGS[tag]['leg'], 'lp', 'p') for tag in TAGS}

    c = Plotter.Canvas()
    for tag in ('1', '34', '23', '12'):
        c.addMainPlot(p[tag])
        p[tag].setColor(TAGS[tag]['col'])

    c.makeLegend(lWidth=0.2, pos='bl')

    c.firstPlot.setTitles(X='', Y='', copy=HISTS[hkeys[0]])
    c.firstPlot.SetMinimum(0.8)
    c.firstPlot.SetMaximum(1.01)

    c.cleanup('Lxy_deltaR.pdf')

makeLxyPlot()
