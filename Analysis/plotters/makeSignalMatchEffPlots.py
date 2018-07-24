import re
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
from DisplacedDimuons.Common.Utilities import SPStr
import HistogramGetter

# get histograms
HISTS = HistogramGetter.getHistograms('../analyzers/roots/Main/SignalMatchEffPlots.root')
f = R.TFile.Open('../analyzers/roots/Main/SignalMatchEffPlots.root')

# make overlaid plots that combine all signal points
def makeEffPlots(quantity, fs, SP=None):
    HKeys = {
        'DSA_Eff'       : 'DSA_{}Eff'      ,
        'RSA_Eff'       : 'RSA_{}Eff'      ,
        'Den'           : '{}Den'          ,
        'Extra'         : '{}Extra'        ,
        'DSA_ChargeEff' : 'DSA_{}ChargeEff',
        'RSA_ChargeEff' : 'RSA_{}ChargeEff',
        'DSA_ChargeDen' : 'DSA_{}ChargeDen',
        'RSA_ChargeDen' : 'RSA_{}ChargeDen',
    }
    for key in HKeys:
        HKeys[key] = HKeys[key].format(quantity)

    h = {}
    p = {}
    g = {}

    if SP is None:
        for i, sp in enumerate(SIGNALPOINTS):
            if i == 0:
                for key in HKeys:
                    h[key] = HISTS[(fs, sp)][HKeys[key]].Clone()
                    h[key].SetDirectory(0)
            else:
                for key in HKeys:
                    h[key].Add(HISTS[(fs, sp)][HKeys[key]])
    else:
        sp = SP
        for key in HKeys:
            h[key] = HISTS[(fs, sp)][HKeys[key]].Clone()
            h[key].SetDirectory(0)

    for key in HKeys:
        RT.addFlows(h[key])
        h[key].Rebin(10)

    NumDens = (
        ('DSA_Eff'      , 'Den'          , 'DSA'       , R.kBlue   ),
        ('RSA_Eff'      , 'Den'          , 'RSA'       , R.kRed    ),
        ('Extra'        , 'Den'          , 'Extra'     , R.kMagenta),
        ('DSA_ChargeEff', 'DSA_ChargeDen', 'DSA:Charge', R.kBlue   ),
        ('RSA_ChargeEff', 'RSA_ChargeDen', 'RSA:Charge', R.kRed    ),
    )

    for num, den, leg, col in NumDens:
        g[num] = R.TGraphAsymmErrors(h[num], h[den], 'cp')
        g[num].SetNameTitle('g_'+num, ';'+h[num].GetXaxis().GetTitle()+';Match Efficiency')
        p[num] = Plotter.Plot(g[num], leg, 'elp', 'pe')

    FIRST  = (0, 3)
    SECOND = (3, 5)
    CHARGE = ''
    for SECTION in (FIRST, SECOND):
        canvas = Plotter.Canvas(lumi = fs if SP is None else '{} ({} GeV, {} GeV, {} mm)'.format(fs, *SP))
        for i in range(SECTION[0], SECTION[1]):
            key = NumDens[i][0]
            col = NumDens[i][3]
            canvas.addMainPlot(p[key])
            p[key].SetMarkerColor(col)
            p[key].SetLineColor(col)
        canvas.makeLegend(pos='bl')
        canvas.legend.moveLegend(Y=0.25)
        canvas.legend.resizeHeight()
        canvas.firstPlot.SetMinimum(0.)
        canvas.firstPlot.SetMaximum(1.)
        RT.addBinWidth(canvas.firstPlot)
        canvas.cleanup('pdfs/SME_{}{}Eff_HTo2XTo{}_{}.pdf'.format(quantity, CHARGE, fs, 'Global' if SP is None else SPStr(SP)))
        CHARGE = 'Charge'

for quantity in ('pT', 'eta', 'phi', 'Lxy', 'd0'):
    for fs in ('4Mu', '2Mu2J'):
        makeEffPlots(quantity, fs)
        for sp in SIGNALPOINTS:
            makeEffPlots(quantity, fs, sp)
