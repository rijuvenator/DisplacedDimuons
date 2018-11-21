import re
import subprocess as bash
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
from DisplacedDimuons.Common.Utilities import SPStr, SPLumiStr
import DisplacedDimuons.Analysis.HistogramGetter as HistogramGetter
import DisplacedDimuons.Analysis.PlotterParser as PlotterParser

ARGS = PlotterParser.PARSER.parse_args()
TRIGGER = ARGS.TRIGGER

bash.call('cd ../analyzers/roots/Main; ../relink RecoMuonPlots {}_SignalOnly; cd -'.format('Trig' if ARGS.TRIGGER else 'Full'), shell=True)

# get histograms
f = R.TFile.Open('../analyzers/roots/Main/RecoMuonPlots.root')

DATA = {'2Mu2J':{}, '4Mu':{}}

def fillDistributionParameters(MUON, fs, sp, quantity):

    # get histograms and define plots
    h = HistogramGetter.getHistogram(f, (fs, sp), MUON+'_'+quantity+'_Matched').Clone()

    mean  = h.GetMean()
    sigma = h.GetStdDev()
    overflow = h.GetBinContent(h.GetNbinsX()+1)

    if sp not in DATA[fs]: DATA[fs][sp] = {}
    if MUON not in DATA[fs][sp]: DATA[fs][sp][MUON] = {}
    if quantity not in DATA[fs][sp][MUON]: DATA[fs][sp][MUON][quantity] = {
        'mean':0,
        'sigma':0,
        'overflow':0,
    }

    DATA[fs][sp][MUON][quantity]['mean' ] = mean
    DATA[fs][sp][MUON][quantity]['sigma'] = sigma
    DATA[fs][sp][MUON][quantity]['overflow'] = overflow

QUANTITIES = ('pTSig', 'd0Sig')

# make plots
#for fs in ('2Mu2J', '4Mu'):
for fs in ('2Mu2J',):
    for sp in SIGNALPOINTS:
        for quantity in QUANTITIES:
            for MUON in ('DSA', 'REF'):
                fillDistributionParameters(MUON, fs, sp, quantity)

for quantity in QUANTITIES:
    #for fs in ('2Mu2J', '4Mu'):
    for fs in ('2Mu2J',):
        for sp in DATA[fs]:
            # print DSA REF and ratios
            print '{:5s} {:4d} {:3d} {:4d} {:5s} :: {:8.4f} {:8.4f} {:4.0f} :: {:8.4f} {:8.4f} {:4.0f} :: {:6.2%} {:6.2%} {:6.2%}'.format(fs, sp[0], sp[1], sp[2], quantity,
                DATA[fs][sp]['DSA'][quantity]['mean'],
                DATA[fs][sp]['DSA'][quantity]['sigma'],
                DATA[fs][sp]['DSA'][quantity]['overflow'],
                DATA[fs][sp]['REF'][quantity]['mean'],
                DATA[fs][sp]['REF'][quantity]['sigma'],
                DATA[fs][sp]['REF'][quantity]['overflow'],
                (DATA[fs][sp]['REF'][quantity]['mean']/DATA[fs][sp]['DSA'][quantity]['mean']),
                (DATA[fs][sp]['REF'][quantity]['sigma']/DATA[fs][sp]['DSA'][quantity]['sigma']),
                (DATA[fs][sp]['REF'][quantity]['overflow']/DATA[fs][sp]['DSA'][quantity]['overflow']) if DATA[fs][sp]['DSA'][quantity]['overflow'] != 0. else 0.,
            )

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

PRETTY = {'pTSig':'#sigma_{p_{T}}/p_{T}', 'd0Sig':'d_{0}/#sigma_{d_{0}}', 'mean':'Mean', 'sigma':'RMS', 'overflow':'Overflow'}
MUONS = ('DSA', 'REF')
PARAMETERS = ('mean', 'sigma', 'overflow')
COLORS = {'DSA':R.kRed, 'REF':R.kBlue}
LINES = [12, 21, 27]
DASHED = [3, 6, 9, 15, 18, 24, 30]
def makeSummaryPlot(fs, quantity):
    h = {}
    p = {}
    for MUON in MUONS:
        p[MUON] = {}
        h[MUON] = {}
        for parameter in PARAMETERS:
            h[MUON][parameter] = R.TH1F('h'+parameter+MUON+fs+quantity, ';;{} {}'.format(PRETTY[quantity], PRETTY[parameter]), 33, 0., 33.)
            for i,sp in enumerate(ORDER):
                h[MUON][parameter].SetBinContent(i+1, DATA[fs][sp][MUON][quantity][parameter])
            p[MUON][parameter] = Plotter.Plot(h[MUON][parameter], MUON if MUON != 'DSADim' else 'DSA\'', 'l', 'hist')

    for parameter in PARAMETERS:
        canvas = Plotter.Canvas(lumi='(each group of 3 = decreasing c#tau from left to right)     ' + fs, ratioFactor=1./3., fontscale=1.+1./3.)
        for MUON in MUONS:
            canvas.addMainPlot(p[MUON][parameter])

            p[MUON][parameter].setColor(COLORS[MUON], which='LF')

        canvas.makeLegend(lWidth=.1, pos='tr', fontscale=1.+1./3.)

        canvas.legend.SetFillStyle(1001)
        canvas.legend.SetFillColor(R.kWhite)
        canvas.legend.SetBorderSize(1)

        canvas.legend.resizeHeight(scale=1.1)

        REVERSE = h['DSA'][parameter].GetBinContent(15) < 0
        if REVERSE:
            m = 0.
            for MUON in MUONS:
                x = p[MUON][parameter].GetBinContent(p[MUON][parameter].GetMinimumBin())
                if x < m:
                    m = x
            canvas.firstPlot.SetMaximum(0.)
            canvas.firstPlot.SetMinimum(m)

            ymin, ymax = m, 0.
        else:
            m = 0.
            for MUON in MUONS:
                x = p[MUON][parameter].GetBinContent(p[MUON][parameter].GetMaximumBin())
                if x > m:
                    m = x
            canvas.firstPlot.SetMinimum(0.)
            canvas.firstPlot.SetMaximum(m)

            ymin, ymax = 0., m

        canvas.firstPlot.SetNdivisions(33)

        # mainPad lines
        lines = []
        for line in LINES:
            lines.append(R.TLine(line, ymin, line, ymax))
            lines[-1].Draw()
        for line in DASHED:
            lines.append(R.TLine(line, ymin, line, ymax))
            lines[-1].SetLineStyle(2)
            lines[-1].Draw()

        canvas.makeRatioPlot(p['REF'][parameter], p['DSA'][parameter], ytit='REF/DSA', drawLine=False)

        canvas.firstPlot.scaleTitleOffsets(0.8, axes='Y')
        canvas.rat      .scaleTitleOffsets(0.8, axes='Y')

        # rat aesthetics
        canvas.rat.SetNdivisions(33)
        canvas.rat.SetFillStyle(0)
        canvas.rat.SetLineColor(R.kBlue)
        if parameter == 'overflow':
            low = 0.
        else:
            low = 0.5
        canvas.rat.GetYaxis().SetRangeUser(low, 1.)
        canvas.rat.GetXaxis().SetLabelSize(0)

        # ratPad lines
        canvas.ratPad.cd()
        for line in LINES:
            lines.append(R.TLine(line, low, line, 1.))
            lines[-1].Draw()
        for line in DASHED:
            lines.append(R.TLine(line, low, line, 1.))
            lines[-1].SetLineStyle(2)
            lines[-1].Draw()

        canvas.cd()

        # mH labels
        canvas.drawText(text='m_{H} [GeV]', align='cl', pos=(0, .02), fontscale=.8)
        canvas.drawText(text='1000', align='cc', pos=(.275, .02))
        canvas.drawText(text='400' , align='cc', pos=(.54 , .02))
        canvas.drawText(text='200' , align='cc', pos=(.725, .02))
        canvas.drawText(text='125' , align='cc', pos=(.875, .02))

        # mX labels
        canvas.drawText(text='m_{X} [GeV]', align='cl', pos=(0, .06), fontscale=.8)
        start = .17
        step = .074
        canvas.drawText(text='350' , align='cc', pos=(start+step*0 , .06))
        canvas.drawText(text='150' , align='cc', pos=(start+step*1 , .06))
        canvas.drawText(text='50'  , align='cc', pos=(start+step*2 , .06))
        canvas.drawText(text='20'  , align='cc', pos=(start+step*3 , .06))

        canvas.drawText(text='150' , align='cc', pos=(start+step*4 , .06))
        canvas.drawText(text='50'  , align='cc', pos=(start+step*5 , .06))
        canvas.drawText(text='20'  , align='cc', pos=(start+step*6 , .06))

        canvas.drawText(text='50'  , align='cc', pos=(start+step*7 , .06))
        canvas.drawText(text='20'  , align='cc', pos=(start+step*8 , .06))

        canvas.drawText(text='50'  , align='cc', pos=(start+step*9 , .06))
        canvas.drawText(text='20'  , align='cc', pos=(start+step*10, .06))

        # custom modifications to cleanup
        canvas.finishCanvas(extrascale=1+1./3.)
        canvas.save('RC_{}_{}_{}{}.pdf'.format(fs, quantity, parameter, '' if not TRIGGER else '_Trig'))
        canvas.deleteCanvas()
    

for quantity in QUANTITIES:
    makeSummaryPlot('2Mu2J', quantity)
