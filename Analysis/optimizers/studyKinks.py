import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
from DisplacedDimuons.Common.Utilities import SPStr, SPLumiStr
import DisplacedDimuons.Analysis.AnalysisTools as AT
import DisplacedDimuons.Analysis.HistogramGetter as HG
import numpy as np
from OptimizerTools import SignalInfo, ScaleFactor, calculateFOM, PARSER

ARGS = PARSER.parse_args()
FIGURE_OF_MERIT = ARGS.FOM

PRETTY_LEG = {'ZBi':'Z_{Bi}', 'ZPL':'Z_{PL}'}[FIGURE_OF_MERIT]

FILES = {
    'Signal' : R.TFile.Open('roots/ReweightedPlots_Trig_HTo2XTo2Mu2J.root'),
    'Data'   : R.TFile.Open('roots/ReweightedPlots_IDPHI_DATA.root'),
}

FACTORS = (1, 2, 5, 10)

CONFIG = {
    'LxySig' : {'forward':False, 'pretty':'dimuon L_{xy}/#sigma_{L_{xy}}'},
}

# this makes a plot of the LxySig distribution for the cTau/10 and cTau plots, scaled to unity
# so that the differences in shape can be compared
def makeKinkDistPlot(quantity, masses):
    points = sorted([sp for sp in SignalInfo if sp[0] == masses[0] and sp[1] == masses[1]], key=lambda x: x[2])
    s = {
        points[0] : HG.getHistogram(FILES['Signal'], (fs, points[0]), '{}_1' .format(quantity)).Clone(),
        points[1] : HG.getHistogram(FILES['Signal'], (fs, points[1]), '{}_10'.format(quantity)).Clone(),
    }

    s[points[0]].Scale(1./s[points[0]].Integral(0, s[points[0]].GetNbinsX()+1))
    s[points[1]].Scale(1./s[points[1]].Integral(0, s[points[1]].GetNbinsX()+1))

    #RT.addFlows(s[points[0]])
    #RT.addFlows(s[points[1]])

    s[points[0]].Rebin(2)
    s[points[1]].Rebin(2)

    pl = {
        points[0] : Plotter.Plot(s[points[0]], 'c#tau = {} mm, nominal'   .format(points[0][2]), 'l', 'hist'),
        points[1] : Plotter.Plot(s[points[1]], 'c#tau = {} mm, reweighted'.format(points[0][2]), 'l', 'hist'),
    }

    colors = {
        points[0] : R.kBlue,
        points[1] : R.kRed ,
    }

    c = Plotter.Canvas(lumi='({} GeV, {} GeV)'.format(*masses))
    c.addMainPlot(pl[points[0]])
    c.addMainPlot(pl[points[1]])

    for p in points:
        pl[p].setColor(colors[p], which='LM')

    c.makeLegend(lWidth=0.3, pos='tr')
    c.legend.SetMargin(0.1)
    c.legend.resizeHeight()

    c.drawText(text='lol', pos=(c.legend.GetX1(), c.legend.GetY1()+.4), NDC=False)

    c.setMaximum()
    RT.addBinWidth(c.firstPlot)

    c.cleanup('pdfs/KINK_Dist_{}_{}_{}_{}.pdf'.format(quantity, masses[0], masses[1], FIGURE_OF_MERIT))

# this plots the two ZBi curves near each other, with some options for tweaking what cross section to use
# this shows you what is going on with finding the optimum of the curves
def makeKinkFOMPlot(quantity, masses, sigmaBMode='DEFAULT'):
    points = sorted([sp for sp in SignalInfo if sp[0] == masses[0] and sp[1] == masses[1]], key=lambda x: x[2])
    s = {
        points[0] : HG.getHistogram(FILES['Signal'], (fs, points[0]), '{}_1' .format(quantity)).Clone(),
        points[1] : HG.getHistogram(FILES['Signal'], (fs, points[1]), '{}_10'.format(quantity)).Clone(),
    }

    if sigmaBMode == 'DEFAULT':
        s[points[0]].Scale(ScaleFactor(points[0], 1 ))
        s[points[1]].Scale(ScaleFactor(points[1], 10))
        extra = ''

    elif sigmaBMode == 'SAME':
        s[points[0]].Scale(ScaleFactor(points[0], 1 ))
        s[points[1]].Scale(ScaleFactor(points[0], 1 ))
        extra = '_SAME'

    elif sigmaBMode == 'GLOBAL':
        s[points[0]].Scale(ScaleFactor(points[0], 1 , 1.e-2))
        s[points[1]].Scale(ScaleFactor(points[1], 1 , 1.e-2))
        extra = '_GLOBAL'

    DHists, DPConfig = HG.getDataHistograms(FILES['Data'], '{}_1'.format(quantity), addFlows=False)
    b = DHists['{}_1'.format(quantity)]['data']

    # get cumulatives
    bCum = b.GetCumulative(CONFIG[quantity]['forward'])
    sCum = {p:s[p].GetCumulative(CONFIG[quantity]['forward']) for p in points}
    fom  = {p:sCum[p].Clone() for p in points}

    nBins = sCum[points[0]].GetNbinsX()
    xAxis = sCum[points[0]].GetXaxis()

    # dictionaries instead of numbers because we have 2 sets of ZBi curves
    fom_max = {p:0. for p in points}
    opt_cut = {p:0. for p in points}
    opt_s   = {p:0. for p in points}
    opt_b   = {p:0. for p in points}

    for ibin in range(1,nBins+1):
        for p in points:
            S, B, cutVal, FOMs = calculateFOM(s[p], b, sCum[p], bCum, nBins, ibin, xAxis, CONFIG[quantity]['forward'])
            if FOMs[FIGURE_OF_MERIT] > fom_max[p]:
                fom_max[p] = FOMs[FIGURE_OF_MERIT]
                opt_cut[p] = cutVal
                opt_s  [p] = S
                opt_b  [p] = B

            fom[p].SetBinContent(ibin, FOMs[FIGURE_OF_MERIT])

    pl = {
        points[0] : Plotter.Plot(fom[points[0]], 'c#tau = {} mm, nominal'   .format(points[0][2]), 'l', 'hist p'),
        points[1] : Plotter.Plot(fom[points[1]], 'c#tau = {} mm, reweighted'.format(points[0][2]), 'l', 'hist p'),
    }

    colors = {
        points[0] : R.kBlue,
        points[1] : R.kRed ,
    }

    c = Plotter.Canvas(lumi='({} GeV, {} GeV)'.format(*masses))
    c.addMainPlot(pl[points[0]])
    c.addMainPlot(pl[points[1]])

    for p in points:
        pl[p].setColor(colors[p], which='LM')

    c.makeLegend(lWidth=0.3, pos='tr')
    c.legend.SetMargin(0.1)
    c.legend.resizeHeight()

    lines = {p:R.TLine(opt_cut[p], 0., opt_cut[p], max(fom_max.values())*1.1) for p in points}
    for p in points:
        lines[p].SetLineStyle(2)
        lines[p].SetLineColor(colors[p])
        lines[p].Draw()

    for i, p in enumerate(points):
        c.drawText(text='#color[{:d}]{{opt = {:.1f}}}'.format(colors[p], opt_cut[p]), pos=(c.legend.GetX2(), c.legend.GetY1()-.04-i*.04), align='br')

    c.firstPlot.SetMinimum(0.)
    c.firstPlot.SetMaximum(max(fom_max.values())*1.1)
    c.firstPlot.setTitles(Y=PRETTY_LEG)
    RT.addBinWidth(c.firstPlot)

    c.cleanup('pdfs/KINK_FOM{}_{}_{}_{}_{}.pdf'.format(extra, quantity, masses[0], masses[1], FIGURE_OF_MERIT))

for fs in ('2Mu2J',):
    done = []
    #for sp in ((1000, 150, 1000),):
    for sp in SignalInfo:
        masses = (sp[0], sp[1])
        if masses not in done:
            done.append(masses)
            for quantity in CONFIG:
                makeKinkDistPlot(quantity, masses)
                makeKinkFOMPlot (quantity, masses)

