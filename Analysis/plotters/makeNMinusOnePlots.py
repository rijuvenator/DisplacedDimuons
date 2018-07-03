import re
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.Selections as Selections
from DisplacedDimuons.Common.Utilities import SPStr
import HistogramGetter

# get histograms
HISTS = HistogramGetter.getHistograms('../analyzers/roots/nMinusOnePlots.root')
f = R.TFile.Open('../analyzers/roots/nMinusOnePlots.root')

# make per sample plots
def makePerSamplePlots():
    for ref in HISTS:
        for key in HISTS[ref]:
            if type(ref) == tuple:
                if ref[0] == '4Mu': name = 'HTo2XTo4Mu_'
                elif ref[0] == '2Mu2J' : name = 'HTo2XTo2Mu2J_'
                name += SPStr(ref[1])
                lumi = '{} ({}, {}, {})'.format(ref[0], *ref[1])
            else:
                name = ref
                lumi = ref

            h = HISTS[ref][key]
            p = Plotter.Plot(h, 'H#rightarrow2X#rightarrow4#mu MC', 'l', 'hist')
            fname = 'pdfs/NM1_{}_{}.pdf'.format(key, name)
            canvas = Plotter.Canvas(lumi=lumi)
            canvas.lumi += ' : |#Delta#Phi| ' + ('<' if '_Less' in key else '>') + ' #pi/2'
            canvas.addMainPlot(p)
            canvas.makeLegend(lWidth=.25, pos='tr')
            canvas.legend.moveLegend(Y=-.3)
            canvas.legend.resizeHeight()
            p.SetLineColor(R.kBlue)

            cutKey = key.replace('_Less','').replace('_More','')
            cutVal = Selections.CUTS[cutKey].val

            l = R.TLine(cutVal, p.GetMinimum(), cutVal, p.GetMaximum()*1.05)
            l.SetLineStyle(2)
            l.SetLineWidth(2)
            l.Draw()

            canvas.cleanup(fname)

# make stack plots
def makeStackPlots(DataMC=False):
    #for hkey in HISTS[(125, 20, 13)]:
    for hkey in ('deltaR_Less',):
        h = {
            'DY50toInf'  : HISTS['DY50toInf'                 ][hkey],
#           'Data'       : HISTS['DoubleMuonRun2016D-07Aug17'][hkey],
            'Signal'     : HISTS[('4Mu', (125, 20, 13))      ][hkey],
            'BG'         : R.THStack('hBG', '')
        }

        PConfig = {
            'DY50toInf'  : ('Drell-Yan 50-#infty GeV'      , 'f' , 'hist'),
#           'Data'       : ('DoubleMuon2016D'              , 'pe', 'pe'  ),
            'Signal'     : ('H#rightarrow2X#rightarrow4#mu', 'l' , 'hist'),
            'BG'         : (''                             , ''  , 'hist'),
        }

        h['BG'].Add(h['DY50toInf'])

        p = {}
        for key in h:
            p[key] = Plotter.Plot(h[key], *PConfig[key])

        fname = 'NM1_Stack_{}.pdf'.format(hkey)

        p['DY50toInf'].SetLineColor(R.kOrange)
        p['DY50toInf'].SetFillColor(R.kOrange)

        canvas = Plotter.Canvas(ratioFactor=0. if not DataMC else 1./3., cHeight=600 if not DataMC else 800)
        canvas.addMainPlot(p['BG'])
#       canvas.addMainPlot(p['Data'])
        canvas.addMainPlot(p['Signal'])

        canvas.makeLegend(lWidth=.25, pos='tl', autoOrder=False)
#       canvas.addLegendEntry(p['Data'     ])
        canvas.addLegendEntry(p['DY50toInf'])
        canvas.addLegendEntry(p['Signal'   ])
        canvas.legend.resizeHeight()

        if DataMC:
            canvas.makeRatioPlot(p['Data'].plot, p['BG'].plot.GetStack().Last())

        p['Signal'    ].SetLineStyle(2)
        p['Signal'    ].SetLineColor(R.kRed)

        canvas.cleanup(fname)

makePerSamplePlots()
makeStackPlots(True)
