import ROOT as R
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
import DisplacedDimuons.Analysis.HistogramGetter as HG
import argparse

PARSER = argparse.ArgumentParser()
PARSER.add_argument('--quantity', dest='QUANTITY', default='vtxChi2')
#PARSER.add_argument('--file'    , dest='FILE'    , default='9')
PARSER.add_argument('--cut'     , dest='CUT'     , default=50., type=float)
ARGS = PARSER.parse_args()

f = R.TFile.Open('roots/ZephyrPlots_Trig_Combined_BS9_2Mu2J.root')

for sp in SIGNALPOINTS:
    for i, key in enumerate(('DSA', 'PAT', 'HYB')):
        if i == 0:
            h = HG.getHistogram(f, ('2Mu2J', sp), key+'-'+ARGS.QUANTITY)
        else:
            h.Add(HG.getHistogram(f, ('2Mu2J', sp), key+'-'+ARGS.QUANTITY))
    c = h.GetCumulative()
    ibin = c.FindBin(float(ARGS.CUT))
    print '{:4d} {:3d} {:4d} {:10.2f} {:5.0f} {:5.2f} {:5.2f}'.format(
        sp[0], sp[1], sp[2],
        h.GetMean(),
        h.GetBinContent(h.GetNbinsX()+1),
        h.GetBinContent(h.GetNbinsX()+1)/h.Integral(0, h.GetNbinsX()+1)*100.,
        100.-c.GetBinContent(ibin)      /h.Integral(0, h.GetNbinsX()+1)*100.
    )

