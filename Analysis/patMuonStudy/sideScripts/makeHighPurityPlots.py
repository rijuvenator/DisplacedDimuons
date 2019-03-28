import ROOT as R
import DisplacedDimuons.Analysis.HistogramGetter as HG
import DisplacedDimuons.Analysis.Plotter as Plotter

f = R.TFile.Open('roots/HPPlots_Trig_Combined_NS_NH_FPTE_HLT_REP_PT_PC_LXYE_MASS_2Mu2J.root')
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
    c.cleanup('pdfs/HP_2Mu2J_'+key+'HPFrac.pdf')

f = R.TFile.Open('roots/HPPlots_Combined_NS_NH_FPTE_HLT_REP_PT_PC_LXYE_MASS_MC.root')
h, pc = HG.getBackgroundHistograms(f, ('pT', 'pT-HP'), stack=False, rebin=5)

for key in ('stack', 'DY50toInf'):
    g = R.TGraphAsymmErrors(h['pT-HP'][key], h['pT'][key], 'cp')
    p = Plotter.Plot(g, '', '', 'pe')
    c = Plotter.Canvas(lumi=key.title() if key == 'stack' else key)
    c.addMainPlot(p)
    p.setTitles(X='pre-refit PAT muon p_{T} [GeV]', Y='High purity fraction')
    p.setColor(R.kBlue, which='LM')
    c.cleanup('pdfs/HP_MC_'+key+'_HPFrac.pdf')
