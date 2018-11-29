import re
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
from DisplacedDimuons.Common.Utilities import SPStr, SPLumiStr
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
import DisplacedDimuons.Analysis.HistogramGetter as HistogramGetter
import DisplacedDimuons.Analysis.PlotterParser as PlotterParser

ARGS = PlotterParser.PARSER.parse_args()
f = R.TFile.Open('roots/Main/3MuPlots_Trig{}_HTo2XTo4Mu.root'.format(ARGS.CUTSTRING))

QUANTITIES = []
for Q in ('Lxy', 'chi2'):
    for crit in ('LCD', 'LCD-OC', 'HPD', 'HPD-OC'):
        QUANTITIES.append('{}_{}'.format(Q, crit))

def makeEffPlot(quantity, den, fs, sp=None):
    tags = (quantity+'_MSD', quantity+'_LCD', quantity+'_CID')

    effTag = quantity+'_CID'

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

    hNum = h[quantity+'_CID']
    h[quantity+'_'+den].Add(h[quantity+'_CID'])
    hDen = h[quantity+'_'+den]

    graph = R.TGraphAsymmErrors(hNum, hDen, 'cp')

    # make plots
    p = Plotter.Plot(graph, '', 'l', 'px')

    # canvas, plots, min max
    canvas = Plotter.Canvas(lumi=SPLumiStr(fs, sp) if sp is not None else fs)
    canvas.addMainPlot(p)
    canvas.setMaximum()
    canvas.firstPlot.SetMinimum(0)

    # set titles
    canvas.firstPlot.setTitles(X=hNum.GetXaxis().GetTitle(), Y='Efficiency')

    # colors
    p.setColor(R.kBlue, which='M')

    # legend, cleanup
    #canvas.makeLegend(lWidth=.2, pos='tr')
    #canvas.legend.resizeHeight()

    canvas.cleanup('pdfs/3Mu_{}Eff-{}{}_HTo2XTo{}_{}.pdf'.format(quantity, den, ARGS.CUTSTRING, fs, SPStr(sp) if sp is not None else 'Global'))

def makeSplit4Plot(quantity, fs, sp=None):
    tags = [quantity+'_'+tag for tag in ('CID', 'MSD', 'LCD', 'UMD')]
    legs = dict(zip(tags, ('correct', 'signal', 'lowest #chi^{2}/dof', 'unmatched')))
    cols = dict(zip(tags, (R.kBlue, R.kGreen, R.kMagenta, R.kRed)))

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
    for tag in tags:
        p[tag] = Plotter.Plot(h[tag], legs[tag], 'l', 'hist')

    # canvas, plots, min max
    canvas = Plotter.Canvas(lumi=SPLumiStr(fs, sp) if sp is not None else fs, logy=True)
    for tag in tags:
        canvas.addMainPlot(p[tag])
    canvas.setMaximum(scale=2.)
    canvas.firstPlot.SetMinimum(1.)

    # colors
    for tag in tags:
        p[tag].setColor(cols[tag], which='L')

    # legend, cleanup
    canvas.makeLegend(lWidth=.2, pos='tr')
    canvas.legend.resizeHeight()

    canvas.cleanup('pdfs/3Mu_{}Dist{}_HTo2XTo{}_{}.pdf'.format(quantity, ARGS.CUTSTRING, fs, SPStr(sp) if sp is not None else 'Global'))

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

TAGS = ('3MuT', '3Mu34', '1M', 'LP')
LEGS = ('3+4#mu/trig.', '3#mu>5GeV/3+4#mu', '1 match/3#mu>5GeV', 'LCD=HPD/match')
COLS = (R.kBlack, R.kBlue, R.kRed, R.kGreen)
PRETTY = dict(zip(TAGS, LEGS))
COLORS = dict(zip(TAGS, COLS))
PROGRAM = {
    '3MuT' :{'num':(1, 2), 'den':(0,  )},
    '3Mu34':{'num':(3, 4), 'den':(1, 2)},
    '1M'   :{'num':(6,  ), 'den':(3, 4)},
    'LP'   :{'num':(7,  ), 'den':(6,  )},
}
LINES = [12, 21, 27]
DASHED = [3, 6, 9, 15, 18, 24, 30]
def makeSummaryPlot(fs):
    DATA = {'2Mu2J':{}, '4Mu':{}}
    for sp in SIGNALPOINTS:
        DATA[fs][sp] = {i:0 for i in TAGS}
        h = HistogramGetter.getHistogram(f, (fs, sp), 'counters').Clone()
        contents = [h.GetBinContent(i) for i in range(1,9)]
        for TAG in TAGS:
            DATA[fs][sp][TAG] = sum([contents[i] for i in PROGRAM[TAG]['num']])/sum([contents[i] for i in PROGRAM[TAG]['den']])
    h = {}
    p = {}
    for TAG in TAGS:
        h[TAG] = R.TH1F('h'+str(TAG)+fs, ';;Efficiency', 33, 0., 33.)
        for i,sp in enumerate(ORDER):
            h[TAG].SetBinContent(i+1, DATA[fs][sp][TAG])
        p[TAG] = Plotter.Plot(h[TAG], PRETTY[TAG], 'l', 'hist')

    canvas = Plotter.Canvas(lumi='(each 3 = c#tau decreasing from left to right)    ' + fs)
    for TAG in TAGS:
        canvas.addMainPlot(p[TAG])
        p[TAG].setColor(COLORS[TAG], which='L')

    canvas.makeLegend(lWidth=.25, pos='bl')
    canvas.legend.SetMargin(canvas.legend.GetMargin()*0.5)

    canvas.legend.SetFillStyle(1001)
    canvas.legend.SetFillColor(R.kWhite)
    canvas.legend.SetBorderSize(1)

    ymin, ymax = 0., 1.
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
    canvas.cleanup('pdfs/3Mu_MatchEffSummary_HTo2XTo{}_Global.pdf'.format(fs))

for fs in ('4Mu',):
    #for sp in [None] + SIGNALPOINTS:
    for sp in [None]:
        for quantity in QUANTITIES:
            makeEffPlot(quantity, 'MSD', fs, sp)
            makeEffPlot(quantity, 'LCD', fs, sp)
            makeSplit4Plot(quantity, fs, sp)
    makeSummaryPlot(fs)
