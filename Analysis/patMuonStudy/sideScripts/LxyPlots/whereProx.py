import ROOT as R
import DisplacedDimuons.Analysis.HistogramGetter as HG
import DisplacedDimuons.Analysis.Plotter as Plotter

#fOld = R.TFile.Open('roots/ZephyrPlots_Trig_Combined_NS_NH_FPTE_HLT_REP_PQ1_PT_PC_LXYE_MASS_CHI2_HTo2XTo2Mu2J.root')
#fNew = R.TFile.Open('roots/ZephyrPlots_Trig_Combined_NS_NH_FPTE_HLT_REP_PQ1_PT_PC_LXYE_MASS_CHI2_DSAPROXMATCH_HTo2XTo2Mu2J.root')

#fOld = R.TFile.Open('roots/ZephyrPlots_Trig_Combined_NS_NH_FPTE_HLT_REP_PQ1_PT_PC_LXYE_MASS_CHI2_DSAPROXMATCH_HTo2XTo2Mu2J.root')
#fNew = R.TFile.Open('roots/ZephyrPlots_Trig_Combined_NS_NH_FPTE_HLT_REP_PQ1_PT_PC_LXYE_MASS_CHI2_DPT_HTo2XTo2Mu2J.root')

fOld = R.TFile.Open('roots/ZephyrPlots_Trig_Combined_NS_NH_FPTE_HLT_REP_PT_PC_LXYE_MASS_CHI2_VTX_COSA_SFPTE_HTo2XTo2Mu2J.root')
fNew = R.TFile.Open('roots/ZephyrPlots_Trig_Combined_NS_NH_FPTE_HLT_REP_PT_PC_LXYE_MASS_CHI2_VTX_COSA_SFPTE_PROXTHRESH_HTo2XTo2Mu2J.root')

def deleteHistogram(HIST):
    R.gROOT.ProcessLine('delete gROOT->FindObject("'+HIST.GetName()+'")')

hOld = HG.getAddedSignalHistograms(fOld, '2Mu2J', 'GEN-Lxy-DSA')
g = hOld['GEN-Lxy-DSA'].Clone()
g.SetName('new')
deleteHistogram(hOld['GEN-Lxy-DSA'])

HybOld = HG.getAddedSignalHistograms(fOld, '2Mu2J', 'GEN-Lxy-HYB')
g.Add(HybOld['GEN-Lxy-HYB'])
deleteHistogram(HybOld['GEN-Lxy-HYB'])

hNew = HG.getAddedSignalHistograms(fNew, '2Mu2J', 'GEN-Lxy-DSA')
h = hNew['GEN-Lxy-DSA'].Clone()
h.SetName('old')
deleteHistogram(hNew['GEN-Lxy-DSA'])

HybNew = HG.getAddedSignalHistograms(fNew, '2Mu2J', 'GEN-Lxy-HYB')
h.Add(HybNew['GEN-Lxy-HYB'])
deleteHistogram(HybNew['GEN-Lxy-HYB'])

h.Rebin(40)
g.Rebin(40)

#h.Divide(g)
#p = Plotter.Plot(h, '', '', 'hist p')

x = R.TGraphAsymmErrors(h, g, 'cp')
p = Plotter.Plot(x, '', '', 'p')

c = Plotter.Canvas(lumi='DSA + HYB 2Mu Signal')
c.addMainPlot(p)
p.setColor(R.kBlue, which='LM')
p.GetXaxis().SetRangeUser(0., 350.)
p.SetMinimum(.95)
p.SetMaximum(1.01)
#p.setTitles(X='gen L_{xy} [cm]', Y='After DSA Prox Match / Before DSA Prox Match')
p.setTitles(X='gen L_{xy} [cm]', Y='DSA Prox Match With / Without Tracker Muons')
c.cleanup('DSAProxLxy.pdf')
