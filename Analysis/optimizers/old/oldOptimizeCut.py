import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
from DisplacedDimuons.Common.Utilities import SPStr, SPLumiStr
import DisplacedDimuons.Analysis.AnalysisTools as AT

R.gStyle.SetPadTickY(0)

DATA = {'2Mu2J':{}, '4Mu':{}}

f = R.TFile.Open('../analyzers/roots/DimuonQualityStudies_Trig_HTo2XTo2Mu2J.root')

def FOM(s, b):
    if (s+b) < 1.e-10: return 0
    return s/((s+b)**0.5)

def getHistogram(f, fs, sp, quantity, which):
    return f.Get(quantity+'_'+which+'_HTo2XTo'+fs+'_'+SPStr(sp)).Clone()

def optimizeCut(fs, sp, quantity):
    # get histograms
    s = getHistogram(f, fs, sp, quantity, 'Matched')
    b = getHistogram(f, fs, sp, quantity, 'Junk'   )

    # get cumulatives
    sCum = s.GetCumulative()
    bCum = b.GetCumulative()
    fom  = sCum.Clone()

    # print out suppression
    nBins = sCum.GetNbinsX()
    if quantity == 'LxyErr':
        ibin = 200
    else:
        ibin = 660
    srej = 1.-sCum.GetBinContent(ibin)/sCum.GetBinContent(nBins)
    brej = 1.-bCum.GetBinContent(ibin)/bCum.GetBinContent(nBins)
    #print '{:5s} {:4d} {:3d} {:4d} :: {:6s} :: reject {:6.2%} of signal, but {:6.2%} of background'.format(
    #        fs,
    #        sp[0], sp[1], sp[2],
    #        quantity,
    #        1.-sCum.GetBinContent(ibin)/sCum.GetBinContent(nBins),
    #        1.-bCum.GetBinContent(ibin)/bCum.GetBinContent(nBins),
    #)

    # fill f.o.m. histogram, and keep track of max f.o.m. and cut value
    nBins = sCum.GetNbinsX()
    xAxis = sCum.GetXaxis()
    fom_max = 0.
    opt_cut = 0.
    for ibin in range(1,nBins+1):
        val = FOM(sCum.GetBinContent(ibin), bCum.GetBinContent(ibin))
        if val > fom_max:
            fom_max = val
            opt_cut = xAxis.GetBinCenter(ibin)
        fom.SetBinContent(ibin, val)

    # make plots
    p = {}
    p['sig'] = Plotter.Plot(sCum, 'matched'     , 'l', 'hist')
    p['bg' ] = Plotter.Plot(bCum, 'other'       , 'l', 'hist')
    p['fom'] = Plotter.Plot(fom , 'S/#sqrt{S+B}', 'l', 'hist')

    # make canvas, colors, maximum
    canvas = Plotter.Canvas(lumi=SPLumiStr(fs, *sp))
    canvas.addMainPlot(p['sig'])
    canvas.addMainPlot(p['bg' ])
    canvas.addMainPlot(p['fom'])

    p['sig'].SetLineColor(R.kBlue )
    p['bg' ].SetLineColor(R.kRed  )
    p['fom'].SetLineColor(R.kGreen)

    canvas.setMaximum()

    # scale f.o.m. and make new axis
    fom.Scale(canvas.firstPlot.GetMaximum()/fom_max/1.05)
    axis = R.TGaxis(xAxis.GetXmax(), 0., xAxis.GetXmax(), canvas.firstPlot.GetMaximum(), 0., fom_max*1.05, 510, '+L')
    for attr in ('LabelFont', 'LabelOffset', 'TitleFont', 'TitleOffset', 'TitleSize'):
        getattr(axis, 'Set'+attr)(getattr(xAxis, 'Get'+attr)())
    axis.SetTitle('Figure of Merit')
    axis.CenterTitle()
    axis.Draw()
    canvas.scaleMargins(1.1, edges='R')

    # make the legend after
    canvas.makeLegend(lWidth=.2, pos='br')
    canvas.legend.resizeHeight()

    # draw optimum text and line
    x, y = canvas.legend.GetX1(), canvas.legend.GetY2()
    canvas.drawText(text='#color[{:d}]{{opt. cut = {:.2f}}}'.format(R.kBlack, opt_cut), pos=(x, y+0.05), align='bl')

    line = R.TLine(opt_cut, 0., opt_cut, canvas.firstPlot.GetMaximum())
    line.SetLineStyle(2)
    line.Draw()

    # save
    canvas.cleanup('OPT_{}_HTo2XTo{}_{}.pdf'.format(quantity, fs, SPStr(sp)))

    # save cut val
    if sp not in DATA[fs]: DATA[fs][sp] = {}
    if quantity not in DATA[fs][sp]: DATA[fs][sp][quantity] = {
        'opt':0,
        'srej':0,
        'brej':0,
    }
    DATA[fs][sp][quantity]['opt'] = opt_cut
    DATA[fs][sp][quantity]['srej'] = srej
    DATA[fs][sp][quantity]['brej'] = brej

for fs in ('2Mu2J',):
    #for sp in SIGNALPOINTS:
    for sp in SIGNALPOINTS:
        for quantity in ('LxyErr', 'deltaR'):
            optimizeCut(fs, sp, quantity)

##########

R.gStyle.SetPadTickY(1)

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

PRETTY = {'LxyErr':'#sigma_{L_{xy}} [cm]', 'deltaR':'#DeltaR(#mu#mu)', 'opt':'Optimal Cut Value', 'srej':'Signal Rejection', 'brej':'Background Rejection'}
PARAMETERS = ('opt','srej','brej')
LINES = [12, 21, 27]
DASHED = [3, 6, 9, 15, 18, 24, 30]
def makeSummaryPlot(fs, quantity):
    h = {}
    p = {}
    for parameter in PARAMETERS:
        h[parameter] = R.TH1F('h', ';;{} {}'.format(PRETTY[quantity], PRETTY[parameter]), 33, 0., 33.)
        for i,sp in enumerate(ORDER):
            h[parameter].SetBinContent(i+1, DATA[fs][sp][quantity][parameter])
        p[parameter] = Plotter.Plot(h[parameter], '', 'l', 'hist')

    for parameter in PARAMETERS:
        canvas = Plotter.Canvas(lumi='(c#tau smaller from left to right)     ' + fs)
        canvas.addMainPlot(p[parameter])

        p[parameter].setColor(R.kOrange, which='LF')

        m = 0.
        x = p[parameter].GetBinContent(p[parameter].GetMaximumBin())
        if x > m:
            m = x
        if quantity == 'LxyErr' and parameter == 'opt':
            m = 20.
        canvas.firstPlot.SetMinimum(0.)
        canvas.firstPlot.SetMaximum(m)

        ymin, ymax = 0., m

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

        #canvas.firstPlot.scaleTitleOffsets(0.8, axes='Y')

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

        canvas.cleanup('RC_{}_{}_{}.pdf'.format(fs, quantity, parameter))

for fs in ('2Mu2J',):
    for quantity in ('LxyErr', 'deltaR'):
        makeSummaryPlot(fs, quantity)
