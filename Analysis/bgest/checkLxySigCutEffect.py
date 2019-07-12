import ROOT as R
import DisplacedDimuons.Analysis.HistogramGetter as HG
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT

# make a bunch of Hists.root with
# for i in {1..10}; do makeAsymmetryHists.py DaddyDSA.txt --cutoff $i & done
# then this will make the comparison plot across cuts

HISTS = {}
MCHISTS = {}

for i in xrange(1,11):
    fname = 'Hists_{}.root'.format(i)
    if i == 7:
        fname = 'Hists.root'

    f = R.TFile.Open(fname)
    h = f.Get('hDeltaPhiBig_Data').Clone()
    h.SetDirectory(0)
    HISTS[i] = h

    g =   f.Get('hDeltaPhiBig_DY50toInf').Clone()
    g.SetDirectory(0)
    MCHISTS[i] = g

for label, var in zip(('Data', 'DY'), (HISTS, MCHISTS)):
    c = Plotter.Canvas()
    plots = {i:Plotter.Plot(var[i], 'LxySig > {}'.format(i), 'l', 'hist') for i in var}
    for i in xrange(1,11):
        plots[i].Scale(1./plots[i].Integral(0, plots[i].GetNbinsX()+1))
        c.addMainPlot(plots[i])
        plots[i].setColor(i if i != 10 else 44)
    c.makeLegend(pos='tr', fontscale=.7, lWidth=.2)
    c.setMaximum()
    c.firstPlot.SetMinimum(0.)
    c.firstPlot.setTitles(Y='Frequency', X='|#Delta#Phi|')
    c.legend.resizeHeight()
    c.cleanup('EffectOfLxySigCut_{}.pdf'.format(label))
