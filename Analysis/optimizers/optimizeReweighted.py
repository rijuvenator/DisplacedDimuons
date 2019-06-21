import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
from DisplacedDimuons.Common.Utilities import SPStr, SPLumiStr
import DisplacedDimuons.Analysis.AnalysisTools as AT
import DisplacedDimuons.Analysis.HistogramGetter as HG
import numpy as np
from OptimizerTools import SignalInfo, ScaleFactor, calculateFOM

FIGURE_OF_MERIT = 'ZBi'
#FIGURE_OF_MERIT = 'ZPL'

PRETTY_LEG = {'ZBi':'Z_{Bi}', 'ZPL':'Z_{PL}'}[FIGURE_OF_MERIT]

FILES = {
    'Signal' : R.TFile.Open('roots/ReweightedPlots_Trig_HTo2XTo2Mu2J.root'),
    'Data'   : R.TFile.Open('roots/ReweightedPlots_IDPHI_DATA.root'),
}

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

    s.Scale(ScaleFactor(sp, factor, 1.e-2))

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
        S, B, cutVal, FOMs = calculateFOM(s, b, sCum, bCum, nBins, ibin, xAxis, CONFIG[quantity]['forward'])
        if FOMs[FIGURE_OF_MERIT] > fom_max:
            fom_max = FOMs[FIGURE_OF_MERIT]
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

    c = Plotter.Canvas(lumi='({} GeV, {} GeV) by {}'.format(masses[0], masses[1], PRETTY_LEG))
    c.addMainPlot(d)
    c.addMainPlot(p)
    c.mainPad.SetLogx()

    p.setColor(R.kBlue, which='LM')
    d.setColor(R.kWhite, which='M')
    c.firstPlot.setTitles(X='c#tau [cm]', Y=CONFIG[quantity]['pretty']+' Cut Value')

    c.cleanup('pdfs/RW_{}_{}_{}_{}.pdf'.format(quantity, masses[0], masses[1], FIGURE_OF_MERIT))

def makeGlobal(quantity):
    dummyX, dummyY = np.array([.1, 1000.]), np.array([0., 25.])
    dummyG = R.TGraph(2, dummyX, dummyY)
    d = Plotter.Plot(dummyG, '', '', 'p')

    n, x, y, g, p = {}, {}, {}, {}, {}
    for masses in DATA:
        n[masses] = len(DATA[masses][quantity]['x'])
        x[masses] = np.array(DATA[masses][quantity]['x'])
        y[masses] = np.array(DATA[masses][quantity]['y'])

        g[masses] = R.TGraph(n[masses], x[masses], y[masses])
        p[masses] = Plotter.Plot(g[masses], '', '', 'pl')

    c = Plotter.Canvas(lumi='{}'.format(PRETTY_LEG))
    c.addMainPlot(d)
    for masses in p:
        c.addMainPlot(p[masses])
    c.mainPad.SetLogx()

    d.setColor(R.kWhite, which='M')
    for masses in p:
        p[masses].setColor(R.kBlue, which='LM')
    c.firstPlot.setTitles(X='c#tau [cm]', Y=CONFIG[quantity]['pretty']+' Cut Value')

    c.cleanup('pdfs/RW_{}_Global_{}.pdf'.format(quantity, FIGURE_OF_MERIT))

for fs in ('2Mu2J',):
    done = []
    for sp in SignalInfo:
    #for sp in ((1000, 150, 1000),):
        masses = (sp[0], sp[1])
        if masses not in done:
            done.append(masses)
            for quantity in CONFIG:
                makePlot(quantity, masses)
                makeGlobal(quantity)
