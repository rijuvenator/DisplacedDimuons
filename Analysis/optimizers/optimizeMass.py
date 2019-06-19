import ROOT as R
from DisplacedDimuons.Common.Constants import SIGNALPOINTS, SIGNALS
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.HistogramGetter as HG
from OptimizerTools import SignalInfo, ScaleFactor, calculateFOM, PARSER

ARGS = PARSER.parse_args()
FIGURE_OF_MERIT = ARGS.FOM

PRETTY_LEG = {'ZBi':'Z_{Bi}', 'ZPL':'Z_{PL}'}

FILE  = R.TFile.Open('../nMinusOne/roots/NM1Distributions_Trig_HTo2XTo2Mu2J.root')
DFILE = R.TFile.Open('../nMinusOne/roots/NM1Distributions_IDPHI_DATA.root')

HISTS = {sp:HG.getHistogram(FILE, ('2Mu2J', sp), 'mass') for sp in SIGNALPOINTS}
SCALED = {sp:HISTS[sp].Clone() for sp in SIGNALPOINTS}
for sp in SIGNALPOINTS:
    integral = SCALED[sp].Integral(0, SCALED[sp].GetNbinsX()+1)
    SCALED[sp].Scale(1./(integral if integral != 0. else 1.))
CUM = {sp:SCALED[sp].GetCumulative() for sp in SIGNALPOINTS}
PLOTS = {sp:Plotter.Plot(CUM[sp], 'm_{{X}} = {} GeV'.format(sp[1]), 'l', 'hist') for sp in SIGNALPOINTS}

HISTS ['data'] = HG.getDataHistograms(DFILE, 'mass')[0]['mass']['data']
SCALED['data'] = HISTS['data'].Clone()
SCALED['data'].Scale(1./SCALED['data'].Integral(0, SCALED['data'].GetNbinsX()+1))
CUM   ['data'] = SCALED['data'].GetCumulative()
PLOTS ['data'] = Plotter.Plot(CUM['data'], 'Data', 'l', 'hist p')

COLORS = {20:R.kRed, 50:R.kBlue, 150:R.kGreen, 350:R.kMagenta}

############################################
#### Plot 1: Cumulative plots of masses ####
############################################

canvas = Plotter.Canvas()

# just long and medium -- the keys in SignalInfo
longAndMedium = []
for sp in SignalInfo:
    longAndMedium.append(sp)
    canvas.addMainPlot(PLOTS[sp])
    PLOTS[sp].SetLineColor(COLORS[sp[1]])

# add the data plot
canvas.addMainPlot(PLOTS['data'])
PLOTS['data'].setColor(R.kBlack, which='LM')

# legend should just include 4 plots
# so loop over the sp used, keep track of the masses,
# and keep a signal point from each mass
canvas.makeLegend(lWidth=.2, autoOrder=False, pos='br')
alreadyUsedMasses = []
justTheseFour = []
for sp in longAndMedium:
    if sp[1] in alreadyUsedMasses: continue
    alreadyUsedMasses.append(sp[1])
    justTheseFour.append(sp)

# it's nice if they're in sorted order
justTheseFour.sort(key=lambda x:x[1])
for sp in justTheseFour:
    canvas.legend.addLegendEntry(PLOTS[sp])

canvas.legend.addLegendEntry(PLOTS['data'])

canvas.legend.resizeHeight()
canvas.firstPlot.SetMaximum(1.1)

if False:
    for ibin in xrange(0, PLOTS['data'].GetNbinsX()+2):
        print '{:5.1f} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f}'.format(
            PLOTS['data'].GetXaxis().GetBinUpEdge(ibin),
            PLOTS['data'].GetBinContent(ibin),
            *[PLOTS[sp].GetBinContent(ibin) for sp in justTheseFour]
        )

canvas.cleanup('pdfs/massCum.pdf')

##############################
#### Plot 2: Mass vs. ZBi ####
##############################

ESCALED = {sp:HISTS[sp].Clone() for sp in SignalInfo}
FOM_HISTS = {sp:HISTS[sp].Clone() for sp in SignalInfo}
for sp in ESCALED:
    ESCALED[sp].Scale(ScaleFactor(sp, sigmaB=1.e-2))

nBins, xAxis = ESCALED[longAndMedium[0]].GetNbinsX(), ESCALED[longAndMedium[0]].GetXaxis()
for sp in ESCALED:
    for ibin in xrange(1, nBins+1):
        S, B, cutVal, FOMs = calculateFOM(ESCALED[sp], HISTS['data'], ESCALED[sp].GetCumulative(False), HISTS['data'].GetCumulative(False), nBins, ibin, xAxis, False)
        FOM_HISTS[sp].SetBinContent(ibin, FOMs[FIGURE_OF_MERIT])

FOM_PLOTS = {sp:Plotter.Plot(FOM_HISTS[sp], 'm_{{X}} = {} GeV'.format(sp[1]), 'l', 'hist') for sp in FOM_HISTS}

canvas = Plotter.Canvas()
for sp in FOM_PLOTS:
    canvas.addMainPlot(FOM_PLOTS[sp])
    FOM_PLOTS[sp].setColor(COLORS[sp[1]], which='LM')

canvas.makeLegend(lWidth=.2, autoOrder=False, pos='tr')
for sp in justTheseFour:
    canvas.legend.addLegendEntry(FOM_PLOTS[sp])

canvas.firstPlot.setTitles(Y=PRETTY_LEG[FIGURE_OF_MERIT])
canvas.legend.resizeHeight()
canvas.setMaximum(recompute=True)
canvas.cleanup('pdfs/massFOM_{}.pdf'.format(FIGURE_OF_MERIT))
