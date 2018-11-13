import re
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
from DisplacedDimuons.Common.Utilities import SPStr, SPLumiStr
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
import DisplacedDimuons.Analysis.HistogramGetter as HistogramGetter
import DisplacedDimuons.Analysis.PlotterParser as PlotterParser

f = R.TFile.Open('../analyzers/roots/pairingCriteriaPlots_Trig_HTo2XTo2Mu2J.root')

def makePTCutPlot(fs, sp=None):
    # configy type stuff
    tags=('nMatch'    , 'nCorrectChi2'              , 'nCorrectPT'         )
    legs=('N(matched)', 'N(correct by #chi^{2}/dof)', 'N(correct by p_{T})')
    cols=(R.kRed       , R.kBlue                    , R.kGreen             )

    # get/add histograms
    if sp is None:
        h = {}
        for tag in tags:
            h[tag] = HistogramGetter.getHistogram(f, (fs, SIGNALPOINTS[0]), tag).Clone()
        for SP in SIGNALPOINTS[1:]:
            for tag in tags:
                h[tag].Add(HistogramGetter.getHistogram(f, (fs, SP), tag))
    else:
        h = {}
        for tag in tags:
            h[tag] = HistogramGetter.getHistogram(f, (fs, sp), tag).Clone()

    # make plots
    p = {}
    for i,tag in enumerate(tags):
        p[tag] = Plotter.Plot(h[tag], legs[i], 'l', 'hist')

    # canvas, plots, min max
    canvas = Plotter.Canvas(lumi=SPLumiStr(fs, sp) if sp is not None else fs)
    for tag in tags:
        canvas.addMainPlot(p[tag])
    canvas.setMaximum()
    canvas.setMinimum()

    # colors
    for i,tag in enumerate(tags):
        p[tag].SetLineColor(cols[i])

    # legend, cleanup
    canvas.makeLegend(lWidth=.275, pos='tr')
    canvas.legend.resizeHeight()

    canvas.cleanup('pdfs/PC_Match_HTo2XTo{}_{}.pdf'.format(fs, SPStr(sp) if sp is not None else 'Global'))

def makePTCutEffPlot(fs, sp=None):
    # configy type stuff
    tags=('nMatch'     , 'nCorrectChi2'                , 'nCorrectPT'           )
    legs=('signal eff.', 'correct by #chi^{2}/dof eff.', 'correct by p_{T} eff.')
    cols=(R.kRed       , R.kBlue                      , R.kGreen                )

    # get/add histograms
    if sp is None:
        h = {}
        for tag in tags:
            h[tag] = HistogramGetter.getHistogram(f, (fs, SIGNALPOINTS[0]), tag).Clone()
        for SP in SIGNALPOINTS[1:]:
            for tag in tags:
                h[tag].Add(HistogramGetter.getHistogram(f, (fs, SP), tag))
    else:
        h = {}
        for tag in tags:
            h[tag] = HistogramGetter.getHistogram(f, (fs, sp), tag).Clone()

    # clone everything, the h is about to be overwritten
    copies = {}
    for tag in tags:
        copies[tag] = h[tag].Clone()

    # nMatch: scale to first bin (gives ~efficiency)
    # others: divide by nMatch
    h['nMatch'].Scale(1./copies['nMatch'].GetBinContent(1))
    for tag in tags[1:]:
        h[tag] = R.TGraphAsymmErrors(copies[tag], copies['nMatch'], 'cp')

    # make plots
    p = {}
    for i,tag in enumerate(tags):
        p[tag] = Plotter.Plot(h[tag], legs[i], 'p', 'p'+('' if i==0 else 'x'))

    # it's an efficiency so the scale is 0-1, but zoom in on the relevant part
    canvas = Plotter.Canvas(lumi=SPLumiStr(fs, sp) if sp is not None else fs)
    for tag in tags:
        canvas.addMainPlot(p[tag])
    canvas.firstPlot.SetMaximum(1.01)
    canvas.firstPlot.SetMinimum(0.90)
    #canvas.setMaximum()
    #canvas.setMinimum()

    # set colors
    for i,tag in enumerate(tags):
        p[tag].setColor(cols[i])

    # legend, cleanup
    canvas.makeLegend(lWidth=.275, pos='br')
    canvas.legend.resizeHeight()
    # hack for getting the legend in the right spot for 1000 and 400, as it turns out
    if sp is not None and sp[0] > 399:
        canvas.legend.moveLegend(X=-.35)
    else:
        canvas.legend.moveLegend(Y=.2)

    canvas.cleanup('pdfs/PC_MatchEff_HTo2XTo{}_{}.pdf'.format(fs, SPStr(sp) if sp is not None else 'Global'))

def makeMultiplicityPlots(fs, sp):
    # configy type stuff
    pTCuts = (0, 5, 10, 15)
    splits = ('_', '_Matched_', '_NotMatched_')
    prettysplits = {'_':'', '_Matched_':' (Matched)', '_NotMatched_':' (Junk)'}
    quants = ('Muon', 'Dimuon')

    for q in quants:
        for split in splits:
            for logy in (True, False):
                tags = []
                legs = []
                cols = [R.kRed, R.kBlue, R.kGreen, R.kMagenta]
                for pTCut in pTCuts:
                    tags.append('n{}{}{}'.format(q, split, pTCut))
                    legs.append('{} GeV'.format(pTCut) if pTCut > 0 else 'no cut')

                # the code after this is identical to the makePTCutPlot code, except for the lumi string, min/max, and cleanup
                if sp is None:
                    h = {}
                    for tag in tags:
                        h[tag] = HistogramGetter.getHistogram(f, (fs, SIGNALPOINTS[0]), tag).Clone()
                    for SP in SIGNALPOINTS[1:]:
                        for tag in tags:
                            h[tag].Add(HistogramGetter.getHistogram(f, (fs, SP), tag))
                else:
                    h = {}
                    for tag in tags:
                        h[tag] = HistogramGetter.getHistogram(f, (fs, sp), tag).Clone()

                p = {}
                for i,tag in enumerate(tags):
                    p[tag] = Plotter.Plot(h[tag], legs[i], 'l', 'hist')

                canvas = Plotter.Canvas(lumi=(SPLumiStr(fs, sp) if sp is not None else fs)+prettysplits[split], logy=logy)
                for tag in tags:
                    canvas.addMainPlot(p[tag])
                if logy:
                    canvas.setMaximum(scale=2.)
                    canvas.firstPlot.SetMinimum(1.)
                else:
                    canvas.setMaximum()
                    canvas.firstPlot.SetMinimum(0.)

                for i,tag in enumerate(tags):
                    p[tag].SetLineColor(cols[i])

                canvas.makeLegend(lWidth=.25, pos='tr')
                canvas.legend.resizeHeight()

                canvas.cleanup('pdfs/PC_{}Mult{}{}HTo2XTo{}_{}.pdf'.format(q, split, 'Log_' if logy else '', fs, SPStr(sp) if sp is not None else 'Global'))

for fs in ('2Mu2J',):
    for sp in [None] + SIGNALPOINTS:
        makePTCutPlot(fs, sp)
        makePTCutEffPlot(fs, sp)
        makeMultiplicityPlots(fs, sp)
