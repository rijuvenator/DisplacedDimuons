import re
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
from DisplacedDimuons.Common.Utilities import SPStr, SPLumiStr
import DisplacedDimuons.Analysis.HistogramGetter as HistogramGetter
import DisplacedDimuons.Analysis.PlotterParser as PlotterParser

ARGS = PlotterParser.PARSER.parse_args()

TRIGGER   = ARGS.TRIGGER
CUTSTRING = ARGS.CUTSTRING
MCONLY    = ARGS.MCONLY

# get histograms
HISTS = HistogramGetter.getHistograms('../analyzers/roots/Main/DimuonPlots.root')
f = R.TFile.Open('../analyzers/roots/Main/DimuonPlots.root')

# make plots that are per sample
def makePerSamplePlots():
    for ref in HISTS:
        if not type(ref) == tuple: continue
        for key in HISTS[ref]:
            if 'VS' in key: continue
            if type(ref) == tuple:
                if ref[0] == '4Mu':
                    name = 'HTo2XTo4Mu_'
                    latexFS = '4#mu'
                elif ref[0] == '2Mu2J':
                    name = 'HTo2XTo2Mu2J_'
                    latexFS = '2#mu2j'
                if TRIGGER:
                    name = 'Trig-'+name
                name += SPStr(ref[1])
                lumi = SPLumiStr(ref[0], *ref[1])
                legName = HistogramGetter.PLOTCONFIG['HTo2XTo'+ref[0]]['LATEX']
            else:
                if '_Matched' in key: continue
                name = ref
                lumi = HistogramGetter.PLOTCONFIG[ref]['LATEX']
                legName = HistogramGetter.PLOTCONFIG[ref]['LATEX']

            h = HISTS[ref][key].Clone()
            RT.addFlows(h)
            if h.GetNbinsX() > 100: h.Rebin(10)
            p = Plotter.Plot(h, legName, 'l', 'hist')
            fname = 'pdfs/{}{}_{}.pdf'.format(key, CUTSTRING, name)

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
    BGORDER = ('WJets', 'WW', 'WZ', 'ZZ', 'tW', 'tbarW', 'ttbar', 'QCD20toInf-ME', 'DY10to50', 'DY50toInf')
    for hkey in HISTS['DY50toInf']:
        if 'Matched' in hkey: continue
        if 'VS' in hkey: continue

        h = {}
        if not MCONLY:
            h      ['Data'  ] = HISTS['DoubleMuonRun2016B-07Aug17-v2'][hkey].Clone()
        if True:
#           h      ['Signal'] = HISTS[('4Mu', (125, 20, 13))         ][hkey].Clone()
            h      ['BG'    ] = R.THStack('hBG', '')

        PConfig = {}
        if not MCONLY:
            PConfig['Data'  ] = ('DoubleMuon2016'               , 'pe', 'pe'  )
        if True:
#           PConfig['Signal'] = ('H#rightarrow2X#rightarrow4#mu', 'l' , 'hist')
            PConfig['BG'    ] = (''                             , ''  , 'hist')

        PC = HistogramGetter.PLOTCONFIG

        for key in BGORDER:
            h[key] = HISTS[key][hkey].Clone()
            RT.addFlows(h[key])
            if h[key].GetNbinsX() > 100: h[key].Rebin(10)
            h[key].Scale(PC[key]['WEIGHT'])
            PConfig[key] = (PC[key]['LATEX'], 'f', 'hist')
            h['BG'].Add(h[key])

        if not MCONLY:
            for era in ('C', 'D', 'E', 'F', 'G', 'H'):
                h['Data'].Add(HISTS['DoubleMuonRun2016{}-07Aug17'.format(era)][hkey])
            RT.addFlows(h['Data'])
            if h['Data'].GetNbinsX() > 100: h['Data'].Rebin(10)

        p = {}
        for key in h:
            p[key] = Plotter.Plot(h[key], *PConfig[key])

        fname = 'pdfs/{}{}_Stack{}{}{}.pdf'.format(hkey, CUTSTRING, 'MC' if MCONLY else '', '-Log' if logy else '', '-Rat' if DataMC else '')

        for key in BGORDER:
            p[key].setColor(PC[key]['COLOR'], which='LF')

        canvas = Plotter.Canvas(ratioFactor=0. if not DataMC else 1./3., logy=logy, fontscale=1. if not DataMC else 1.+1./3.)
        if True:
            canvas.addMainPlot(p['BG'])
        if not MCONLY:
            canvas.addMainPlot(p['Data'])
#       canvas.addMainPlot(p['Signal'])

        canvas.makeLegend(lWidth=.27, pos='tr', autoOrder=False, fontscale=0.8 if not DataMC else 1.)
        if not MCONLY:
            canvas.addLegendEntry(p['Data'     ])
        for key in reversed(BGORDER):
            canvas.addLegendEntry(p[key])
#       canvas.addLegendEntry(p['Signal'])
        canvas.legend.resizeHeight()

        p['BG'].setTitles(X=p['WJets'].GetXaxis().GetTitle(), Y='Normalized Counts')
        RT.addBinWidth(p['BG'])

        canvas.firstPlot.SetMaximum(h['BG'].GetStack().Last().GetMaximum() * 1.05)
        #canvas.firstPlot.SetMaximum(1.e-4)
        if logy:
            canvas.firstPlot.SetMinimum(1.)

        if DataMC:
            canvas.makeRatioPlot(p['Data'].plot, p['BG'].plot.GetStack().Last())
            canvas.firstPlot.scaleTitleOffsets(0.8, axes='Y')
            canvas.rat      .scaleTitleOffsets(0.8, axes='Y')

#       p['Signal'    ].SetLineStyle(2)
#       p['Signal'    ].SetLineColor(R.kRed)

        canvas.finishCanvas(extrascale=1. if not DataMC else 1.+1./3.)
        canvas.save(fname)
        canvas.deleteCanvas()

# make 3D color plots
def makeColorPlots(key):
    key = 'Dim_' + key

    for ref in HISTS:
        if not type(ref) == tuple: continue
        if type(ref) == tuple:
            if ref[0] == '4Mu':
                name = 'HTo2XTo4Mu_'
                latexFS = '4#mu'
            elif ref[0] == '2Mu2J':
                name = 'HTo2XTo2Mu2J_'
                latexFS = '2#mu2j'
            if TRIGGER:
                name = 'Trig-'+name
            name += SPStr(ref[1])
            lumi = SPLumiStr(ref[0], *ref[1])
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

        fname = 'pdfs/{}{}_{}.pdf'.format(key, CUTSTRING, name)
        canvas.cleanup(fname)

# make split delta phi plots
def makeSplitDeltaPhiPlots():
    for ref in HISTS:
        if not type(ref) == tuple: continue
        for KEY in HISTS[ref]:
            if 'VSdeltaPhi' not in KEY: continue
            if type(ref) == tuple:
                if ref[0] == '4Mu':
                    name = 'HTo2XTo4Mu_'
                    latexFS = '4#mu'
                elif ref[0] == '2Mu2J':
                    name = 'HTo2XTo2Mu2J_'
                    latexFS = '2#mu2j'
                if TRIGGER:
                    name = 'Trig-'+name
                name += SPStr(ref[1])
                lumi = SPLumiStr(ref[0], *ref[1])
            else:
                name = ref
                lumi = HistogramGetter.PLOTCONFIG[ref]['LATEX']
                if '_Matched' in KEY: continue

            H = HISTS[ref][KEY].Clone()
            nBins = H.GetNbinsX()

            h = {
                    'Less' : {'hist': H.ProjectionY('Less', 1        , nBins/2), 'legName' : '|#Delta#Phi|<#pi/2', 'color' : R.kBlue},
                    'More' : {'hist': H.ProjectionY('More', nBins/2+1, nBins  ), 'legName' : '|#Delta#Phi|>#pi/2', 'color' : R.kRed },
            }

            p = {}
            for key in h:
                if h[key]['hist'].Integral() != 0:
                    h[key]['hist'].Scale(1./h[key]['hist'].Integral())
                if nBins > 100: h[key]['hist'].Rebin(10)
                p[key] = Plotter.Plot(h[key]['hist'], h[key]['legName'], 'l', 'hist')

            canvas = Plotter.Canvas(lumi=lumi)
            for key in h:
                canvas.addMainPlot(p[key])
                p[key].SetLineColor(h[key]['color'])
            canvas.makeLegend(pos='tl')
            canvas.legend.resizeHeight()
            canvas.setMaximum(recompute=True)
            canvas.firstPlot.setTitles(Y='Normalized Counts')

            pave = []
            for key in h:
                pave.append(canvas.makeStatsBox(p[key], color=h[key]['color']))
            for i, box in enumerate(pave):
                if i == 0: continue
                HEIGHT = pave[i-1].GetY2NDC() - pave[i-1].GetY1NDC()
                Plotter.MOVE_OBJECT(box, Y=-HEIGHT-.05)

            parse = re.match(r'Dim_(.*)VSdeltaPhi(.*)', KEY)
            yAxis, other = parse.group(1), parse.group(2)
            fname = 'pdfs/Dim_{}{}{}_Both_{}.pdf'.format(yAxis, other, CUTSTRING, name)
            canvas.cleanup(fname)

# make split delta phi plots
# this function is a combination of the stack plot code and the split delta phi code
def makeSplitDeltaPhiStackPlots(logy=False):
    BGORDER = ('WJets', 'WW', 'WZ', 'ZZ', 'tW', 'tbarW', 'ttbar', 'QCD20toInf-ME', 'DY10to50', 'DY50toInf')
    for hkey in HISTS['DY50toInf']:
        if 'Matched' in hkey: continue
        if 'VSdeltaPhi' not in hkey: continue

        h = {}
        for DeltaPhiRange in ('Less', 'More'):
            h[DeltaPhiRange] = {
                'BG' : R.THStack('hBG_'+DeltaPhiRange, '')
            }

        PConfig = {
            'BG' : ('', '', 'hist'),
        }

        PC = HistogramGetter.PLOTCONFIG

        for key in BGORDER:
            H = HISTS[key][hkey].Clone()
            nBins = H.GetNbinsX()

            h['Less'][key] = H.ProjectionY(key+'_Less', 1        , nBins/2)
            h['More'][key] = H.ProjectionY(key+'_More', nBins/2+1, nBins  )

            for DeltaPhiRange in ('Less', 'More'):
                h[DeltaPhiRange][key].Scale(PC[key]['WEIGHT'])
                if h[DeltaPhiRange][key].GetNbinsX() > 100: h[DeltaPhiRange][key].Rebin(10)
                h[DeltaPhiRange]['BG'].Add(h[DeltaPhiRange][key])

            PConfig[key] = (PC[key]['LATEX'], 'f', 'hist')

        # make less, more
        p = {}
        for DeltaPhiRange in ('Less', 'More'):
            p[DeltaPhiRange] = {}
            for key in h['Less']:
                p[DeltaPhiRange][key] = Plotter.Plot(h[DeltaPhiRange][key], *PConfig[key])

            for key in BGORDER:
                p[DeltaPhiRange][key].setColor(PC[key]['COLOR'], which='LF')

            canvas = Plotter.Canvas(logy=logy)
            canvas.addMainPlot(p[DeltaPhiRange]['BG'])

            canvas.makeLegend(lWidth=.27, pos='tr', autoOrder=False)
            for key in reversed(BGORDER):
                canvas.addLegendEntry(p[DeltaPhiRange][key])
            canvas.legend.resizeHeight()

            p[DeltaPhiRange]['BG'].setTitles(X=p[DeltaPhiRange]['WJets'].GetXaxis().GetTitle(), Y='Normalized Counts')
            RT.addBinWidth(p[DeltaPhiRange]['BG'])

            realMax = 0.
            dh = h[DeltaPhiRange]['BG'].GetStack().Last()
            for ibin in xrange(1, dh.GetNbinsX()+1):
                if dh.GetBinContent(ibin) > realMax:
                    realMax = dh.GetBinContent(ibin)
            canvas.firstPlot.SetMaximum(1.05 * realMax)

            parse = re.match(r'Dim_(.*)VSdeltaPhi(.*)', hkey)
            yAxis, other = parse.group(1), parse.group(2)
            fname = 'pdfs/Dim_{}{}{}{}_StackMC{}.pdf'.format(yAxis, other, CUTSTRING, '_'+DeltaPhiRange, '-Log' if logy else '')
            canvas.cleanup(fname)

        # make both, using the Last(), and ratio
        hLast = {}
        LastConfig = {
            'Less' : {'legName' : '|#Delta#Phi|<#pi/2', 'color' : R.kBlue},
            'More' : {'legName' : '|#Delta#Phi|>#pi/2', 'color' : R.kRed },
        }
        for DeltaPhiRange in ('Less', 'More'):
            hLast[DeltaPhiRange] = h[DeltaPhiRange]['BG'].GetStack().Last()
            p[DeltaPhiRange]['Last'] = Plotter.Plot(hLast[DeltaPhiRange], LastConfig[DeltaPhiRange]['legName'], 'l', 'hist')

        for makeRatio in (False, True):
            canvas = Plotter.Canvas(ratioFactor=0. if not makeRatio else 1./3., logy=logy, fontscale=1. if not makeRatio else 1.+1./3.)

            canvas.addMainPlot(p['Less']['Last'])
            canvas.addMainPlot(p['More']['Last'])

            for DeltaPhiRange in ('Less', 'More'):
                p[DeltaPhiRange]['Last'].SetLineColor(LastConfig[DeltaPhiRange]['color'])

            canvas.firstPlot.setTitles(Y='Normalized Counts')
            RT.addBinWidth(canvas.firstPlot)

            canvas.makeLegend(pos='tl')
            canvas.legend.resizeHeight()
            canvas.setMaximum(recompute=True)

            if makeRatio:
                canvas.makeRatioPlot(p['Less']['Last'], p['More']['Last'], ytit='Less/Greater')
                canvas.firstPlot.scaleTitleOffsets(0.8, axes='Y')
                canvas.rat      .scaleTitleOffsets(0.8, axes='Y')
            canvas.mainPad.cd()

            pave = []
            for DeltaPhiRange in ('Less', 'More'):
                pave.append(canvas.makeStatsBox(p[DeltaPhiRange]['Last'], color=LastConfig[DeltaPhiRange]['color']))
            for i, box in enumerate(pave):
                if i == 0: continue
                HEIGHT = pave[i-1].GetY2NDC() - pave[i-1].GetY1NDC()
                Plotter.MOVE_OBJECT(box, Y=-HEIGHT-.05)

            parse = re.match(r'Dim_(.*)VSdeltaPhi(.*)', hkey)
            yAxis, other = parse.group(1), parse.group(2)
            fname = 'pdfs/Dim_{}{}{}_Both{}_StackMC{}.pdf'.format(yAxis, other, CUTSTRING, '' if not makeRatio else 'Rat', '-Log' if logy else '')
            canvas.cleanup(fname)

def makeOverlaidPlot():
    REFLIST = (('2Mu2J', (1000, 20, 2)), ('2Mu2J', (200, 50, 200)))
    key = 'Dim_deltaPhi_Matched'

    h = {
        REFLIST[0] : HISTS[REFLIST[0]][key].Clone(),
        REFLIST[1] : HISTS[REFLIST[1]][key].Clone(),
    }

    p = {}
    for ref in h:
        RT.addFlows(h[ref])
        if h[ref].GetNbinsX() > 100: h[ref].Rebin(10)
        p[ref] = Plotter.Plot(h[ref], '2#mu2j ({}, {}, {})'.format(*ref[1]), 'l', 'hist')

    fname = 'pdfs/{}{}_Overlaid.pdf'.format(key, CUTSTRING)

    canvas = Plotter.Canvas()
    canvas.addMainPlot(p[REFLIST[1]])
    canvas.addMainPlot(p[REFLIST[0]])
    canvas.makeLegend(lWidth=.25, pos='tl')
    #canvas.legend.moveLegend(Y=-.3)
    canvas.legend.resizeHeight()
    p[REFLIST[1]].SetLineColor(R.kBlue)
    p[REFLIST[0]].SetLineColor(R.kRed )
    RT.addBinWidth(canvas.firstPlot)

    pave1 = canvas.makeStatsBox(p[REFLIST[1]], color=R.kBlue)
    pave2 = canvas.makeStatsBox(p[REFLIST[0]], color=R.kRed )
    Plotter.MOVE_OBJECT(pave2, Y=-.22, NDC=False)
    canvas.cleanup(fname)

# This is now a heavy process that gets killed if everything runs at once
# So run in pieces
if True:
    makePerSamplePlots()
if True:
    makeStackPlots(False, False)
    if not MCONLY:
        makeStackPlots(True, True)
    else:
        makeStackPlots(False, True)
    makeSplitDeltaPhiStackPlots()
    makeSplitDeltaPhiStackPlots(True)
if True:
    for q1 in ('Lxy', 'LxySig', 'LxyErr', 'deltaR', 'deltaEta', 'deltaphi', 'mass'):
        for q2 in ('Lxy', 'deltaPhi'):
            if q1 == q2: continue
            if q1 == 'mass' and q2 == 'Lxy': continue
            key = q1 + 'VS' + q2
            makeColorPlots(key)
            makeColorPlots(key+'_Matched')
if True:
    makeSplitDeltaPhiPlots()

# special purpose overlaid plot
#makeOverlaidPlot()
