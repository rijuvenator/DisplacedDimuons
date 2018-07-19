import re
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
from DisplacedDimuons.Common.Utilities import SPStr
import HistogramGetter

# get histograms
HISTS = HistogramGetter.getHistograms('../analyzers/roots/DimuonPlots.root')
f = R.TFile.Open('../analyzers/roots/DimuonPlots.root')

# make plots that are per sample
def makePerSamplePlots():
    for ref in HISTS:
        for key in HISTS[ref]:
            if 'LxySigVSLxy' in key: continue
            if type(ref) == tuple:
                if ref[0] == '4Mu':
                    name = 'HTo2XTo4Mu_'
                    latexFS = '4#mu'
                elif ref[0] == '2Mu2J':
                    name = 'HTo2XTo2Mu2J_'
                    latexFS = '2#mu2j'
                name += SPStr(ref[1])
                lumi = '{} ({} GeV, {} GeV, {} mm)'.format(ref[0], *ref[1])
                legName = HistogramGetter.PLOTCONFIG['HTo2XTo'+ref[0]]['LATEX']
            else:
                name = ref
                lumi = HistogramGetter.PLOTCONFIG[ref]['LATEX']
                legName = HistogramGetter.PLOTCONFIG[ref]['LATEX']
                if '_Matched' in key: continue

            h = HISTS[ref][key].Clone()
            if h.GetNbinsX() > 100: h.Rebin(10)
            p = Plotter.Plot(h, legName, 'l', 'hist')
            fname = 'pdfs/{}_{}.pdf'.format(key, name)

            canvas = Plotter.Canvas(lumi=lumi)
            canvas.addMainPlot(p)
            canvas.makeLegend(lWidth=.25, pos='tr')
            canvas.legend.moveLegend(Y=-.3)
            canvas.legend.resizeHeight()
            p.SetLineColor(R.kBlue)
            RT.addBinWidth(p)

            pave = canvas.makeStatsBox(p, color=R.kBlue)
            canvas.cleanup(fname)

# make stack plots
def makeStackPlots(DataMC=False, logy=False):
    BGORDER = ('WJets', 'WW', 'WZ', 'ZZ', 'tW', 'tbarW', 'ttbar', 'DY10to50', 'DY50toInf')
    for hkey in HISTS['DY50toInf']:
        if 'Matched' in hkey: continue
        if 'LxySigVSLxy' in hkey: continue

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
            if h[key].GetNbinsX() > 100: h[key].Rebin(10)
            h[key].Scale(PC[key]['WEIGHT'])
            PConfig[key] = (PC[key]['LATEX'], 'f', 'hist')
            h['BG'].Add(h[key])

        p = {}
        for key in h:
            p[key] = Plotter.Plot(h[key], *PConfig[key])

        fname = 'pdfs/{}_Stack{}.pdf'.format(hkey, '-Log' if logy else '')

        for key in BGORDER:
            p[key].SetLineColor(PC[key]['COLOR'])
            p[key].SetFillColor(PC[key]['COLOR'])

        canvas = Plotter.Canvas(ratioFactor=0. if not DataMC else 1./3., cHeight=600 if not DataMC else 800, logy=logy)
        canvas.addMainPlot(p['BG'])
#       canvas.addMainPlot(p['Data'])
#       canvas.addMainPlot(p['Signal'])

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

# make 3D color plots
def makeColorPlots(key):
    key = 'Dim_' + key

    for ref in HISTS:
        if type(ref) == tuple:
            if ref[0] == '4Mu':
                name = 'HTo2XTo4Mu_'
                latexFS = '4#mu'
            elif ref[0] == '2Mu2J':
                name = 'HTo2XTo2Mu2J_'
                latexFS = '2#mu2j'
            name += SPStr(ref[1])
            lumi = '{} ({} GeV, {} GeV, {} mm)'.format(ref[0], *ref[1])
        else:
            name = ref
            lumi = HistogramGetter.PLOTCONFIG[ref]['LATEX']
            if '_Matched' in key: continue

        h = HISTS[ref][key].Clone()
        h.Rebin2D(10, 10)
        p = Plotter.Plot(h, '', '', 'colz')
        canvas = Plotter.Canvas(lumi=lumi)
        #canvas.mainPad.SetLogz(True)
        canvas.addMainPlot(p)
        canvas.scaleMargins(1.75, edges='R')
        canvas.scaleMargins(0.8, edges='L')

        fname = 'pdfs/{}_{}.pdf'.format(key, name)
        canvas.cleanup(fname)

makePerSamplePlots()
makeStackPlots(False)
makeStackPlots(False, True)
makeColorPlots('LxySigVSLxy')
makeColorPlots('LxySigVSLxy_Matched')
makeColorPlots('LxyErrVSLxy')
makeColorPlots('LxyErrVSLxy_Matched')
