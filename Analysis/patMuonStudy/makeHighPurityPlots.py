import ROOT as R
import DisplacedDimuons.Analysis.HistogramGetter as HG
import DisplacedDimuons.Analysis.Plotter as Plotter

f = R.TFile.Open('roots/HPPlots_2Mu2J.root')
h = HG.getAddedSignalHistograms(f, '2Mu2J', ('pT', 'GM-pT', 'pT-HP', 'GM-pT-HP'))

for key in ('', 'GM-'):
    h[key+'pT-HP'].Rebin(5)
    h[key+'pT'   ].Rebin(5)
    g = R.TGraphAsymmErrors(h[key+'pT-HP'], h[key+'pT'], 'cp')
    p = Plotter.Plot(g, '', '', 'pe')
    c = Plotter.Canvas()
    c.addMainPlot(p)
    p.setTitles(X='pre-refit PAT muon p_{T} [GeV]', Y='High purity fraction')
    p.setColor(R.kBlue, which='LM')
    c.cleanup('pdfs/HP_'+key+'HPFrac.pdf')
