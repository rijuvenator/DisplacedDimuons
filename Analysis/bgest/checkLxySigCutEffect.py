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
    fname = 'roots/Hists_{}.root'.format(i)
    if i == 6:
        fname = 'roots/Hists.root'

    f = R.TFile.Open(fname)
    h = f.Get('hDeltaPhiBig_Data').Clone()
    h.SetDirectory(0)
    HISTS[i] = h

    g =   f.Get('hDeltaPhiBig_DY50toInf').Clone()
    g.SetDirectory(0)
    MCHISTS[i] = g

colors = {
    1 : R.kRed,
    2 : R.kOrange+7,
    3 : R.kOrange,
    4 : R.kYellow,
    5 : R.kGreen,
    6 : R.kGreen+2,
    7 : R.kTeal+5,
    8 : R.kBlue,
    9 : R.kViolet+1,
    10: R.kMagenta
}

# these plots are square (for my thesis)
# remove the cWidth argument, remove the mode argument, and remove the scaleTitleOffsets call for rectangular

for label, var in zip(('Data', 'DY'), (HISTS, MCHISTS)):
    c = Plotter.Canvas(lumi='{}, 36.3 fb^{{-1}} (13 TeV)'.format('Data 2016' if label == 'Data' else 'Drell-Yan Simulation'), cWidth=600)
    plots = {i:Plotter.Plot(var[i], 'L_{{xy}}/#sigma_{{L_{{xy}}}} > {}'.format(i), 'l', 'hist') for i in var}
    for i in xrange(1,11):
        plots[i].Scale(1./plots[i].Integral(0, plots[i].GetNbinsX()+1))
        plots[i].Rebin(2)
        c.addMainPlot(plots[i])
        plots[i].setColor(colors[i])
    c.makeLegend(pos='tr', fontscale=.7, lWidth=.2)
    c.firstPlot.SetMaximum(0.05)
    c.firstPlot.SetMinimum(0.)
    c.firstPlot.setTitles(Y='Frequency', X='|#Delta#Phi|')
    c.legend.resizeHeight()
    c.firstPlot.scaleTitleOffsets(1.3, 'Y')
    c.cleanup('BGEST_EffectOfLxySigCut_{}.pdf'.format(label), mode='LUMI')
