import re
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
from DisplacedDimuons.Common.Utilities import SPStr, SPLumiStr
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
import DisplacedDimuons.Analysis.HistogramGetter as HistogramGetter
import DisplacedDimuons.Analysis.PlotterParser as PlotterParser

PlotterParser.PARSER.add_argument('--fs', dest='FS', default='2Mu2J', help='which final state to run')
ARGS = PlotterParser.PARSER.parse_args()

f = R.TFile.Open('roots/Main/pairingCriteriaPlots_Trig_HTo2XTo{}.root'.format(ARGS.FS))

def makePTCutPlot(fs, sp=None):
    # configy type stuff
    tags=['nMatch'    , 'nCorrectChi2'              , 'nCorrectPT'         , 'nCorrectPTOC'              , 'nCorrectPTChi2'    ]
    legs=['N(matched)', 'N(correct by #chi^{2}/dof)', 'N(correct by p_{T})', 'N(correct by p_{T} & o.c.)', 'N(correct HPD+LCD)']
    cols=[R.kRed       , R.kBlue                    , R.kGreen             , R.kMagenta                  , R.kOrange           ]

    if ARGS.FS == '2Mu2J':
        tags = tags[:-2]
        legs = legs[:-2]
        cols = cols[:-2]

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
    tags=['nMatch'     , 'nCorrectChi2'                , 'nCorrectPT'           , 'nCorrectPTOC'               , 'nCorrectPTChi2'    ]
    legs=['signal eff.', 'correct by #chi^{2}/dof eff.', 'correct by p_{T} eff.', 'correct by p_{T} & o.c. eff', 'correct by HPD+LCD']
    cols=[R.kRed       , R.kBlue                      , R.kGreen                , R.kMagenta                   , R.kOrange           ]

    if ARGS.FS == '2Mu2J':
        tags = tags[:-2]
        legs = legs[:-2]
        cols = cols[:-2]

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
    canvas.firstPlot.SetMinimum(0.90 if ARGS.FS == '2Mu2J' else 0.50)
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
    if ARGS.FS == '4Mu': return

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

ORDER = [
    (1000, 350, 3500),
    (1000, 350,  350),
    (1000, 350,   35),
    (1000, 150, 1000),
    (1000, 150,  100),
    (1000, 150,   10),
    (1000,  50,  400),
    (1000,  50,   40),
    (1000,  50,    4),
    (1000,  20,  200),
    (1000,  20,   20),
    (1000,  20,    2),
    ( 400, 150, 4000),
    ( 400, 150,  400),
    ( 400, 150,   40),
    ( 400,  50,  800),
    ( 400,  50,   80),
    ( 400,  50,    8),
    ( 400,  20,  400),
    ( 400,  20,   40),
    ( 400,  20,    4),
    ( 200,  50, 2000),
    ( 200,  50,  200),
    ( 200,  50,   20),
    ( 200,  20,  700),
    ( 200,  20,   70),
    ( 200,  20,    7),
    ( 125,  50, 5000),
    ( 125,  50,  500),
    ( 125,  50,   50),
    ( 125,  20, 1300),
    ( 125,  20,  130),
    ( 125,  20,   13),
]

CUTS = (0, 5, 10, 15)
#CUTS = (15, 10, 5, 0)
PRETTY = {i:str(i)+' GeV' for i in CUTS}
PRETTY[0] = 'no cut'
#COLORS = {0:R.kRed, 5:R.kBlue, 10:R.kGreen, 15:R.kMagenta}
#COLORS = {0:R.kRed, 5:R.kRed+1, 10:R.kRed+2, 15:R.kRed+3}
#COLORS = {0:R.kWhite, 5:R.kGray, 10:R.kGray+1, 15:R.kGray+2}
COLORS = {0:R.kWhite, 5:R.kRed, 10:R.kRed+2, 15:R.kRed+4}
LINES = [12, 21, 27]
DASHED = [3, 6, 9, 15, 18, 24, 30]
def makeSummaryPlot(fs, quantity='Match', reverseCuts=False):
    DATA = {'2Mu2J':{}, '4Mu':{}}
    for sp in SIGNALPOINTS:
        DATA[fs][sp] = {i:0 for i in CUTS}
        if quantity == 'Match':
            h = HistogramGetter.getHistogram(f, (fs, sp), 'nMatch').Clone()
            h.Scale(1./h.GetBinContent(1))
        else:
            h = HistogramGetter.getHistogram(f, (fs, sp), 'n'+quantity).Clone()
            hDen = HistogramGetter.getHistogram(f, (fs, sp), 'nMatch').Clone()
            h.Divide(hDen)
        for CUT in CUTS:
            ibin = CUT+1
            DATA[fs][sp][CUT] = h.GetBinContent(ibin)
    h = {}
    p = {}
    for CUT in CUTS:
        h[CUT] = R.TH1F('h'+str(CUT)+fs+quantity, ';;Signal Efficiency', 33, 0., 33.)
        for i,sp in enumerate(ORDER):
            h[CUT].SetBinContent(i+1, DATA[fs][sp][CUT])
        p[CUT] = Plotter.Plot(h[CUT], PRETTY[CUT], 'l', 'hist')

    canvas = Plotter.Canvas(lumi='(each 3 = c#tau decreasing from left to right)    ' + fs)
    REALCUTS = CUTS if not reverseCuts else list(reversed(CUTS))
    for CUT in REALCUTS:
        canvas.addMainPlot(p[CUT])
        p[CUT].setColor(COLORS[CUT], which='LF')

    canvas.makeLegend(lWidth=.15, pos='bl')

    canvas.legend.SetFillStyle(1001)
    canvas.legend.SetFillColor(R.kWhite)
    canvas.legend.SetBorderSize(1)

    ymin, ymax = 0.8, 1.
    if quantity == 'CorrectChi2' or quantity == 'CorrectPTChi2': ymin = 0.
    if fs == '4Mu' and quantity == 'Match': ymin = 0.5
    canvas.firstPlot.SetMaximum(ymax)
    canvas.firstPlot.SetMinimum(ymin)

    canvas.firstPlot.SetNdivisions(33)
    canvas.firstPlot.GetXaxis().SetLabelSize(0)

    # mainPad lines
    lines = []
    for line in LINES:
        lines.append(R.TLine(line, ymin, line, ymax))
        lines[-1].Draw()
    for line in DASHED:
        lines.append(R.TLine(line, ymin, line, ymax))
        lines[-1].SetLineStyle(2)
        lines[-1].Draw()

    canvas.cd()

    # mH labels
    canvas.drawText(text='m_{H} [GeV]', align='cl', pos=(0, .04))
    start = .16
    step = .073
    canvas.drawText(text='1000', align='cc', pos=(start+step*(1+0.5), .04))
    canvas.drawText(text='400' , align='cc', pos=(start+step*(5+0.0), .04))
    canvas.drawText(text='200' , align='cc', pos=(start+step*(7+0.5), .04))
    canvas.drawText(text='125' , align='cc', pos=(start+step*(9+0.5), .04))

    # mX labels
    canvas.drawText(text='m_{X} [GeV]', align='cl', pos=(0, .08))
    start = .16
    canvas.drawText(text='350' , align='cc', pos=(start+step*0 , .08))
    canvas.drawText(text='150' , align='cc', pos=(start+step*1 , .08))
    canvas.drawText(text='50'  , align='cc', pos=(start+step*2 , .08))
    canvas.drawText(text='20'  , align='cc', pos=(start+step*3 , .08))

    canvas.drawText(text='150' , align='cc', pos=(start+step*4 , .08))
    canvas.drawText(text='50'  , align='cc', pos=(start+step*5 , .08))
    canvas.drawText(text='20'  , align='cc', pos=(start+step*6 , .08))

    canvas.drawText(text='50'  , align='cc', pos=(start+step*7 , .08))
    canvas.drawText(text='20'  , align='cc', pos=(start+step*8 , .08))

    canvas.drawText(text='50'  , align='cc', pos=(start+step*9 , .08))
    canvas.drawText(text='20'  , align='cc', pos=(start+step*10, .08))

    # custom modifications to cleanup
    canvas.cleanup('pdfs/PC_{}EffSummary_HTo2XTo{}_Global.pdf'.format(quantity, fs))

for fs in (ARGS.FS,):
    for sp in [None] + SIGNALPOINTS:
        makePTCutPlot(fs, sp)
        makePTCutEffPlot(fs, sp)
        makeMultiplicityPlots(fs, sp)
    if True:
        makeSummaryPlot(fs, quantity='Match'        , reverseCuts=False)
    if fs == '4Mu':
        makeSummaryPlot(fs, quantity='CorrectChi2'  , reverseCuts=True )
        makeSummaryPlot(fs, quantity='CorrectPTOC'  , reverseCuts=True )
        makeSummaryPlot(fs, quantity='CorrectPTChi2', reverseCuts=True )
