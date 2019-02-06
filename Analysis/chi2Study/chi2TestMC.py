import ROOT as R
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
from DisplacedDimuons.Common.Utilities import SPStr
import DisplacedDimuons.Analysis.HistogramGetter as HG

R.gStyle.SetPalette(55)
R.gStyle.SetNumberContours(100)

key = 'Lxy2D-LxySig10'
#key = 'Lxy2D'

f = R.TFile.Open('roots/Chi2Plots_MC.root')

BGORDER = ('WJets', 'WW', 'WZ', 'ZZ', 'tW', 'tbarW', 'ttbar', 'QCD20toInf-ME', 'DY10to50', 'DY50toInf')
PC = HG.PLOTCONFIG
h = HG.getHistogram(f, BGORDER[0], key).Clone()
h.Scale(PC[BGORDER[0]]['WEIGHT'])
for ref in BGORDER[1:]:
    thisH = HG.getHistogram(f, ref, key).Clone()
    thisH.Scale(PC[ref]['WEIGHT'])
    h.Add(thisH)

h.Rebin2D(10, 10)
#h.GetXaxis().SetRangeUser(0., 3.5)
#h.GetYaxis().SetRangeUser(0., 40.)
h.Draw('colz')
#raw_input()

key = 'Lxy2D'
h2 = HG.getHistogram(f, BGORDER[0], key).Clone()
h2.Scale(PC[BGORDER[0]]['WEIGHT'])
for ref in BGORDER[1:]:
    thisH = HG.getHistogram(f, ref, key).Clone()
    thisH.Scale(PC[ref]['WEIGHT'])
    h2.Add(thisH)
h2.Rebin2D(10, 10)
