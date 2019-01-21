import ROOT as R
import DisplacedDimuons.Analysis.HistogramGetter as HistogramGetter
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
from DisplacedDimuons.Common.Utilities import SPStr

def printCum(h):
    nBins = h.GetNbinsX()
    c = h.GetCumulative()
    c.Scale(1./h.Integral(0, nBins+1))

    #print '{:5s} {:4d} {:3d} {:4d} {:4.1f} {:7.4f}'.format(fs, sp[0], sp[1], sp[2], c.GetXaxis().GetBinUpEdge(1000), c.GetBinContent(1000))

    for ibin in xrange(nBins+2):
        if 49.99 <= c.GetXaxis().GetBinUpEdge(ibin) <= 50.01:
            print '{:5s} {:4d} {:3d} {:4d} {:6.2%}'.format(fs, sp[0], sp[1], sp[2], 1-c.GetBinContent(ibin))
        #if c.GetBinContent(ibin) > .97:
        #    print '{:5s} {:4d} {:3d} {:4d} {:5.1f}'.format(fs, sp[0], sp[1], sp[2], c.GetXaxis().GetBinLowEdge(ibin))
        #    break
    #else:
    #    print '{:5s} {:4d} {:3d} {:4d} {:5.1f}'.format(fs, sp[0], sp[1], sp[2], 500.)

f = R.TFile.Open('../analyzers/roots/Chi2Plots.root')

hkey = 'Dim_vtxChi2_Matched'

for fs in ('2Mu2J', '4Mu'):
    for sp in SIGNALPOINTS:
        h = HistogramGetter.getHistogram(f, (fs, sp), hkey).Clone()
        printCum(h)

f.Close()

print ''

f = R.TFile.Open('../analyzers/roots/Main/DimuonPlots_NoPrompt_NS_NH_FPTE_PT_HLT_PC_LXYE_M_MCOnly.root')
hkey = 'Dim_vtxChi2'
BGORDER = ('WJets', 'WW', 'WZ', 'ZZ', 'tW', 'tbarW', 'ttbar', 'QCD20toInf-ME', 'DY10to50', 'DY50toInf')
PC = HistogramGetter.PLOTCONFIG
h = HistogramGetter.getHistogram(f, BGORDER[0], hkey).Clone()
h.Scale(PC[BGORDER[0]]['WEIGHT'])
for ref in BGORDER[1:]:
    thisH = HistogramGetter.getHistogram(f, ref, hkey).Clone()
    thisH.Scale(PC[ref]['WEIGHT'])
    h.Add(thisH)
print '---',
printCum(h)
