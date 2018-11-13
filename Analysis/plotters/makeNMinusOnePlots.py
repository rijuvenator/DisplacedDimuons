import re
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
import DisplacedDimuons.Analysis.Selections as Selections
from DisplacedDimuons.Common.Utilities import SPStr, SPLumiStr
import DisplacedDimuons.Analysis.HistogramGetter as HistogramGetter

TRIGGER = False

# get histograms
HISTS = HistogramGetter.getHistograms('../analyzers/roots/Main/nMinusOnePlots.root')
f = R.TFile.Open('../analyzers/roots/Main/nMinusOnePlots.root')

# make per sample plots
def makePerSamplePlots():
    for ref in HISTS:
        for key in HISTS[ref]:
            if type(ref) == tuple:
                if ref[0] == '4Mu': name = 'HTo2XTo4Mu_'
                elif ref[0] == '2Mu2J' : name = 'HTo2XTo2Mu2J_'
                name += SPStr(ref[1])
                if TRIGGER:
                    name = 'Trig-'+name
                lumi = SPLumiStr(ref[0], *ref[1])
                legName = HistogramGetter.PLOTCONFIG['HTo2XTo'+ref[0]]['LATEX']
            else:
                name = ref
                lumi = HistogramGetter.PLOTCONFIG[ref]['LATEX']
                legName = HistogramGetter.PLOTCONFIG[ref]['LATEX']

            h = HISTS[ref][key].Clone()
            RT.addFlows(h)
            p = Plotter.Plot(h, legName, 'l', 'hist')
            fname = 'pdfs/NM1_{}_{}.pdf'.format(key, name)
            canvas = Plotter.Canvas(lumi=lumi)
            canvas.lumi += ' : |#Delta#Phi| ' + ('<' if '_Less' in key else '>') + ' #pi/2'
            canvas.addMainPlot(p)
            canvas.makeLegend(lWidth=.25, pos='tr')
            canvas.legend.moveLegend(Y=-.3)
            canvas.legend.resizeHeight()
            p.SetLineColor(R.kBlue)
            RT.addBinWidth(p)

            cutKey = key.replace('_Less','').replace('_More','')
            cutVal = Selections.CUTS[cutKey].val

            l = R.TLine(cutVal, p.GetMinimum(), cutVal, p.GetMaximum()*1.05)
            l.SetLineStyle(2)
            l.SetLineWidth(2)
            l.Draw()

            canvas.cleanup(fname)

# make stack plots
def makeStackPlots(DataMC=False, logy=False):
    BGORDER = ('WJets', 'WW', 'WZ', 'ZZ', 'tW', 'tbarW', 'ttbar', 'DY10to50', 'DY50toInf')
    for hkey in HISTS['DY50toInf']:

        h = {
#           'Data'       : HISTS['DoubleMuonRun2016D-07Aug17'][hkey].Clone(),
#           'Signal'     : HISTS[('4Mu', (125, 20, 13))      ][hkey].Clone(),
            'BG'         : R.THStack('hBG', '')
        }

        PConfig = {
#           'Data'       : ('DoubleMuon2016D'              , 'pe', 'pe'  ),
#           'Signal'     : ('H#rightarrow2X#rightarrow4#mu', 'l' , 'hist'),
            'BG'         : (''                             , ''  , 'hist'),
        }

        PC = HistogramGetter.PLOTCONFIG

        for key in BGORDER:
            h[key] = HISTS[key][hkey].Clone()
            RT.addFlows(h[key])
            if h[key].GetNbinsX() > 100: h[key].Rebin(10)
            h[key].Scale(PC[key]['WEIGHT'])
            PConfig[key] = (PC[key]['LATEX'], 'f', 'hist')
            h['BG'].Add(h[key])

        p = {}
        for key in h:
            p[key] = Plotter.Plot(h[key], *PConfig[key])

        fname = 'pdfs/NM1_{}_Stack{}.pdf'.format(hkey, '-Log' if logy else '')

        for key in BGORDER:
            p[key].setColor(PC[key]['COLOR'], which='LF')

        canvas = Plotter.Canvas(ratioFactor=0. if not DataMC else 1./3., cHeight=600 if not DataMC else 800, logy=logy)
        canvas.addMainPlot(p['BG'])
#       canvas.addMainPlot(p['Data'])
#       canvas.addMainPlot(p['Signal'])

        canvas.lumi += ' : |#Delta#Phi| ' + ('<' if '_Less' in key else '>') + ' #pi/2'

        canvas.makeLegend(lWidth=.27, pos='tr', autoOrder=False, fontscale=0.8)
#       canvas.addLegendEntry(p['Data'     ])
        for key in reversed(BGORDER):
            canvas.addLegendEntry(p[key])
#       canvas.addLegendEntry(p['Signal'])
        canvas.legend.resizeHeight()

        p['BG'].setTitles(X=p['WJets'].GetXaxis().GetTitle(), Y='Normalized Counts')
        RT.addBinWidth(p['BG'])

        canvas.firstPlot.SetMaximum(h['BG'].GetStack().Last().GetMaximum() * 1.05)
        #canvas.firstPlot.SetMaximum(1.e-4)

#       if DataMC:
#           canvas.makeRatioPlot(p['Data'].plot, p['BG'].plot.GetStack().Last())

#       p['Signal'    ].SetLineStyle(2)
#       p['Signal'    ].SetLineColor(R.kRed)

        canvas.cleanup(fname)

makePerSamplePlots()
makeStackPlots(False)
makeStackPlots(False, True)
