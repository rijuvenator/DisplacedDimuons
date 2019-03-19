import ROOT as R
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
import DisplacedDimuons.Analysis.HistogramGetter as HG
import argparse

PARSER = argparse.ArgumentParser()
PARSER.add_argument('--quantity' , dest='QUANTITY' , default='vtxChi2')
PARSER.add_argument('--cutstring', dest='CUTSTRING', default='Combined_NS_NH_FPTE_HLT_REP_PT_PC_LXYE_M')
PARSER.add_argument('--cut'      , dest='CUT'      , default=50., type=float)
PARSER.add_argument('--rtypes'   , dest='RTYPES'   , default='DPH')
ARGS = PARSER.parse_args()

f = R.TFile.Open('roots/ZephyrPlots_Trig_{}_HTo2XTo2Mu2J.root'.format(ARGS.CUTSTRING))

RTYPES = []
if 'D' in ARGS.RTYPES: RTYPES.append('DSA')
if 'P' in ARGS.RTYPES: RTYPES.append('PAT')
if 'H' in ARGS.RTYPES: RTYPES.append('HYB')

print '{:4s} {:3s} {:4s} {:>10s} {:>6s} {:>6s} {:>6s}'.format('mH', 'mX', 'cTau', 'Mean', 'OFlow', 'OFlow%', '%>{}'.format(ARGS.CUT))
for sp in SIGNALPOINTS:
    for i, key in enumerate(RTYPES):
        if i == 0:
            h = HG.getHistogram(f, ('2Mu2J', sp), key+'-'+ARGS.QUANTITY)
        else:
            h.Add(HG.getHistogram(f, ('2Mu2J', sp), key+'-'+ARGS.QUANTITY))
    c = h.GetCumulative()
    ibin = c.FindBin(float(ARGS.CUT))
    print '{:4d} {:3d} {:4d} {:10.2f} {:6.0f} {:6.2f} {:6.2f}'.format(
        sp[0], sp[1], sp[2],
        h.GetMean(),
        h.GetBinContent(h.GetNbinsX()+1),
        h.GetBinContent(h.GetNbinsX()+1)/h.Integral(0, h.GetNbinsX()+1)*100.,
        100.-c.GetBinContent(ibin)      /h.Integral(0, h.GetNbinsX()+1)*100.
    )

