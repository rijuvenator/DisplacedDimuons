import ROOT as R
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
from DisplacedDimuons.Common.Utilities import SPStr
import DisplacedDimuons.Analysis.HistogramGetter as HG

R.gStyle.SetPalette(55)
R.gStyle.SetNumberContours(100)

FS = '2Mu2J'
key = 'Lxy2D-LxySig10'

f = R.TFile.Open('roots/Chi2Plots.root')

h = HG.getHistogram(f, ('2Mu2J', SIGNALPOINTS[0]), key).Clone()

for fs in (FS,):
    for sp in SIGNALPOINTS[1:]:
        h.Add(HG.getHistogram(f, ('2Mu2J', sp), key))

h.Rebin2D(10, 10)
#h.GetXaxis().SetRangeUser(0., 3.5)
#h.GetYaxis().SetRangeUser(0., 40.)
h.Draw('colz')
#raw_input()

HISTS = {}
for sp in SIGNALPOINTS:
    HISTS[sp] = HG.getHistogram(f, ('2Mu2J', sp), key)
