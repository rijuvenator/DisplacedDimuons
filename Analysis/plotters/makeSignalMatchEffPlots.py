import re
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
from DisplacedDimuons.Common.Utilities import SPStr

Patterns = {
    'HTo2XTo4Mu' : re.compile(r'(.*)_HTo2XTo4Mu_(\d{3,4})_(\d{2,3})_(\d{1,4})')
}

# get all histograms
HISTS = {}
f = R.TFile.Open('../analyzers/roots/SignalMatchEffPlots.root')
for hkey in [tkey.GetName() for tkey in f.GetListOfKeys()]:
    # hkey has the form KEY_HTo2XTo4Mu_mH_mX_cTau
    matches = Patterns['HTo2XTo4Mu'].match(hkey)
    key = matches.group(1)
    sp = tuple(map(int, matches.group(2, 3, 4)))
    if sp not in HISTS:
        HISTS[sp] = {}
    HISTS[sp][key] = f.Get(hkey)

# end of plot function boilerplate
def Cleanup(canvas, filename):
    canvas.finishCanvas()
    canvas.save(filename)
    canvas.deleteCanvas()

# make overlaid plots that combine all signal points
def makeEffPlots(quantity):
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
        HKeys[key] = (HKeys[key]+'_HTo2XTo4Mu').format(quantity) + '_{}'

    h = {}
    p = {}
    g = {}

    for i, sp in enumerate(SIGNALPOINTS):
        if i == 0:
            for key in HKeys:
                h[key] = f.Get(HKeys[key].format(SPStr(sp)))
                h[key].SetDirectory(0)
        else:
            for key in HKeys:
                h[key].Add(f.Get(HKeys[key].format(SPStr(sp))))

    for key in HKeys:
        h[key].Rebin(10)

    NumDens = (
        ('DSA_Eff'      , 'Den'          , 'DSA'       , R.kRed    ),
        ('RSA_Eff'      , 'Den'          , 'RSA'       , R.kBlue   ),
        ('Extra'        , 'Den'          , 'Extra'     , R.kMagenta),
        ('DSA_ChargeEff', 'DSA_ChargeDen', 'DSA:Charge', R.kRed    ),
        ('RSA_ChargeEff', 'RSA_ChargeDen', 'RSA:Charge', R.kBlue   ),
    )

    for num, den, leg, col in NumDens:
        g[num] = R.TGraphAsymmErrors(h[num], h[den], 'cp')
        g[num].SetNameTitle('g_'+num, ';'+h[num].GetXaxis().GetTitle()+';Match Efficiency')
        p[num] = Plotter.Plot(g[num], leg, 'elp', 'pe')

    FIRST  = (0, 3)
    SECOND = (3, 5)
    CHARGE = ''
    for SECTION in (FIRST, SECOND):
        canvas = Plotter.Canvas()
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
        Cleanup(canvas, 'pdfs/SME_{}{}Eff.pdf'.format(quantity, CHARGE))
        CHARGE = 'Charge'

for quantity in ('pT', 'eta', 'phi', 'Lxy'):
    makeEffPlots(quantity)
