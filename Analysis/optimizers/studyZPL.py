import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
from DisplacedDimuons.Common.Utilities import SPStr, SPLumiStr
import DisplacedDimuons.Analysis.AnalysisTools as AT
import DisplacedDimuons.Analysis.HistogramGetter as HG
import numpy as np
from OptimizerTools import SignalInfo, ScaleFactor, calculateFOM, PARSER

PRETTY_LEG = {'ZBi':'Z_{Bi}', 'ZPL':'Z_{PL}'}

FILES = {
    'Signal' : R.TFile.Open('roots/ReweightedPlots_Trig_HTo2XTo2Mu2J.root'),
    'Data'   : R.TFile.Open('roots/ReweightedPlots_IDPHI_DATA.root'),
}

FACTORS = (1, 2, 5, 10)

CONFIG = {
    'LxySig' : {'forward':False, 'pretty':'dimuon L_{xy}/#sigma_{L_{xy}}'},
}

# this plots the ZBi and ZPL curves near each other
# this shows you what is going on with finding the optimum of the curves
def compareFOMPlot(quantity, sp, sigmaBMode='GLOBAL'):
    keys = FACTORS
    for FACTOR in FACTORS:
        s = HG.getHistogram(FILES['Signal'], (fs, sp), '{}_{}'.format(quantity, FACTOR)).Clone()

        if sigmaBMode == 'GLOBAL':
            s.Scale(ScaleFactor(sp, 1, 1.e-2))
            extra = 'GLOBAL'

        DHists, DPConfig = HG.getDataHistograms(FILES['Data'], '{}_1'.format(quantity), addFlows=False)
        b = DHists['{}_1'.format(quantity)]['data']

        # get cumulatives
        bCum = b.GetCumulative(CONFIG[quantity]['forward'])
        sCum = s.GetCumulative(CONFIG[quantity]['forward'])
        fom  = {z:sCum.Clone() for z in ('ZBi', 'ZPL')}

        nBins = sCum.GetNbinsX()
        xAxis = sCum.GetXaxis()

        # dictionaries instead of numbers because we have 2 sets of ZBi curves
        fom_max = {z:0. for z in ('ZBi', 'ZPL')}
        opt_cut = {z:0. for z in ('ZBi', 'ZPL')}
        opt_s   = {z:0. for z in ('ZBi', 'ZPL')}
        opt_b   = {z:0. for z in ('ZBi', 'ZPL')}

        for ibin in range(1,nBins+1):
            S, B, cutVal, FOMs = calculateFOM(s, b, sCum, bCum, nBins, ibin, xAxis, CONFIG[quantity]['forward'])
            for z in ('ZBi', 'ZPL'):
                if FOMs[z] > fom_max[z]:
                    fom_max[z] = FOMs[z]
                    opt_cut[z] = cutVal
                    opt_s  [z] = S
                    opt_b  [z] = B
            
                fom[z].SetBinContent(ibin, FOMs[z])

        p = {z:Plotter.Plot(fom[z], PRETTY_LEG[z], 'l', 'hist p') for z in fom}

        colors = {'ZBi':R.kRed, 'ZPL':R.kBlue}

        c = Plotter.Canvas(lumi='({} GeV, {} GeV, {} mm){}'.format(sp[0], sp[1], sp[2], '' if FACTOR == 1 else ' #rightarrow {} mm'.format(sp[2]/FACTOR)))
        for z in fom:
            c.addMainPlot(p[z])
            p[z].setColor(colors[z], which='LM')

        c.makeLegend(lWidth=0.1, pos='tr')
        #c.legend.SetMargin(0.1)
        c.legend.resizeHeight()

        lines = {z:R.TLine(opt_cut[z], 0., opt_cut[z], max(fom_max.values())*1.1) for z in fom}
        for z in fom:
            lines[z].SetLineStyle(2)
            lines[z].SetLineColor(colors[z])
            lines[z].Draw()

        for i, z in enumerate(fom.keys()):
            c.drawText(text='#color[{:d}]{{opt = {:.1f}}}'.format(colors[z], opt_cut[z]), pos=(c.legend.GetX2(), c.legend.GetY1()-.04-i*.04), align='br')

        c.firstPlot.SetMinimum(0.)
        c.firstPlot.SetMaximum(max(fom_max.values())*1.1)
        c.firstPlot.setTitles(Y='Figure of Merit')
        RT.addBinWidth(c.firstPlot)

        c.cleanup('pdfs/COMPARE_FOM-{}_{}_{}_{}_{}_{}.pdf'.format(extra, quantity, sp[0], sp[1], sp[2], FACTOR))

for fs in ('2Mu2J',):
    #for sp in ((1000, 150, 1000),):
    for sp in SignalInfo:
        for quantity in CONFIG:
            compareFOMPlot (quantity, sp)


#ARGS = PARSER.parse_args()
#FIGURE_OF_MERIT = ARGS.FOM
#
#hexVal = {
#    'orange' : dict(zip(FACTORS,reversed([(254,237,222),(253,190,133),(253,141, 60),(217, 71,  1)]))),
#    'blue'   : dict(zip(FACTORS,reversed([(239,243,255),(189,215,231),(107,174,214),( 33,113,181)])))
#}
#
#COLORS = {
#    col : {f:{'idx':7000*(j+1)+i, 'col':R.TColor(7000*(j+1)+i, *[c/255. for c in hexVal[col][f]])} for i,f in enumerate(FACTORS)} for j,col in enumerate(hexVal.keys())
#}
#
#
## this plots the two ZBi curves near each other, with some options for tweaking what cross section to use
## this shows you what is going on with finding the optimum of the curves
#def makeKinkFOMPlot(quantity, masses, sigmaBMode='GLOBAL'):
#    points = sorted([sp for sp in SignalInfo if sp[0] == masses[0] and sp[1] == masses[1]], key=lambda x: x[2])
#    keys = [(sp, f) for sp in reversed(points) for f in FACTORS]
#    s = {key:HG.getHistogram(FILES['Signal'], (fs, key[0]), '{}_{}'.format(quantity, key[1])).Clone() for key in keys} 
#
#    if sigmaBMode == 'GLOBAL':
#        for key in s:
#            s[key].Scale(ScaleFactor(points[0], 1, 1.e-2))
#        extra = 'GLOBAL'
#
#    DHists, DPConfig = HG.getDataHistograms(FILES['Data'], '{}_1'.format(quantity), addFlows=False)
#    b = DHists['{}_1'.format(quantity)]['data']
#
#    # get cumulatives
#    bCum = b.GetCumulative(CONFIG[quantity]['forward'])
#    sCum = {key:s[key].GetCumulative(CONFIG[quantity]['forward']) for key in keys}
#    fom  = {key:sCum[key].Clone() for key in keys}
#
#    nBins = sCum[keys[0]].GetNbinsX()
#    xAxis = sCum[keys[0]].GetXaxis()
#
#    # dictionaries instead of numbers because we have 2 sets of ZBi curves
#    fom_max = {key:0. for key in keys}
#    opt_cut = {key:0. for key in keys}
#    opt_s   = {key:0. for key in keys}
#    opt_b   = {key:0. for key in keys}
#
#    for ibin in range(1,nBins+1):
#        for key in keys:
#            S, B, cutVal, FOMs = calculateFOM(s[key], b, sCum[key], bCum, nBins, ibin, xAxis, CONFIG[quantity]['forward'])
#            if FOMs[FIGURE_OF_MERIT] > fom_max[key]:
#                fom_max[key] = FOMs[FIGURE_OF_MERIT]
#                opt_cut[key] = cutVal
#                opt_s  [key] = S
#                opt_b  [key] = B
#
#            fom[key].SetBinContent(ibin, FOMs[FIGURE_OF_MERIT])
#
#    p = {key:Plotter.Plot(fom[key], 'c#tau = {} mm/{}'.format(key[0][2], key[1]), 'l', 'hist p') for key in keys}
#
#    colors = {}
#    for sp in points:
#        for factor in FACTORS:
#            colors[(sp, factor)] = COLORS['orange' if sp == points[0] else 'blue'][factor]['idx']
#
#    c = Plotter.Canvas(lumi='({} GeV, {} GeV)'.format(*masses))
#    for key in keys:
#        c.addMainPlot(p[key])
#
#    for key in keys:
#        p[key].setColor(colors[key], which='LM')
#
#    c.makeLegend(lWidth=0.3, pos='tr')
#    c.legend.SetMargin(0.1)
#    c.legend.resizeHeight()
#
#    lines = {key:R.TLine(opt_cut[key], 0., opt_cut[key], max(fom_max.values())*1.1) for key in keys}
#    for key in keys:
#        lines[key].SetLineStyle(2)
#        lines[key].SetLineColor(colors[key])
#        lines[key].Draw()
#
#    for i, key in enumerate(keys):
#        c.drawText(text='#color[{:d}]{{opt = {:.1f}}}'.format(colors[key], opt_cut[key]), pos=(c.legend.GetX2(), c.legend.GetY1()-.04-i*.04), align='br')
#
#    c.firstPlot.SetMinimum(0.)
#    c.firstPlot.SetMaximum(max(fom_max.values())*1.1)
#    c.firstPlot.setTitles(Y=PRETTY_LEG)
#    RT.addBinWidth(c.firstPlot)
#
#    c.cleanup('pdfs/X_FOM-{}_{}_{}_{}_{}.pdf'.format(extra, quantity, masses[0], masses[1], FIGURE_OF_MERIT))
