import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
from DisplacedDimuons.Common.Utilities import SPStr, SPLumiStr
import DisplacedDimuons.Analysis.AnalysisTools as AT
import DisplacedDimuons.Analysis.HistogramGetter as HG
import numpy as np

FIGURE_OF_MERIT = 'ZBi'
#FIGURE_OF_MERIT = 'ZPL'

FILES = {
    'Signal' : R.TFile.Open('roots/ReweightedPlots_Trig_HTo2XTo2Mu2J.root'),
    'Data'   : R.TFile.Open('roots/ReweightedPlots_IDPHI_DATA.root'),
}

SignalInfo = {
#   (1000, 350,   35) : {'sigmaBLimit' : 0.     , 'sumWeights' : {}},
    (1000, 350,  350) : {'sigmaBLimit' : 2.5e-3 , 'sumWeights' : {}},
    (1000, 350, 3500) : {'sigmaBLimit' : 3.5e-3 , 'sumWeights' : {}},
#   (1000, 150,   10) : {'sigmaBLimit' : 0.     , 'sumWeights' : {}},
    (1000, 150,  100) : {'sigmaBLimit' : 4.0e-3 , 'sumWeights' : {}},
    (1000, 150, 1000) : {'sigmaBLimit' : 1.7e-3 , 'sumWeights' : {}},
#   (1000,  50,    4) : {'sigmaBLimit' : 0.     , 'sumWeights' : {}},
    (1000,  50,   40) : {'sigmaBLimit' : 2.1e-2 , 'sumWeights' : {}},
    (1000,  50,  400) : {'sigmaBLimit' : 4.1e-3 , 'sumWeights' : {}},
#   (1000,  20,    2) : {'sigmaBLimit' : 0.     , 'sumWeights' : {}},
    (1000,  20,   20) : {'sigmaBLimit' : 1.0    , 'sumWeights' : {}},
    (1000,  20,  200) : {'sigmaBLimit' : 1.5e-1 , 'sumWeights' : {}},
#   ( 400, 150,   40) : {'sigmaBLimit' : 0.     , 'sumWeights' : {}},
    ( 400, 150,  400) : {'sigmaBLimit' : 2.7e-3 , 'sumWeights' : {}},
    ( 400, 150, 4000) : {'sigmaBLimit' : 4.4e-3 , 'sumWeights' : {}},
#   ( 400,  50,    8) : {'sigmaBLimit' : 0.     , 'sumWeights' : {}},
    ( 400,  50,   80) : {'sigmaBLimit' : 1.0e-2 , 'sumWeights' : {}},
    ( 400,  50,  800) : {'sigmaBLimit' : 2.7e-3 , 'sumWeights' : {}},
#   ( 400,  20,    4) : {'sigmaBLimit' : 0.     , 'sumWeights' : {}},
    ( 400,  20,   40) : {'sigmaBLimit' : 4.8e-2 , 'sumWeights' : {}},
    ( 400,  20,  400) : {'sigmaBLimit' : 9.6e-3 , 'sumWeights' : {}},
#   ( 200,  50,   20) : {'sigmaBLimit' : 0.     , 'sumWeights' : {}},
    ( 200,  50,  200) : {'sigmaBLimit' : 8.8e-3 , 'sumWeights' : {}},
    ( 200,  50, 2000) : {'sigmaBLimit' : 9.7e-3 , 'sumWeights' : {}},
#   ( 200,  20,    7) : {'sigmaBLimit' : 0.     , 'sumWeights' : {}},
    ( 200,  20,   70) : {'sigmaBLimit' : 4.3e-2 , 'sumWeights' : {}},
    ( 200,  20,  700) : {'sigmaBLimit' : 9.2e-3 , 'sumWeights' : {}},
#   ( 125,  50,   50) : {'sigmaBLimit' : 0.     , 'sumWeights' : {}},
    ( 125,  50,  500) : {'sigmaBLimit' : 2.7e-2 , 'sumWeights' : {}},
    ( 125,  50, 5000) : {'sigmaBLimit' : 6.8e-2 , 'sumWeights' : {}},
#   ( 125,  20,   13) : {'sigmaBLimit' : 0.     , 'sumWeights' : {}},
    ( 125,  20,  130) : {'sigmaBLimit' : 4.8e-2 , 'sumWeights' : {}},
    ( 125,  20, 1300) : {'sigmaBLimit' : 4.3e-2 , 'sumWeights' : {}},
}

# this is the result of catting the output files
# from the reweightedPlots jobs
# lines are of the format mH mX cTau ::: factor weight
f = open('SignalSumWeights.txt')
for line in f:
    cols = line.strip('\n').split()
    sp = tuple(map(int, cols[:3]))
    if sp not in SignalInfo: continue
    factor = int(cols[4])
    weight = float(cols[5])
    SignalInfo[sp]['sumWeights'][factor] = weight

def ScaleFactor(sp, factor):
    return SignalInfo[sp]['sigmaBLimit'] / SignalInfo[sp]['sumWeights'][factor] * HG.INTEGRATED_LUMINOSITY_2016

FACTORS = (1, 2, 5, 10)

CONFIG = {
    'LxySig' : {'forward':False, 'pretty':'dimuon L_{xy}/#sigma_{L_{xy}}'},
}

DATA = {}
for sp in SignalInfo:
    masses = (sp[0], sp[1])
    if masses in DATA: continue
    DATA[masses] = {quantity:{'x':[], 'y':[]} for quantity in CONFIG}

def fillData(fs, sp, quantity, factor):
    # get histograms
    s = HG.getHistogram(FILES['Signal'], (fs, sp), '{}_{}'.format(quantity, factor)).Clone()
    DHists, DPConfig = HG.getDataHistograms(FILES['Data'], '{}_1'.format(quantity), addFlows=False)
    b = DHists['{}_1'.format(quantity)]['data']

    if SignalInfo[sp]['sigmaBLimit'] == 0.: return

    n = s.Integral(0, s.GetNbinsX()+1)
    s.Scale(ScaleFactor(sp, factor))

    # get cumulatives
    sCum = s.GetCumulative(CONFIG[quantity]['forward'])
    bCum = b.GetCumulative(CONFIG[quantity]['forward'])

    # fill f.o.m. histogram, and keep track of max f.o.m. and cut value
    nBins = sCum.GetNbinsX()
    xAxis = sCum.GetXaxis()

    fom_max = 0.
    opt_cut = 0.
    opt_s   = 0.
    opt_b   = 0.

    for ibin in range(1,nBins+1):
        S = sCum.GetBinContent(ibin)
        B = bCum.GetBinContent(ibin)
        if not CONFIG[quantity]['forward']:
            S += s.GetBinContent(nBins+1)
            B += b.GetBinContent(nBins+1)
        ZBiVal = AT.ZBi(S+B, B, 1.)
        ZPLVal = AT.ZPL(S+B, B, 1.)
        cutVal = xAxis.GetBinUpEdge(ibin) if CONFIG[quantity]['forward'] else xAxis.GetBinLowEdge(ibin)

        val = ZBiVal if FIGURE_OF_MERIT == 'ZBi' else ZPLVal
        if val > fom_max:
            fom_max = val
            opt_cut = cutVal
            opt_s   = S
            opt_b   = B

    # for each (mH, mX) pair, store the xvalue: cTau (mm) / 10 -> cm, divided by factor
    # this will run for each sample point, meaning afterwards, the (mH, mX) x and y lists
    # will have len(factors) * 2 (maybe 3 if we put the small lifetimes in) points
    masses = (sp[0], sp[1])
    cTau = sp[-1]
    DATA[masses][quantity]['x'].append(cTau/10./factor)
    DATA[masses][quantity]['y'].append(opt_cut)

for fs in ('2Mu2J',):
    # sorting puts e.g. (1000, 150, 1000) after (1000, 150, 100)
    # Since the factors are ordered 1, 2, 5, 10,
    # reversing puts the points in the order (1000, 1..10) , (100, 1..10)
    # so that the points when connected with a line don't jump around
    for sp in reversed(sorted(SignalInfo.keys())):
        for quantity in CONFIG:
            for factor in FACTORS:
                fillData(fs, sp, quantity, factor)

# I can't get SetRangeUser to work for a TGraph on the Xaxis
# So my solution was to make a dummy plot with 2 points that
# have the X and Y range that I desired and let ROOT figure it out
# Then make the points white and then they don't show up on the plot :D
# Yes, I realize this is a terrible solution.
# ROOT is also terrible with TGraphs on a log x axis.
# If you can figure out how to fix it, please be my guest.
def makePlot(quantity, masses):
    dummyX, dummyY = np.array([.1, 1000.]), np.array([0., 25.])
    dummyG = R.TGraph(2, dummyX, dummyY)

    n = len(DATA[masses][quantity]['x'])
    x = np.array(DATA[masses][quantity]['x'])
    y = np.array(DATA[masses][quantity]['y'])

    g = R.TGraph(n, x, y)
    p = Plotter.Plot(g, '', '', 'pl')
    d = Plotter.Plot(dummyG, '', '', 'p')

    c = Plotter.Canvas(lumi='({} GeV, {} GeV)'.format(*masses))
    c.addMainPlot(d)
    c.addMainPlot(p)
    c.mainPad.SetLogx()

    p.setColor(R.kBlue, which='LM')
    d.setColor(R.kWhite, which='M')
    c.firstPlot.setTitles(X='c#tau [cm]', Y=CONFIG[quantity]['pretty']+' Cut Value')

    c.cleanup('RW_{}_{}_{}_{}.pdf'.format(quantity, masses[0], masses[1], FIGURE_OF_MERIT))

# technically, this is wasteful because it makes
# (mH, mX) plots twice: one for cTau and one for cTau/10
# I could keep track of which masses had been done with
# some list and skip if it had already been done
for fs in ('2Mu2J',):
    for sp in SignalInfo:
        masses = (sp[0], sp[1])
        for quantity in CONFIG:
            makePlot(quantity, masses)


