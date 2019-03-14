import ROOT as R
import DisplacedDimuons.Analysis.HistogramGetter as HG
from DisplacedDimuons.Common.Constants import SIGNALPOINTS

FILE = R.TFile.Open('roots/PATMuonStudyPlots_Trig_Combined_BS8_2Mu2J.root')
fs = '2Mu2J'

# stripped copy of the function in makeSummaryPlots for looking at individual fits
if False:
    for sp in SIGNALPOINTS:
        print sp

        h = HG.getHistogram(FILE, (fs, sp), 'PAT-LxyRes')
        func = R.TF1('f', 'gaus', -.01, .01)
        h.Fit('f', 'R')
        h.Draw()
        func.Draw("same")
        raw_input()

        h = HG.getHistogram(FILE, (fs, sp), 'DSA-LxyRes')
        func = R.TF1('f', 'gaus', -15., 15.)
        h.Fit('f', 'R')
        h.Draw()
        func.Draw("same")
        raw_input()

# stripped copy of the function in makePATPlots for looking at individual fits
if False:
    recoType = 'PAT'

    key = recoType + '-LxyResVSgenLxy'
    HISTS = HG.getAddedSignalHistograms(FILE, fs, (key,))

    upperEdge = 35
    for ibin in xrange(1,upperEdge+1):
        h = HISTS[key].ProjectionY('h'+str(ibin), ibin, ibin)
        #lims = .01
        lims = 5. if recoType == 'DSA' else .05
        if recoType == 'PAT' and ibin > 10:
            lims = lims/5.
        func = R.TF1('f', 'gaus', -lims, lims)
        h.Fit('f', 'R')
        print ibin
        h.Draw()
        func.Draw("same")
        raw_input()

