import ROOT as R
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
import DisplacedDimuons.Analysis.HistogramGetter as HG

f = R.TFile.Open('roots/PATMuonStudyPlots_Trig_Combined_BS8_2Mu2J.root')

for sp in SIGNALPOINTS:
    h = HG.getHistogram(f, ('2Mu2J', sp), 'PAT-vtxChi2')
    c = h.GetCumulative()
    print '{:4d} {:3d} {:4d} {:10.2f} {:5.0f} {:5.2f} {:5.2f}'.format(sp[0], sp[1], sp[2], h.GetMean(), h.GetBinContent(h.GetNbinsX()+1), h.GetBinContent(h.GetNbinsX()+1)/h.Integral(0, h.GetNbinsX()+1)*100., 100.-c.GetBinContent(101)/h.Integral(0, h.GetNbinsX()+1)*100.)

