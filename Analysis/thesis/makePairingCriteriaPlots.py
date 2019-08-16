import ROOT as R
import DisplacedDimuons.Analysis.HistogramGetter as HG
import DisplacedDimuons.Analysis.Plotter as Plotter
from DisplacedDimuons.Common.Constants import SIGNALPOINTS, SIGNALS
from DisplacedDimuons.Common.Utilities import SPStr
import DisplacedDimuons.Analysis.RootTools as RT
import DisplacedDimuons.Analysis.PlotterParser as PP
import itertools

PP.PARSER.add_argument('--square', dest='SQUARE', action='store_true')
ARGS = PP.PARSER.parse_args()

FILES = {
    '2Mu2J' : R.TFile.Open('roots/PairingCriteriaPlots_Trig_HTo2XTo2Mu2J.root'),
    '4Mu'   : R.TFile.Open('roots/PairingCriteriaPlots_Trig_HTo2XTo4Mu.root')
}

#######################################
##### PAIRING CRITERIA EFFICIENCY #####
#######################################

def makeEffPlot(fs, sp):
    if sp is None:
        hNum = HG.getAddedSignalHistograms(FILES[fs], fs, 'Lxy-Num')['Lxy-Num']
        hDen = HG.getAddedSignalHistograms(FILES[fs], fs, 'Lxy-Den')['Lxy-Den']
    else:
        hNum = HG.getHistogram(FILES[fs], (fs, sp), 'Lxy-Num').Clone()
        hDen = HG.getHistogram(FILES[fs], (fs, sp), 'Lxy-Den').Clone()

        hNumInt = hNum.Integral(hNum.GetXaxis().FindBin(65.), hNum.GetNbinsX()+1)
        hDenInt = hDen.Integral(hDen.GetXaxis().FindBin(65.), hDen.GetNbinsX()+1)

        #if sp == (sp[0], sp[1], SIGNALS[sp[0]][sp[1]][0]): return
        print '{:5s} {:4d} {:3d} {:4d} ::: {:5.0f} {:5.0f} {:7.2%}'.format(fs, sp[0], sp[1], sp[2], hNumInt, hDenInt, hNumInt/hDenInt if hDenInt != 0. else 0.)

        return

    hNum.Rebin(2)
    hDen.Rebin(2)

    g = R.TGraphAsymmErrors(hNum, hDen, 'cp')

    p = Plotter.Plot(g, '', '', 'p')

    prettyFS = '2#mu' if '2Mu' in fs else '4#mu'
    if sp is not None:
        lumi = 'H#rightarrow2X#rightarrow{} ({} GeV, {} GeV, {} mm)'.format(prettyFS, *sp)
    else:
        lumi = 'H#rightarrow2X#rightarrow{}, all samples combined'.format(prettyFS)
    c = Plotter.Canvas(lumi=lumi, cWidth=600 if ARGS.SQUARE else 800)

    c.addMainPlot(p)
    p.setColor(R.kBlue, which='LM')

    c.firstPlot.SetMinimum(0.)
    c.firstPlot.SetMaximum(1.)
    c.firstPlot.setTitles(X='', copy=hNum)
    c.firstPlot.setTitles(Y='Efficiency for pairing criteria to select correct dimuons')

    if ARGS.SQUARE:
        c.firstPlot.scaleTitleOffsets(1.1, 'X')
    c.cleanup('pdfs/PC_Lxy_{}_{}.pdf'.format(fs, 'Global' if sp is None else SPStr(sp)), mode='LUMI')

def makeMultipleEffPlot(fs, spList):
    hNum, hDen, g, p = {}, {}, {}, {}
    for sp in spList:
        hNum[sp] = HG.getHistogram(FILES[fs], (fs, sp), 'Lxy-Num').Clone()
        hDen[sp] = HG.getHistogram(FILES[fs], (fs, sp), 'Lxy-Den').Clone()

        hNum[sp].Rebin(10)
        hDen[sp].Rebin(10)

        g[sp] = R.TGraphAsymmErrors(hNum[sp], hDen[sp], 'cp')

        p[sp] = Plotter.Plot(g[sp], 'm_{{H}} = {} GeV, m_{{X}} = {} GeV, c#tau = {} mm'.format(*sp), 'lp', 'p')

    prettyFS = '2#mu' if '2Mu' in fs else '4#mu'
    lumi = 'H#rightarrow2X#rightarrow{}'.format(prettyFS)
    c = Plotter.Canvas(lumi=lumi, cWidth=600 if ARGS.SQUARE else 800)

    colors = (R.kRed, R.kAzure+7, R.kGreen+1)

    for col, sp in zip(colors, spList):
        c.addMainPlot(p[sp])
        p[sp].setColor(col, which='LMF')

    c.makeLegend(lWidth=.7, pos='br', fontscale=.9)
    c.legend.SetMargin(0.1)
    c.legend.resizeHeight()

    c.firstPlot.SetMinimum(0.5)
    c.firstPlot.SetMaximum(1. )
    c.firstPlot.setTitles(X='', copy=hNum[spList[0]])
    c.firstPlot.setTitles(Y='Efficiency for pairing criteria to select correct dimuons')

    if ARGS.SQUARE:
        c.firstPlot.scaleTitleOffsets(1.1, 'X')
        c.firstPlot.scaleTitleOffsets(1.2, 'Y')
    c.cleanup('pdfs/PC_Lxy_{}_Mul.pdf'.format(fs), mode='LUMI')

for fs in FILES:
    for sp in itertools.chain(SIGNALPOINTS, [None]):
        makeEffPlot(fs, sp)

    makeMultipleEffPlot(fs, [(400, 150, 4000), (125, 20, 1300), (1000, 20, 20)])
