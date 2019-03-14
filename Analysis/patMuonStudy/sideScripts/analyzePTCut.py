import ROOT as R
import DisplacedDimuons.Analysis.HistogramGetter as HG
from DisplacedDimuons.Common.Constants import SIGNALPOINTS

# see commit from Mar 5 2019 for the patch required to run studyPTCut.py

f = R.TFile.Open('roots/PTCutPlots_2Mu2J.root')

for sp in SIGNALPOINTS:
    h = HG.getHistogram(f, ('2Mu2J', sp), 'nMatches')
    maxMatched = max([h.GetBinContent(i) for i in xrange(1, h.GetNbinsX()+1)])
    ibin = h.GetMaximumBin()

    print '{:4d} {:3d} {:4d} : '.format(*sp),
    print 'the maximum {:5d} occurs @ pT > {:2d}'.format(int(maxMatched), int(ibin-1)),
    if ibin != 11:
        if int(maxMatched-h.GetBinContent(11)) != 0:
            print ', but 10 GeV would only cause a loss of {:2d} events ({:.2%})'.format(int(maxMatched - h.GetBinContent(11)), 1.-(h.GetBinContent(11)/maxMatched))
        else:
            print ' -- but 10 GeV is an equivalently optimal cut'
    else:
        print ' -- this is the optimal cut'
