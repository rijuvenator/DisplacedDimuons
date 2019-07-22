import ROOT as R
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.HistogramGetter as HG
import DisplacedDimuons.Analysis.RootTools as RT
import itertools

FILES = {
    'Signal' : R.TFile.Open('roots/SegMatchPlots_2Mu2J.root'),
    'Data'   : R.TFile.Open('roots/SegMatchPlots_DATA.root'),
}

def makePlot(mtype, vtype, quantity, which):
    hkey = '{}_{}_{}'.format(mtype, vtype, quantity)
    if which == 'Signal':
        HISTS = HG.getAddedSignalHistograms(FILES['Signal'], '2Mu2J', hkey)
        h = HISTS[hkey]
    elif which == 'Data':
        HISTS, PConfig = HG.getDataHistograms(FILES['Data'], hkey, addFlows=False)
        h = HISTS[hkey]['data']
    p = Plotter.Plot(h, '', '', 'hist')
    c = Plotter.Canvas()
    c.addMainPlot(p)
    p.setColor(R.kBlue)
    if hkey == 'Prox_PD_deltaR' or hkey == 'Prox_PP_deltaR':
        s = 0
        print hkey, which
        for ibin in xrange(1,p.GetNbinsX()+1):
            s += p.GetBinContent(ibin)
            print p.GetXaxis().GetBinLowEdge(ibin), p.GetBinContent(ibin), s
    s = c.makeStatsBox(p, R.kBlue)
    c.cleanup(hkey+'_'+which+'.pdf')

for mtype, vtype, quantity, which in itertools.product(('Prox', 'Seg'), ('PD', 'PP'), ('deltaR', 'fSeg'), ('Signal', 'Data')):
    makePlot(mtype, vtype, quantity, which)
    if which == 'Signal':
        makePlot(mtype, vtype, quantity+'_Matched', which)
