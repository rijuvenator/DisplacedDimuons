import re
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
from DisplacedDimuons.Common.Utilities import SPStr, SPLumiStr
import HistogramGetter

TRIGGER = False

# get histograms
HISTS = HistogramGetter.getHistograms('../analyzers/roots/Main/SignalRecoEffPlots.root')
f = R.TFile.Open('../analyzers/roots/Main/SignalRecoEffPlots.root')

# make overlaid plots that combine all signal points
def makeEffPlots(quantity, fs, SP=None):
    HKeys = {
        'DSA_Eff'       : 'DSA_{}Eff'      ,
        'RSA_Eff'       : 'RSA_{}Eff'      ,
        'REF_Eff'       : 'REF_{}Eff'      ,
        'Den'           : '{}Den'          ,
        'Extra'         : '{}Extra'        ,
        'DSA_ChargeEff' : 'DSA_{}ChargeEff',
        'RSA_ChargeEff' : 'RSA_{}ChargeEff',
        'REF_ChargeEff' : 'REF_{}ChargeEff',
        'DSA_ChargeDen' : 'DSA_{}ChargeDen',
        'RSA_ChargeDen' : 'RSA_{}ChargeDen',
        'REF_ChargeDen' : 'REF_{}ChargeDen',
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
        if quantity != 'dR':
            h[key].Rebin(10)
        else:
            h[key].Rebin(5)

# Extra is commented out, same with FIRST SECOND
# so they don't appear on SRE plots by default now

    NumDens = (
        ('DSA_Eff'      , 'Den'          , 'DSA'       , R.kBlue   ),
        ('RSA_Eff'      , 'Den'          , 'RSA'       , R.kRed    ),
        ('REF_Eff'      , 'Den'          , 'REF'       , R.kGreen  ),
#       ('Extra'        , 'Den'          , 'Extra'     , R.kMagenta),
        ('DSA_ChargeEff', 'DSA_ChargeDen', 'DSA:Charge', R.kBlue   ),
        ('RSA_ChargeEff', 'RSA_ChargeDen', 'RSA:Charge', R.kRed    ),
        ('REF_ChargeEff', 'REF_ChargeDen', 'REF:Charge', R.kGreen  ),
    )

    for num, den, leg, col in NumDens:
        g[num] = R.TGraphAsymmErrors(h[num], h[den], 'cp')
        g[num].SetNameTitle('g_'+num, ';'+h[num].GetXaxis().GetTitle()+';Reconstruction Efficiency')
        p[num] = Plotter.Plot(g[num], leg, 'elp', 'pe')

#   FIRST  = (0, 3)
#   SECOND = (3, 5)
#   FIRST  = (0, 2)
#   SECOND = (2, 4)
    FIRST  = (0, 3)
    SECOND = (3, 6)
    CHARGE = ''
    for SECTION in (FIRST, SECOND):
        canvas = Plotter.Canvas(lumi = fs if SP is None else SPLumiStr(fs, *SP))
        for i in range(SECTION[0], SECTION[1]):
            key = NumDens[i][0]
            col = NumDens[i][3]
            canvas.addMainPlot(p[key])
            p[key].SetMarkerColor(col)
            p[key].SetLineColor(col)
        # aesthetic change
        if quantity == 'Lxy' or (quantity == 'd0' and CHARGE == ''):
            canvas.makeLegend(pos='bl')
        else:
            canvas.makeLegend(pos='br')
            canvas.legend.moveLegend(Y=0.25)
            canvas.legend.moveLegend(X=-.1)
        canvas.legend.resizeHeight()
        canvas.firstPlot.SetMinimum(0.)
        canvas.firstPlot.SetMaximum(1.)
        #RT.addBinWidth(canvas.firstPlot)
        # aesthetic change
        if quantity == 'dR':
            canvas.firstPlot.GetXaxis().SetRangeUser(0., 1.)
        canvas.cleanup('pdfs/SRE_{}{}Eff_{}HTo2XTo{}_{}.pdf'.format(quantity, CHARGE, 'Trig-' if TRIGGER else '', fs, 'Global' if SP is None else SPStr(SP)))
        CHARGE = 'Charge'

for quantity in ('pT', 'eta', 'phi', 'Lxy', 'd0', 'dR', 'dphi'):
    for fs in ('4Mu', '2Mu2J'):
        makeEffPlots(quantity, fs)
        for sp in SIGNALPOINTS:
            makeEffPlots(quantity, fs, sp)
