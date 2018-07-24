import re
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
from DisplacedDimuons.Common.Utilities import SPStr
import HistogramGetter

# get histograms
HISTS = HistogramGetter.getHistograms('../analyzers/roots/Main/RecoMuonPlots.root')
f = R.TFile.Open('../analyzers/roots/Main/RecoMuonPlots.root')

# make plots that are per sample
def makePerSamplePlots():
    for ref in HISTS:
        for key in HISTS[ref]:
            if 'deltaRGR' in key: continue
            if 'DoubleMuon' in ref: continue
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
                if '_Matched' in key: continue
                name = ref
                lumi = HistogramGetter.PLOTCONFIG[ref]['LATEX']
                legName = HistogramGetter.PLOTCONFIG[ref]['LATEX']

            h = HISTS[ref][key].Clone()
            if h.GetNbinsX() > 100: h.Rebin(10)
            RT.addFlows(h)
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

        h = {
            'Data'       : HISTS['DoubleMuonRun2016B-07Aug17-v2'][hkey].Clone(),
#           'Signal'     : HISTS[('4Mu', (125, 20, 13))         ][hkey].Clone(),
            'BG'         : R.THStack('hBG', '')
        }

        PConfig = {
            'Data'       : ('DoubleMuon2016'               , 'pe', 'pe'  ),
#           'Signal'     : ('H#rightarrow2X#rightarrow4#mu', 'l' , 'hist'),
            'BG'         : (''                             , ''  , 'hist'),
        }

        PC = HistogramGetter.PLOTCONFIG

        for key in BGORDER:
            h[key] = HISTS[key][hkey].Clone()
            if h[key].GetNbinsX() > 100: h[key].Rebin(10)
            RT.addFlows(h[key])
            h[key].Scale(PC[key]['WEIGHT'])
            PConfig[key] = (PC[key]['LATEX'], 'f', 'hist')
            h['BG'].Add(h[key])

        for era in ('C', 'D', 'E', 'F', 'G', 'H'):
            h['Data'].Add(HISTS['DoubleMuonRun2016{}-07Aug17'.format(era)][hkey])
        if h['Data'].GetNbinsX() > 100: h['Data'].Rebin(10)
        RT.addFlows(h['Data'])

        p = {}
        for key in h:
            p[key] = Plotter.Plot(h[key], *PConfig[key])

        fname = 'pdfs/{}_Stack{}{}.pdf'.format(hkey, '-Log' if logy else '', '-Rat' if DataMC else '')

        for key in BGORDER:
            p[key].SetLineColor(PC[key]['COLOR'])
            p[key].SetFillColor(PC[key]['COLOR'])

        canvas = Plotter.Canvas(ratioFactor=0. if not DataMC else 1./3., logy=logy, fontscale=1. if not DataMC else 1.+1./3.)
        canvas.addMainPlot(p['BG'])
        canvas.addMainPlot(p['Data'])
#       canvas.addMainPlot(p['Signal'])

        canvas.makeLegend(lWidth=.27, pos='tr', autoOrder=False, fontscale=0.8 if not DataMC else 1.)
        canvas.addLegendEntry(p['Data'     ])
        for key in reversed(BGORDER):
            canvas.addLegendEntry(p[key])
#       canvas.addLegendEntry(p['Signal'])
        canvas.legend.resizeHeight()

        p['BG'].setTitles(X=p['WJets'].GetXaxis().GetTitle(), Y='Normalized Counts')
        RT.addBinWidth(p['BG'])

        canvas.firstPlot.SetMaximum(h['BG'].GetStack().Last().GetMaximum() * 1.05)
        #canvas.firstPlot.SetMaximum(1.e-4)

        if DataMC:
            canvas.makeRatioPlot(p['Data'].plot, p['BG'].plot.GetStack().Last())
            canvas.firstPlot.scaleTitleOffsets(0.8, axes='Y')
            canvas.rat      .scaleTitleOffsets(0.8, axes='Y')

#       p['Signal'    ].SetLineStyle(2)
#       p['Signal'    ].SetLineColor(R.kRed)

        canvas.finishCanvas(extrascale=1. if not DataMC else 1.+1./3.)
        canvas.save(fname)
        canvas.deleteCanvas()

# make plots that are per sample
def makeGenRecoPlots():
    for ref in HISTS:
        if not type(ref) == tuple: continue
        if ref[0] == '4Mu':
            name = 'HTo2XTo4Mu_'
            latexFS = '4#mu'
        elif ref[0] == '2Mu2J':
            name = 'HTo2XTo2Mu2J_'
            latexFS = '2#mu2j'
        name += SPStr(ref[1])
        lumi = '{} ({} GeV, {} GeV, {} mm)'.format(ref[0], *ref[1])

        colors = {'Matched':R.kRed, 'Closest':R.kBlue}
        KEYS = ('Matched', 'Closest')

        for MUON in ('DSA', 'RSA'):
            h, p = {}, {}
            for key in KEYS:
                h[key] = HISTS[ref]['{}_{}_{}'.format(MUON, 'deltaRGR', key)].Clone()
                if h[key].GetNbinsX() > 100: h.Rebin(10)
                RT.addFlows(h[key])
                p[key] = Plotter.Plot(h[key], key, 'l', 'hist')
            fname = 'pdfs/{}_{}_{}_{}.pdf'.format(MUON, 'deltaRGR', 'Matched', name)

            canvas = Plotter.Canvas(lumi=lumi)
            for key in KEYS:
                canvas.addMainPlot(p[key])
                p[key].SetLineColor(colors[key])

            canvas.makeLegend(lWidth=.25, pos='tr')
            canvas.legend.resizeHeight()
            canvas.setMaximum()
            RT.addBinWidth(canvas.firstPlot)

            LPOS = (canvas.legend.GetX1NDC()+.01, canvas.legend.GetY1NDC()-.04)

            for i, key in enumerate(KEYS):
                canvas.drawText(text='#color[{}]{{n = {:d}}}'.format(colors[key], int(p[key].GetEntries())), pos=(LPOS[0], LPOS[1]-i*0.04))


            canvas.cleanup(fname)

makePerSamplePlots()
makeStackPlots(False)
makeStackPlots(False, True)
makeStackPlots(True, True)
makeGenRecoPlots()
