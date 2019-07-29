import ROOT as R
from DisplacedDimuons.Common.Constants import SIGNALPOINTS, SIGNALS
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.HistogramGetter as HG
import DisplacedDimuons.Analysis.AnalysisTools as AT
import numpy as np
from OptimizerTools import SignalInfo, ScaleFactor, calculateFOM, PARSER

ARGS = PARSER.parse_args()
FIGURE_OF_MERIT = ARGS.FOM

PRETTY_LEG = {'ZBi':'Z_{Bi}', 'ZPL':'Z_{PL}'}

FILE  = R.TFile.Open('../nMinusOne/roots/NM1Distributions_Trig_HTo2XTo2Mu2J.root')
DFILE = R.TFile.Open('../nMinusOne/roots/NM1Distributions_IDPHI_DATA.root')

HISTS  = {sp:HG.getHistogram(FILE, ('2Mu2J', sp), 'mass') for sp in SIGNALPOINTS}
SCALED = {sp:HISTS[sp].Clone() for sp in SIGNALPOINTS}
for sp in SIGNALPOINTS:
    integral = SCALED[sp].Integral(0, SCALED[sp].GetNbinsX()+1)
    SCALED[sp].Scale(1./(integral if integral != 0. else 1.))
CUM    = {sp:SCALED[sp].GetCumulative() for sp in SIGNALPOINTS}
DISTS  = {sp:Plotter.Plot(HISTS[sp],  'm_{{X}} = {} GeV'.format(sp[1]), 'l', 'hist') for sp in SIGNALPOINTS}
PLOTS  = {sp:Plotter.Plot(CUM[sp], 'm_{{X}} = {} GeV'.format(sp[1]), 'l', 'hist') for sp in SIGNALPOINTS}

HISTS ['data'] = HG.getDataHistograms(DFILE, 'mass')[0]['mass']['data']
SCALED['data'] = HISTS['data'].Clone()
SCALED['data'].Scale(1./SCALED['data'].Integral(0, SCALED['data'].GetNbinsX()+1))
CUM   ['data'] = SCALED['data'].GetCumulative()
DISTS ['data'] = Plotter.Plot(HISTS['data'], 'Data', 'l', 'hist p')
PLOTS ['data'] = Plotter.Plot(CUM['data'], 'Data', 'l', 'hist p')

cols = [(228,26,28),(55,126,184),(77,175,74),(152,78,163)]
cols = [(102,194,165),(252,141,98),(141,160,203),(231,138,195)]
rcols = {7000+i:R.TColor(7000+i, *(c/255. for c in cols[i])) for i in xrange(4)}
COLORS = {20:7000, 50:7001, 150:7002, 350:7003}

COLORS = {20:R.kRed, 50:R.kBlue, 150:R.kGreen, 350:R.kOrange}


# some code for making invariant mass plots with Gaussian fits
# superseded by the mass plot that will eventually be in the "thesis" folder
# so I am guarding against global changes to the gStyle and etc. by
# hiding the code inside a False. Change it to True if you want it back.
if False:
    #########################################
    ####   Plot 0: invariant-mass plots  ####
    #########################################
    fname = 'pdfs/invmassPlots.pdf'
    canvas = R.TCanvas('c1', 'canvas', 0, 0, 800, 600)
    R.gStyle.SetOptStat(111111)

    canvas.Clear()
    htit = 'm(X) = 350 GeV'
    mLow = 0.
    mHigh = 400.
    func = R.TF1('f', 'gaus', mLow, mHigh)
    pad = R.TPad('pad','pad', 0, 0, 1, 1)
    legend = {}
    pad.Draw()
    pad.Divide(2,2)
    ipad = 1
    for sp in SIGNALPOINTS:
        print sp
        if sp[1] == 350:
            pad.cd(ipad)
            HISTS[sp].Rebin(4)
            HISTS[sp].Fit('f', 'LRE')
            str = "%s %s %s" %(sp[0], sp[1], sp[2])
            legend[sp] = R.TLegend(0.2, 0.6, 0.4, 0.8)
            legend[sp].AddEntry("HISTS[sp]", str, "l");
            legend[sp].Draw()
            ipad = ipad + 1
    canvas.Print(fname+"(", "Title:"+htit)

    canvas.Clear()
    htit = 'm(X) = 150 GeV'
    mLow = 50.
    mHigh = 220.
    func = R.TF1('f', 'gaus', mLow, mHigh)
    pad = R.TPad('pad','pad', 0, 0, 1, 1)
    legend = {}
    pad.Draw()
    pad.Divide(2,3)
    ipad = 1
    for sp in SIGNALPOINTS:
        if sp[1] == 150:
            pad.cd(ipad)
            HISTS[sp].Rebin(2)
            HISTS[sp].Fit('f', 'LRE')
            str = "%s %s %s" %(sp[0], sp[1], sp[2])
            legend[sp] = R.TLegend(0.65, 0.3, 0.85, 0.5)
            legend[sp].AddEntry("HISTS[sp]", str, "l");
            legend[sp].Draw()
            ipad = ipad + 1
    canvas.Print(fname, "Title:"+htit)

    htit = 'm(X) = 50 GeV'
    mLow = 10.
    mHigh = 70.
    func = R.TF1('f', 'gaus', mLow, mHigh)
    ihist = 0
    hist = {}
    for sp in SIGNALPOINTS:
        if sp[1] == 50:
            ipad = ihist%6
            if ipad == 0:
                canvas.Clear()
                pad = R.TPad('pad','pad', 0, 0, 1, 1)
                legend = {}
                pad.Draw()
                pad.Divide(2,3)
            pad.cd(ipad+1)
    #        HISTS[sp].Rebin(2)
            nbins = HISTS[sp].GetNbinsX()
            xmax = HISTS[sp].GetXaxis().GetXmax()
            nbins_100GeV = int(nbins*100./xmax)
            hist[sp] = R.TH1F("h", "hist", nbins_100GeV, 0., 100.)
            for ibin in range(1, nbins_100GeV):
                f_bin   = HISTS[sp].GetBinContent(ibin)
                err_bin = HISTS[sp].GetBinError(ibin)
                hist[sp].SetBinContent(ibin, f_bin)
                hist[sp].SetLineColor(R.kBlue)
            hist[sp].Rebin(2)
            hist[sp].Fit('f', 'LRE')
            str = "%s %s %s" %(sp[0], sp[1], sp[2])
            legend[sp] = R.TLegend(0.65, 0.3, 0.85, 0.5)
            legend[sp].AddEntry("HISTS[sp]", str, "l");
            legend[sp].Draw()
            ihist = ihist + 1
            if ipad == 5 or ipad == 11:
                canvas.Print(fname, "Title:"+htit)

    htit = 'm(X) = 20 GeV'
    mLow = 5.
    mHigh = 30.
    func = R.TF1('f', 'gaus', mLow, mHigh)
    ihist = 0
    hist = {}
    for sp in SIGNALPOINTS:
        if sp[1] == 20:
            ipad = ihist%6
            if ipad == 0:
                canvas.Clear()
                pad = R.TPad('pad','pad', 0, 0, 1, 1)
                legend = {}
                pad.Draw()
                pad.Divide(2,3)
            pad.cd(ipad+1)
    #        HISTS[sp].Rebin(2)
            nbins = HISTS[sp].GetNbinsX()
            xmax = HISTS[sp].GetXaxis().GetXmax()
            nbins_50GeV = int(nbins*50./xmax)
            hist[sp] = R.TH1F("h", "hist", nbins_50GeV, 0., 50.)
            for ibin in range(1, nbins_50GeV):
                f_bin   = HISTS[sp].GetBinContent(ibin)
                err_bin = HISTS[sp].GetBinError(ibin)
                hist[sp].SetBinContent(ibin, f_bin)
                hist[sp].SetLineColor(R.kBlue)
            hist[sp].Rebin(2)
            hist[sp].Fit('f', 'LRE')
            str = "%s %s %s" %(sp[0], sp[1], sp[2])
            legend[sp] = R.TLegend(0.65, 0.3, 0.85, 0.5)
            legend[sp].AddEntry("HISTS[sp]", str, "l");
            legend[sp].Draw()
            ihist = ihist + 1
            if ipad == 5 or ipad == 11:
                canvas.Print(fname, "Title:"+htit)

    canvas.Clear()
    htit = 'm(X) = 150 GeV'
    mLow = 50.
    mHigh = 220.
    func = R.TF1('f', 'gaus', mLow, mHigh)
    pad = R.TPad('pad','pad', 0, 0, 1, 1)
    legend = {}
    pad.Draw()
    pad.Divide(2,3)
    ipad = 1
    for sp in SIGNALPOINTS:
        if sp[1] == 150:
            pad.cd(ipad)
            HISTS[sp].Rebin(2)
            HISTS[sp].Fit('f', 'LRE')
            str = "%s %s %s" %(sp[0], sp[1], sp[2])
            legend[sp] = R.TLegend(0.6, 0.5, 0.8, 0.7)
            legend[sp].AddEntry("HISTS[sp]", str, "l");
            legend[sp].Draw()
            ipad = ipad + 1
    canvas.Print(fname+")", "Title:"+htit)

#exit()

#########################################
#### Plot 1: Distributions of masses ####
#########################################

canvas = Plotter.Canvas()

# just long and medium -- the keys in SignalInfo
longAndMedium = []
for sp in SignalInfo:
    longAndMedium.append(sp)
    canvas.addMainPlot(DISTS[sp])
    DISTS[sp].SetLineColor(COLORS[sp[1]])
    print '{1:4d} {2:3d} {3:4d} {0:6.2f}'.format(DISTS[sp].GetXaxis().GetBinCenter(DISTS[sp].GetMaximumBin()), *sp)

# add the data plot
canvas.addMainPlot(DISTS['data'])
DISTS['data'].setColor(R.kBlack, which='LM')

# legend should just include 4 plots
# so loop over the sp used, keep track of the masses,
# and keep a signal point from each mass
canvas.makeLegend(lWidth=.2, autoOrder=False, pos='tr')
alreadyUsedMasses = []
justTheseFour = []
for sp in longAndMedium:
    if sp[1] in alreadyUsedMasses: continue
    alreadyUsedMasses.append(sp[1])
    justTheseFour.append(sp)

# it's nice if they're in sorted order
justTheseFour.sort(key=lambda x:x[1])
for sp in justTheseFour:
    canvas.legend.addLegendEntry(DISTS[sp])

canvas.legend.addLegendEntry(DISTS['data'])

canvas.legend.resizeHeight()
canvas.setMaximum()

if False:
    for ibin in xrange(0, DISTS['data'].GetNbinsX()+2):
        print '{:5.1f} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f}'.format(
            DISTS['data'].GetXaxis().GetBinUpEdge(ibin),
            DISTS['data'].GetBinContent(ibin),
            *[DISTS[sp].GetBinContent(ibin) for sp in justTheseFour]
        )

canvas.cleanup('pdfs/massDist.pdf')

############################################
#### Plot 2: Cumulative plots of masses ####
############################################

canvas = Plotter.Canvas()

# just long and medium -- the keys in SignalInfo
for sp in SignalInfo:
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
#### Plot 3: Mass vs. ZBi ####
##############################

ESCALED = {sp:HISTS[sp].Clone() for sp in SignalInfo}
for sp in ESCALED:
    ESCALED[sp].Scale(ScaleFactor(sp, sigmaB=1.e-2))

FOM_DATA = {sp:{'x':[], 'y':[]} for sp in ESCALED}

nBins, xAxis = ESCALED[longAndMedium[0]].GetNbinsX(), ESCALED[longAndMedium[0]].GetXaxis()
for sp in ESCALED:
    for ibin in xrange(1, nBins+1):
        S, B, cutVal, FOMs = calculateFOM(ESCALED[sp], HISTS['data'], ESCALED[sp].GetCumulative(False), HISTS['data'].GetCumulative(False), nBins, ibin, xAxis, False)
        FOM_DATA[sp]['x'].append(HISTS['data'].GetXaxis().GetBinCenter(ibin))
        FOM_DATA[sp]['y'].append(FOMs[FIGURE_OF_MERIT])

FOM_GRAPHS = {}
for sp in ESCALED:
    FOM_GRAPHS[sp] = R.TGraph(len(FOM_DATA[sp]['x']), np.array(FOM_DATA[sp]['x']), np.array(FOM_DATA[sp]['y']))

FOM_PLOTS = {sp:Plotter.Plot(FOM_GRAPHS[sp], 'm_{{X}} = {} GeV'.format(sp[1]), 'l', 'l') for sp in FOM_GRAPHS}

canvas = Plotter.Canvas()
for sp in FOM_PLOTS:
    canvas.addMainPlot(FOM_PLOTS[sp])
    FOM_PLOTS[sp].setColor(COLORS[sp[1]], which='LM')

canvas.makeLegend(lWidth=.2, autoOrder=False, pos='tr')
for sp in justTheseFour:
    canvas.legend.addLegendEntry(FOM_PLOTS[sp])

canvas.firstPlot.setTitles(X='M(#mu#mu) [GeV]', Y=PRETTY_LEG[FIGURE_OF_MERIT])
canvas.legend.resizeHeight()
canvas.firstPlot.SetMaximum(8.)
canvas.firstPlot.SetMinimum(0.)
canvas.cleanup('pdfs/massFOM_{}.pdf'.format(FIGURE_OF_MERIT))

#####################################
#### Plot 4: Mass Window vs. ZBi ####
#####################################

FOM_DATA = {sp:{'x':[], 'y':[]} for sp in ESCALED}

peaks = {20:16.75, 50:46.25, 150:139.25, 350:330.25}

for sp in ESCALED:
    peakBinVal = peaks[sp[1]]
    peakBinSig = ESCALED[sp].FindBin(peakBinVal)
    peakBinDat = HISTS['data'].FindBin(peakBinVal)
    for window in range(1,501):
        S = ESCALED[sp    ].Integral(peakBinSig-window, peakBinSig+window)
        B = HISTS  ['data'].Integral(peakBinDat-window, peakBinDat+window)
        FOM_DATA   [sp]['x'].append(window*.5)
        FOM_DATA   [sp]['y'].append(getattr(AT, FIGURE_OF_MERIT)(S+B, B, 1.))

for ibin in xrange(HISTS['data'].GetNbinsX()+1):
    if HISTS['data'].GetBinContent(ibin) != 0:
        print '{:5.1f}-{:5.1f} : {:2.0f}'.format(HISTS['data'].GetXaxis().GetBinLowEdge(ibin), HISTS['data'].GetXaxis().GetBinUpEdge(ibin), HISTS['data'].GetBinContent(ibin))

FOM_GRAPHS = {}
for sp in ESCALED:
    FOM_GRAPHS[sp] = R.TGraph(len(FOM_DATA[sp]['x']), np.array(FOM_DATA[sp]['x']), np.array(FOM_DATA[sp]['y']))

FOM_PLOTS = {sp:Plotter.Plot(FOM_GRAPHS[sp], 'm_{{X}} = {} GeV'.format(sp[1]), 'l', 'l') for sp in FOM_GRAPHS}

canvas = Plotter.Canvas()
for sp in FOM_PLOTS:
    canvas.addMainPlot(FOM_PLOTS[sp])
    FOM_PLOTS[sp].setColor(COLORS[sp[1]], which='LM')

canvas.makeLegend(lWidth=.2, autoOrder=False, pos='tr')
for sp in justTheseFour:
    canvas.legend.addLegendEntry(FOM_PLOTS[sp])

canvas.firstPlot.setTitles(X='One side of mass window [GeV]', Y=PRETTY_LEG[FIGURE_OF_MERIT])
canvas.legend.resizeHeight()
canvas.firstPlot.SetMaximum(8.)
canvas.firstPlot.SetMinimum(0.)
canvas.cleanup('pdfs/massFOM_Window_{}.pdf'.format(FIGURE_OF_MERIT))
