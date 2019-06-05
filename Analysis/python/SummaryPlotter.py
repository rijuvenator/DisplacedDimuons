import re
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
from DisplacedDimuons.Common.Constants import SIGNALPOINTS

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

def initializeData():
    DATA = {'2Mu2J':{}, '4Mu':{}}
    for sp in SIGNALPOINTS:
        for fs in DATA:
            DATA[fs][sp] = {}
    return DATA

COLORS = {0:R.kWhite, 5:R.kRed, 10:R.kRed+2, 15:R.kRed+4}
LINES = [12, 21, 27]
DASHED = [3, 6, 9, 15, 18, 24, 30]
def makeSummaryPlot(
    DATA,
    fs,
    KEYS,
    TITLE,
    PRETTY,
    COLORS,
    YLIMS,
    FNAME,
    LEGPOS='bl',
    LOGY=False,
    LEGWIDTH=0.15,
    ):

    h = {}
    p = {}
    for KEY in KEYS:
        h[KEY] = R.TH1F('h'+str(KEY), TITLE, 33, 0., 33.)
        for i, sp in enumerate(ORDER):
            h[KEY].SetBinContent(i+1, DATA[fs][sp][KEY])
        p[KEY] = Plotter.Plot(h[KEY], PRETTY[KEY], 'l', 'hist')

    canvas = Plotter.Canvas(lumi='(each 3 = c#tau decreasing from left to right)    ' + fs, logy=LOGY)
    for KEY in KEYS:
        canvas.addMainPlot(p[KEY])
        p[KEY].setColor(COLORS[KEY], which='LF')

    DRAWLEGEND = len(KEYS) > 1

    if DRAWLEGEND:
        canvas.makeLegend(lWidth=LEGWIDTH, pos=LEGPOS)
        canvas.legend.SetFillStyle(1001)
        canvas.legend.SetFillColor(R.kWhite)
        canvas.legend.SetBorderSize(1)
        canvas.legend.resizeHeight(scale=1.1)

    ymin, ymax = YLIMS['min'], YLIMS['max']
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
    canvas.cleanup(FNAME)
