import re
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
from DisplacedDimuons.Common.Utilities import SPStr, SPLumiStr
import DisplacedDimuons.Analysis.HistogramGetter as HistogramGetter
import DisplacedDimuons.Analysis.PlotterParser as PlotterParser

PlotterParser.PARSER.add_argument('--fs', dest='FS', default='2Mu2J', help='which final state to do')
ARGS = PlotterParser.PARSER.parse_args()

TRIGGER = ARGS.TRIGGER

# get histograms
#HISTS = HistogramGetter.getHistograms('../analyzers/roots/Main/SignalRecoResPlots.root')
f = R.TFile.Open('../analyzers/roots/Main/SignalRecoResPlots.root')

# overlaid resolution plots, per signal
# individual resolution plot can be achieved with a list of length 1 for MUONS
# outputTag is what tag to name the plot, e.g. DSA is DSA, but DSADim+REF can be RBA
# MUONS is expected to be some subject of ('DSA', 'RSA', 'REF', 'DSADim').
# For the legend, DSADim -> DSA by doing MUON[:3]
def makeOverlaidResPlot(MUONS, fs, sp, quantity, outputTag=None):
    # whether the plot is dif or res makes a difference wrt binning, fit range, and stats box positions
    # only pT is a res type; the others are all dif types
    ISDIF = quantity != 'pT'

    # what to name the plot. if MUONS is length 1, no sense to pass it twice, so get it automatically
    if outputTag is None:
        outputTag = MUONS[0]

    # colors, in order of MUONS, and also hashed
    defaultColorOrder = (R.kBlue, R.kRed, R.kGreen)
    colorDict = dict(zip(MUONS, defaultColorOrder))

    # get histograms and define plots
    h = {}
    for MUON in MUONS:
        h[MUON] = HistogramGetter.getHistogram(f, (fs, sp), MUON+'_'+quantity+'Res').Clone()
    p = {}
    for MUON in MUONS:
        RT.addFlows(h[MUON])
        if not ISDIF:
            h[MUON].Rebin(5)
        else:
            h[MUON].Rebin(10)
        p[MUON] = Plotter.Plot(h[MUON], 'Signal MC ({})'.format(MUON[:3]), 'l', 'hist')

    # define and fit gaussians to everything. Set FITRANGE to be something useful.
    funcs = {}
    fplots = {}
    for MUON in MUONS:
        if quantity == 'pT':
            FITRANGE = (-0.4, 0.3)
        elif quantity == 'eta':
            FITRANGE = (-0.1, 0.1)
        else:
            FITRANGE = (-20., 20.)
        funcs[MUON] = R.TF1('f'+MUON, 'gaus', *FITRANGE)
        h[MUON].Fit('f'+MUON, 'R')
        fplots[MUON] = Plotter.Plot(funcs[MUON], 'Gaussian fit ({})'.format(MUON[:3]), 'l', '')

    # define canvas, add plots. addS is so that statsbox will be drawn later.
    # these all should be pretty obvious until...
    canvas = Plotter.Canvas(lumi=SPLumiStr(fs, *sp))
    for i, MUON in enumerate(MUONS):
        canvas.addMainPlot(p[MUON], addS=True if i!=0 else False)
        canvas.addMainPlot(fplots[MUON])

    if len(MUONS) > 1:
        canvas.firstPlot.setTitles(X=canvas.firstPlot.GetXaxis().GetTitle().replace(MUONS[0],'Reco'))

    canvas.makeLegend(lWidth=.25, pos='tl')
    canvas.legend.resizeHeight()

    for MUON in MUONS:
        p     [MUON].SetLineColor(colorDict[MUON]  )
        fplots[MUON].SetLineColor(colorDict[MUON]+1)

    RT.addBinWidth(canvas.firstPlot)

    # dif type: fit boxes go down the left side
    # res type: fit boxes go down the middle
    # stats boxes are on the right
    paves = []
    for i, MUON in enumerate(MUONS):
        paves.append(canvas.makeStatsBox(p[MUON], color=colorDict[MUON]))
        Plotter.MOVE_OBJECT(paves[-1], Y=-.2*i)

        if not ISDIF:
            canvas.setFitBoxStyle(h[MUON], lWidth=0.275, pos='tr')
        else:
            canvas.setFitBoxStyle(h[MUON], lWidth=0.275, pos='tl')

        sbox = p[MUON].FindObject('stats')
        sbox.SetTextColor(colorDict[MUON]+1)

        if not ISDIF:
            Plotter.MOVE_OBJECT(sbox, Y=-.15*i, X=-.18, NDC=True)
        else:
            Plotter.MOVE_OBJECT(sbox, Y=-.15*i-0.04*4.1, NDC=True)

    fname = 'pdfs/SRR_{}_{}_{}HTo2XTo{}_{}.pdf'.format(outputTag, quantity+'Res', 'Trig-' if TRIGGER else '', fs, SPStr(sp))
    canvas.cleanup(fname)

# make 3D color plots
def makeColorPlot(MUON, fs, quantity, sp=None, q2=None):
    if q2 is None:
        fstring = '{M}_{Q}VS{Q}'.format(M=MUON, Q=quantity)
    else:
        fstring = '{M}_{Q}ResVS{Q2}'.format(M=MUON, Q=quantity, Q2=q2)

    if sp is None:
        for i, SP in enumerate(SIGNALPOINTS):
            if i == 0:
                h = HistogramGetter.getHistogram(f, (fs, SP), fstring).Clone()
            else:
                h.Add(HistogramGetter.getHistogram(f, (fs, SP), fstring).Clone())
        fname = 'pdfs/SRR_{}_{}HTo2XTo{}_Global.pdf'.format(fstring, 'Trig-' if TRIGGER else '', fs)
    else:
        h = HistogramGetter.getHistogram(f, (fs, sp), fstring).Clone()
        fname = 'pdfs/SRR_{}_{}HTo2XTo{}_{}.pdf'.format(fstring, 'Trig-' if TRIGGER else '', fs, SPStr(sp))

    h.Rebin2D(10, 10)
    p = Plotter.Plot(h, '', '', 'colz')
    canvas = Plotter.Canvas(lumi=SPLumiStr(fs, *sp) if sp is not None else fs)
    canvas.mainPad.SetLogz(True)
    canvas.addMainPlot(p)
    canvas.scaleMargins(1.75, edges='R')
    canvas.scaleMargins(0.8, edges='L')
    canvas.cleanup(fname)

# this function defines/configures some information for the binned/binwise plots
# it needs to manually be changed based on what the binning is -- there's probably some clever way of doing this
# pretty is the latex name, binranges DEFINE how many bins and what ranges to use, appropriate for ProjectionY
# values turns a binrange into an [x1, x2] interval (what will be written on the legend)
# colors defines colors; colors2 is for text (this might not be needed since R.kRed is a number)
# legname is the format for what will be written on the plot: value1, 2, between quantity, etc.
# qm uses a few tricks to get these formats to work out
# to get binranges from an interval [x1, x2], do (... binwidth*x1-1) (binwidth*x1, binwidth*x2-1) (binwidth*x2 ...)
def getBinningValues(q2):
    if q2 == 'pT':
        pretty    = 'p_{T}'
        binranges = ((0,99), (100,299), (300,499), (500, 1500))
        binwidth  = 1500./1500.
        values    = {key:(key[0]*binwidth, (key[1]+1)*binwidth) for key in binranges}
        colors    = dict(zip(binranges, (R.kRed, R.kBlue, R.kGreen, R.kMagenta)))
        colors2   = dict(zip(binranges, (2     , 4      , 3       , 6         )))
        legName   = '{V1} #leq {Q2} #leq {V2} GeV'
    elif q2 == 'Lxy':
        pretty    = 'L_{xy}'
        binranges = ((0,214), (215,411), (412,1000))
        binwidth  = 800./1000.
        values    = {key:(key[0]*binwidth, (key[1]+1)*binwidth) for key in binranges}
        colors    = dict(zip(binranges, (R.kRed, R.kBlue, R.kGreen)))
        colors2   = dict(zip(binranges, (2     , 4      , 3       )))
        legName   = '{V1} #leq {Q2} #leq {V2} cm'
    elif q2 == 'd0':
        pretty    = 'd_{0}'
        binranges = ((0,39), (40,119), (120,499), (500, 1000))
        binwidth  = 1000./1000.
        values    = {key:(key[0]*binwidth, (key[1]+1)*binwidth) for key in binranges}
        colors    = dict(zip(binranges, (R.kRed, R.kBlue, R.kGreen, R.kMagenta)))
        colors2   = dict(zip(binranges, (2     , 4      , 3       , 6         )))
        legName   = '{V1} #leq {Q2} #leq {V2} cm'
    elif q2 == 'qm':
        pretty    = 'charge matched'
        binranges = ((1, 1), (2, 2))
        values    = {(1, 1):(False, False),(2, 2):(True, True)}
        colors    = dict(zip(binranges, (R.kRed, R.kBlue)))
        colors2   = dict(zip(binranges, (2     , 4      )))
        legName   = '{Q2} : {V1}'

    return pretty, binranges, values, colors, colors2, legName

# make res plot binned by other quantities
def makeBinnedResPlot(MUON, fs, sp, quantity, q2):
    h = HistogramGetter.getHistogram(f, (fs, sp), '{M}_{Q}ResVS{Q2}'.format(M=MUON, Q=quantity, Q2=q2)).Clone()

    fname = 'pdfs/SRR_{}_{}_{}-Binned_{}HTo2XTo{}_{}.pdf'.format(MUON, quantity+'Res', q2, 'Trig-' if TRIGGER else '', fs, SPStr(sp))

    pretty, binranges, values, colors, colors2, legName = getBinningValues(q2)

    projections = {key:h.ProjectionY('_'+str(i), key[0], key[1]) for i,key in enumerate(binranges)}
    plots       = {key:Plotter.Plot(projections[key], legName.format(Q2=pretty, V1=values[key][0], V2=values[key][1]), 'l', 'hist') for key in binranges}

    canvas = Plotter.Canvas(lumi=SPLumiStr(fs, *sp))
    for key in binranges:
        RT.addFlows(plots[key])
        plots[key].Rebin(10)
        if plots[key].Integral() != 0:
            plots[key].Scale(1./plots[key].Integral())
        canvas.addMainPlot(plots[key])

    canvas.makeLegend(lWidth=.25, pos='tr')
    canvas.legend.moveLegend(X=-.08)
    canvas.legend.resizeHeight()
    canvas.setMaximum(recompute=True)

    for i, key in enumerate(binranges):
        plots[key].SetLineColor(colors[key])
        plots[key].setTitles(X=plots[key].GetXaxis().GetTitle(), Y='Normalized Counts')
        canvas.drawText('#color[{}]{{'.format(colors2[key]) + 'RMS = {:.4f}'.format(plots[key].GetStdDev()) + '}',
                        (canvas.legend.GetX1NDC()+.01, canvas.legend.GetY1NDC()-(i*0.04)-.04)
        )

    RT.addBinWidth(canvas.firstPlot)
    canvas.cleanup(fname)

# make res plot binned by other quantities, separated by bin
# necessarily, this must account for multiple plot types -- we are splitting bins across plots,
# so it must be because we're plotting two different plots of the same bin
# therefore MUONS should be a list, even if of one element, e.g. ('DSA', 'RSA') or ('REF', 'DSADim')
# outputTag should be whatever the resulting file name should be
def makeBinnedResPlotBinwise(MUONS, outputTag, quantity, q2, fs, sp):
    defaultColorOrder = (R.kRed, R.kBlue, R.kGreen, R.kMagenta)
    h = {}
    for MUON in MUONS:
        h[MUON] = HistogramGetter.getHistogram(f, (fs, sp), '{M}_{Q}ResVS{Q2}'.format(M=MUON, Q=quantity, Q2=q2)).Clone()

    # leaving space for the bin number
    fname = 'pdfs/SRR_{}_{}_{}-Binned-Bin-{{}}_{}HTo2XTo{}_{}.pdf'.format(outputTag, quantity+'Res', q2, 'Trig-' if TRIGGER else '', fs, SPStr(sp))

    pretty, binranges, values, colors, colors2, legName = getBinningValues(q2)

    for i, key in enumerate(binranges):
        canvas = Plotter.Canvas(lumi=SPLumiStr(fs, *sp))
        projections, plots = {}, {}
        for j, MUON in enumerate(MUONS):
            projections[MUON] = h[MUON].ProjectionY('_'+str(i)+'_'+str(j), key[0], key[1])
            plots[MUON]       = Plotter.Plot(projections[MUON], MUON, 'l', 'hist')
            RT.addFlows(plots[MUON])
            plots[MUON].Rebin(10)
            if plots[MUON].Integral() != 0:
                plots[MUON].Scale(1./plots[MUON].Integral())
            plots[MUON].SetLineColor(defaultColorOrder[j])

            canvas.addMainPlot(plots[MUON])

        canvas.makeLegend(lWidth=.25, pos='tr')
        canvas.legend.resizeHeight()
        canvas.setMaximum(recompute=True)

        canvas.drawText(legName.format(Q2=pretty, V1=values[key][0], V2=values[key][1]), (canvas.legend.GetX1NDC()+.01, canvas.legend.GetY1NDC()-.04))

        for j, MUON in enumerate(MUONS):
            plots[MUON].SetLineColor(defaultColorOrder[j])
            plots[MUON].setTitles(X=plots[MUON].GetXaxis().GetTitle(), Y='Normalized Counts')
            canvas.drawText('#color[{}]{{'.format(defaultColorOrder[j]) + 'RMS = {:.4f}'.format(plots[MUON].GetStdDev()) + '}',
                (canvas.legend.GetX1NDC()+.01, canvas.legend.GetY1NDC()-(j*0.04)-.08)
            )

        RT.addBinWidth(canvas.firstPlot)
        canvas.cleanup(fname.format(i+1))

# make plots
for fs in (ARGS.FS,):
    #for quantity in ('pT', 'Lxy', 'd0', 'dz', 'd0Lin', 'dzLin'):
    #    for MUON in ('DSA', 'RSA', 'REF'):
    #        if quantity == 'Lxy' and MUON in ('DSA', 'RSA'): continue

    #        # 2D reco quantity vs. gen quantity plots, global
    #        makeColorPlot(MUON, fs, quantity, sp=None, q2=None)
    #        # 2D resolution vs. gen quantity plots, global
    #        for q2 in ('pT', 'Lxy', 'd0', 'dz', 'd0Lin', 'dzLin', 'qm'):
    #            makeColorPlot(MUON, fs, quantity, sp=None, q2=q2)

    for sp in SIGNALPOINTS:
        for quantity in ('pT', 'Lxy', 'd0', 'dz', 'd0Lin', 'dzLin', 'eta'):
            for MUON in ('DSA', 'RSA', 'REF'):
                if quantity == 'Lxy' and MUON in ('DSA', 'RSA'): continue
                # 1D resolution plots, per signal point
                makeOverlaidResPlot((MUON,), fs, sp, quantity)

                if quantity != 'Lxy':
                    # 1D resolution plots, normalized, overlaid for 2 "muons"
                    makeOverlaidResPlot(('REF', 'DSADim'), fs, sp, quantity, outputTag='RBA')

                for q2 in ('pT', 'Lxy', 'd0', 'qm'):
                    # 1D resolution plots per signal point, binned by gen quantity
                    makeBinnedResPlot(MUON, fs, sp, quantity, q2)

        # 1D resolution plots, binned by gen quantity, split up by bin, overlaid for 2 "muons"
        makeBinnedResPlotBinwise(('REF', 'DSADim'), 'RBA', 'pT', 'Lxy', fs, sp)
