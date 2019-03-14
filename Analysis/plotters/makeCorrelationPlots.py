import re
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
from DisplacedDimuons.Common.Utilities import SPStr, SPLumiStr
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
import DisplacedDimuons.Analysis.HistogramGetter as HistogramGetter
import DisplacedDimuons.Analysis.PlotterParser as PlotterParser

PlotterParser.PARSER.add_argument('--region', dest='REGION', default='Prompt')
ARGS = PlotterParser.PARSER.parse_args()

REGION    = ARGS.REGION
TRIGGER   = ARGS.TRIGGER
CUTSTRING = ARGS.CUTSTRING
MCONLY    = ARGS.MCONLY

# get histograms
fMC  = R.TFile.Open('../analyzers/roots/Main/CorrelationPlots_{}_NS_NH_FPTE_PT_HLT_PC_LXYE_M_MCOnly.root'.format(REGION))
fSig = R.TFile.Open('../analyzers/roots/Main/CorrelationPlots_Trig_{}_NS_NH_FPTE_PT_HLT_PC_LXYE_M_SignalOnly.root'.format(REGION))

# make stack plots
def makeStackPlots(hkey):
    BGORDER = ('WJets', 'WW', 'WZ', 'ZZ', 'tW', 'tbarW', 'ttbar', 'QCD20toInf-ME', 'DY10to50', 'DY50toInf')
    PC = HistogramGetter.PLOTCONFIG
    h = HistogramGetter.getHistogram(fMC, BGORDER[0], hkey).Clone()
    h.Scale(PC[BGORDER[0]]['WEIGHT'])
    #h.Rebin2D(10, 10)
    for ref in BGORDER[1:]:
        thisH = HistogramGetter.getHistogram(fMC, ref, hkey).Clone()
        thisH.Scale(PC[ref]['WEIGHT'])
        #thisH.Rebin2D(10, 10)
        h.Add(thisH)
    p = Plotter.Plot(h, '', '', 'colz')

    if 'd0Sig' not in hkey:
        h.GetXaxis().SetRangeUser(0., 50.)
    h.GetYaxis().SetRangeUser(0., 20./(2 if 'Err' in hkey else 1))

    canvas = Plotter.Canvas()
    canvas.mainPad.SetLogz(True)
    canvas.addMainPlot(p)
    canvas.scaleMargins(1.75, edges='R')
    canvas.scaleMargins(0.8, edges='L')
    canvas.cleanup('pdfs/COR_MC_{}_{}.pdf'.format(REGION, hkey))

# combine signal plots
def makeCombinedSignalPlots(fs, hkey):
    h = HistogramGetter.getHistogram(fSig, (fs, SIGNALPOINTS[0]), hkey).Clone()
    #h.Rebin2D(10, 10)
    for sp in SIGNALPOINTS[1:]:
        thisH = HistogramGetter.getHistogram(fSig, (fs, sp), hkey).Clone()
        #thisH.Rebin2D(10, 10)
        h.Add(thisH)
    p = Plotter.Plot(h, '', '', 'colz')

    if 'd0Sig' not in hkey:
        h.GetXaxis().SetRangeUser(0., 50.)
    h.GetYaxis().SetRangeUser(0., 20./(2 if 'Err' in hkey else 1))

    canvas = Plotter.Canvas()
    canvas.mainPad.SetLogz(True)
    canvas.addMainPlot(p)
    canvas.scaleMargins(1.75, edges='R')
    canvas.scaleMargins(0.8, edges='L')
    canvas.cleanup('pdfs/COR_{}_{}_{}.pdf'.format(fs, REGION, hkey))

for hkey in ('LxySigVSvtxChi2', 'LxyErrVSvtxChi2', 'LxySigVSd0Sig', 'LxyErrVSd0Sig'):
    makeStackPlots(hkey)
    for fs in ('2Mu2J', '4Mu'):
        makeCombinedSignalPlots(fs, hkey)
