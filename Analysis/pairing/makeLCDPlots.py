import re
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
from DisplacedDimuons.Common.Utilities import SPStr, SPLumiStr
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
import DisplacedDimuons.Analysis.HistogramGetter as HistogramGetter
import DisplacedDimuons.Analysis.PlotterParser as PlotterParser

ARGS = PlotterParser.PARSER.parse_args()
f = R.TFile.Open('roots/Main/LCDPlots_Trig{}_HTo2XTo4Mu.root'.format(ARGS.CUTSTRING))

#QUANTITIES = ('GLxy', 'GpT1', 'Gmass', 'RLxy', 'RpT1', 'Rmass')
QUANTITIES = ('GLxy', 'RLxy')
CRITERIA = []
for fillWhen in ('', '-4'):
    for oppCharge in ('', '-OC'):
        CRITERIA.append('Chi2'+oppCharge+fillWhen)
        for criteria in ('-LCD', '-C2S', '-AMD'):
            fullName = 'HPD'+oppCharge+criteria+fillWhen
            if fillWhen == '-4' or (fillWhen == '' and criteria != '-AMD'):
                CRITERIA.append(fullName)

def makeDistPlot(quantity, criteria, fs, sp=None):
    # configy type stuff
    legs = ('All', 'Matched', 'NotMatched')
    tags = [quantity+'_'+('All'+('-4' if '-4' in criteria else '') if 'All' in leg else criteria+'_'+leg) for leg in legs]
    cols = (R.kBlack, R.kBlue, R.kRed)

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
    logy = True
    canvas = Plotter.Canvas(lumi=SPLumiStr(fs, sp) if sp is not None else fs, logy=logy)
    for tag in tags:
        canvas.addMainPlot(p[tag])
    canvas.setMaximum()
    if not logy:
        canvas.firstPlot.SetMinimum(0)
    else:
        canvas.firstPlot.SetMinimum(1.)
    if 'Lxy' in quantity:
        canvas.firstPlot.GetXaxis().SetRangeUser(0., 330.)

    # colors
    for i,tag in enumerate(tags):
        p[tag].SetLineColor(cols[i])

    # legend, cleanup
    canvas.makeLegend(lWidth=.2, pos='tr')
    canvas.legend.resizeHeight()

    canvas.cleanup('pdfs/LCD_{}Dist_{}{}_HTo2XTo{}_{}.pdf'.format(quantity, criteria, ARGS.CUTSTRING, fs, SPStr(sp) if sp is not None else 'Global'))

def makeEffPlot(quantity, criteria, fs, sp=None):
    # configy type stuff
    legs = ('All', 'Matched', 'NotMatched')
    tags = [quantity+'_'+('All'+('-4' if '-4' in criteria else '') if 'All' in leg else criteria+'_'+leg) for leg in legs]
    cols = (R.kBlack, R.kBlue, R.kRed)

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

    for tag in tags:
        h[tag].Rebin(5)

    clones = {tag:h[tag].Clone() for tag in tags}
    for tag in tags[1:]:
        h[tag] = R.TGraphAsymmErrors(clones[tag], clones[tags[0]], 'cp')

    # make plots
    p = {}
    for i,tag in enumerate(tags):
        p[tag] = Plotter.Plot(h[tag], legs[i], 'l', 'px')

    # canvas, plots, min max
    canvas = Plotter.Canvas(lumi=SPLumiStr(fs, sp) if sp is not None else fs)
    for tag in tags:
        if 'All' in tag: continue
        canvas.addMainPlot(p[tag])
    canvas.setMaximum()
    canvas.firstPlot.SetMinimum(0)
    if 'Lxy' in quantity:
        canvas.firstPlot.GetXaxis().SetRangeUser(0., 330.)

    # set titles
    canvas.firstPlot.setTitles(X=clones[tags[0]].GetXaxis().GetTitle(), Y='Efficiency')

    # colors
    for i,tag in enumerate(tags):
        p[tag].setColor(cols[i])

    # legend, cleanup
    canvas.makeLegend(lWidth=.2, pos='tr')
    canvas.legend.resizeHeight()

    if not (criteria in ('HPD-OC-C2S', 'HPD-C2S') and ARGS.CUTSTRING in ('', '_5GeV')):
        canvas.legend.moveLegend(Y=-.3)

    canvas.cleanup('pdfs/LCD_{}Eff_{}{}_HTo2XTo{}_{}.pdf'.format(quantity, criteria, ARGS.CUTSTRING, fs, SPStr(sp) if sp is not None else 'Global'))

class HTag(object):
    def __init__(self, tag):
        self.tag = tag
        self.oc = True if '-OC' in tag else False
        self.sig4 = True if '-4' in tag else False
        self.crit = re.match(r'.*(Chi2|C2S|LCD|AMD)', tag).group(1)

    def __str__(self):
        return '{} :: OC = {}, SIG4 = {}, CRIT = {}'.format(self.tag, self.oc, self.sig4, self.crit)

HTAGS = [HTag(crit) for crit in CRITERIA]

def makeComboPlots(quantity, colorAxis):
    fs = '4Mu'

    SELS  = ('', '_4Reco', '_5GeV', '_4Reco_5GeV')
    CRITS = ('Chi2', 'C2S', 'LCD', 'AMD')
    OCS   = (True, False)
    SIG4S = (True, False)

    PRETTYSEL = {'':'NoSel', '_4Reco':'4Reco', '_5GeV':'5GeV', '_4Reco_5GeV':'4Reco_5GeV'}

    FILES = {sel:R.TFile.Open('roots/Main/LCDPlots_Trig{}_HTo2XTo4Mu.root'.format(sel)) for sel in SELS}

    def makeHists(htags, SEL=None):
        HISTS = {}
        if SEL is None:
            for sel in SELS:
                FILES[sel].cd()
                # when SEL is None, htags is of length 1
                for tag in htags:
                    HISTS[sel.lstrip('_')] = HistogramGetter.getHistogram(FILES[sel], (fs, SIGNALPOINTS[0]), tag).Clone()
                    for SP in SIGNALPOINTS[1:]:
                        HISTS[sel.lstrip('_')].Add(HistogramGetter.getHistogram(FILES[sel], (fs, SP), tag))
        else:
            FILES[SEL].cd()
            for tag in htags:
                HISTS[tag] = HistogramGetter.getHistogram(FILES[SEL], (fs, SIGNALPOINTS[0]), tag).Clone()
                for SP in SIGNALPOINTS[1:]:
                    HISTS[tag].Add(HistogramGetter.getHistogram(FILES[SEL], (fs, SP), tag))

        return HISTS

    def getDenHist(SIG4, SEL=None):
        DENS = {}
        if SEL is None:
            for sel in SELS:
                FILES[sel].cd()
                htags = [quantity+'_All-4' if SIG4 else quantity+'_All']
                for tag in htags:
                    DENS[sel.lstrip('_')] = HistogramGetter.getHistogram(FILES[sel], (fs, SIGNALPOINTS[0]), tag).Clone()
                    for SP in SIGNALPOINTS[1:]:
                        DENS[sel.lstrip('_')].Add(HistogramGetter.getHistogram(FILES[sel], (fs, SP), tag))
        else:
            FILES[SEL].cd()
            if SIG4 is None:
                htags = [quantity+'_All', quantity+'_All-4']
                for tag in htags:
                    DENS[tag] = HistogramGetter.getHistogram(FILES[SEL], (fs, SIGNALPOINTS[0]), tag).Clone()
                    for SP in SIGNALPOINTS[1:]:
                        DENS[tag].Add(HistogramGetter.getHistogram(FILES[SEL], (fs, SP), tag))
            else:
                htags = [quantity+'_All-4' if SIG4 else quantity+'_All']
                for tag in htags:
                    DENS['All'] = HistogramGetter.getHistogram(FILES[SEL], (fs, SIGNALPOINTS[0]), tag).Clone()
                    for SP in SIGNALPOINTS[1:]:
                        DENS['All'].Add(HistogramGetter.getHistogram(FILES[SEL], (fs, SP), tag))

        return DENS

    def proceed(HISTS, DENS, splitString):

        if len(HISTS) == 0:
            print splitString
            return

        for TAG in HISTS:
            HISTS[TAG].Rebin(5)
        for TAG in DENS:
            DENS[TAG].Rebin(5)

        if colorAxis == 'SEL':
            GRAPHS = {}
            for TAG in HISTS:
                GRAPHS[TAG] = R.TGraphAsymmErrors(HISTS[TAG], DENS[TAG], 'cp')
        elif colorAxis == 'SIG4':
            GRAPHS = {}
            for TAG in HISTS:
                if '-4' in TAG:
                    GRAPHS[TAG] = R.TGraphAsymmErrors(HISTS[TAG], DENS[quantity+'_All-4'], 'cp')
                else:
                    GRAPHS[TAG] = R.TGraphAsymmErrors(HISTS[TAG], DENS[quantity+'_All'  ], 'cp')
        else:
            GRAPHS = {TAG:R.TGraphAsymmErrors(HISTS[TAG], DENS['All'], 'cp') for TAG in HISTS}

        if colorAxis == 'CRIT':
            ORDER = ['' for i in range(len(GRAPHS))]
            ORDERMAP = {'Chi2':0, 'C2S':1, 'LCD':2, 'AMD':3}
            LEGS = {}
            COLMAP = {'Chi2':R.kBlue, 'C2S':R.kBlack, 'LCD':R.kGreen, 'AMD':R.kRed}
            COLS = {}
            for TAG in GRAPHS:
                kernel = re.match(r'.*(Chi2|LCD|AMD|C2S)',TAG).group(1)
                LEGS[TAG] = kernel
                COLS[TAG] = COLMAP[kernel]
                ORDER[ORDERMAP[kernel]] = TAG
        elif colorAxis == 'SEL':
            ORDER = ['', '4Reco', '5GeV', '4Reco_5GeV']
            LEGS = {'':'NoSel' , '4Reco':'4Reco', '5GeV':'5GeV', '4Reco_5GeV':'4Reco+5GeV'}
            COLS = {'':R.kBlack, '4Reco':R.kBlue, '5GeV':R.kRed, '4Reco_5GeV':R.kViolet}
        elif colorAxis == 'SIG4':
            ORDER = ['' for i in range(len(GRAPHS))]
            LEGS = {}
            COLS = {}
            for TAG in GRAPHS:
                if '-4' in TAG:
                    ORDER[0] = TAG
                    LEGS[TAG] = '2 sig match'
                    COLS[TAG] = R.kBlue
                else:
                    ORDER[1] = TAG
                    LEGS[TAG] = '#leq 2 sig match'
                    COLS[TAG] = R.kRed
        elif colorAxis == 'OC':
            ORDER = ['' for i in range(len(GRAPHS))]
            LEGS = {}
            COLS = {}
            for TAG in GRAPHS:
                if '-OC' in TAG:
                    ORDER[1] = TAG
                    LEGS[TAG] = 'opp. charge'
                    COLS[TAG] = R.kBlue
                else:
                    ORDER[0] = TAG
                    LEGS[TAG] = 'all pairs'
                    COLS[TAG] = R.kRed

        p = {TAG:Plotter.Plot(GRAPHS[TAG], LEGS[TAG], 'l', 'px') for TAG in GRAPHS}
        canvas = Plotter.Canvas(lumi='4Mu')
        for TAG in ORDER:
            canvas.addMainPlot(p[TAG])
            p[TAG].setColor(COLS[TAG], which='LM')
        canvas.firstPlot.SetMaximum(1.)
        canvas.firstPlot.SetMinimum(0.)
        canvas.firstPlot.GetXaxis().SetRangeUser(0., 330.)
        canvas.firstPlot.setTitles(Y='Efficiency',X=HISTS[HISTS.keys()[0]].GetXaxis().GetTitle())
        canvas.makeLegend(lWidth=.2, pos='br')
        canvas.legend.resizeHeight()
        canvas.cleanup('pdfs/LCD_Combo-{}_{}_HTo2XTo4Mu_Global.pdf'.format(colorAxis, splitString))


    if   colorAxis == 'SEL':
        # loop over the correct sub-axes
        for SEL in (1,):
            for CRIT in CRITS:
                for OC in OCS:
                    for SIG4 in SIG4S:
                        # htags is length 1 (but there will be 4 plots)
                        htags = [quantity+'_'+tag.tag+'_Matched' for tag in HTAGS if tag.oc == OC and tag.sig4 == SIG4 and tag.crit == CRIT]
                        # in colorAxis=SEL mode, use the SELS as tags instead
                        HISTS = makeHists(htags)
                        # in colorAxis=SIG4 mode, there are 4 DENs
                        DENS = getDenHist(SIG4)
                        splitString = '{CRIT}_{OC}_{SIG4}'.format(CRIT=CRIT, OC='OC' if OC else 'NOC', SIG4='4S' if SIG4 else 'NO4S')
                        proceed(HISTS, DENS, splitString)
    elif colorAxis == 'CRIT':
        # loop over the correct sub-axes
        for SEL in SELS:
            for CRIT in (1,):
                for OC in OCS:
                    for SIG4 in SIG4S:
                        # htags is length 3 or 4
                        htags = [quantity+'_'+tag.tag+'_Matched' for tag in HTAGS if tag.oc == OC and tag.sig4 == SIG4                     ]
                        HISTS = makeHists(htags, SEL)
                        DENS = getDenHist(SIG4, SEL)
                        splitString = '{SEL}_{OC}_{SIG4}'.format(SEL=PRETTYSEL[SEL], OC='OC' if OC else 'NOC', SIG4='4S' if SIG4 else 'NO4S')
                        proceed(HISTS, DENS, splitString)
    elif colorAxis == 'SIG4':
        # loop over the correct sub-axes
        for SEL in SELS:
            for CRIT in CRITS:
                for OC in OCS:
                    for SIG4 in (1,):
                        # htags is length 2
                        htags = [quantity+'_'+tag.tag+'_Matched' for tag in HTAGS if tag.oc == OC and                      tag.crit == CRIT]
                        HISTS = makeHists(htags, SEL)
                        # in colorAxis=SIG4 mode, there are 2 DENs
                        DENS = getDenHist(None, SEL)
                        splitString = '{SEL}_{CRIT}_{OC}'.format(SEL=PRETTYSEL[SEL], CRIT=CRIT, OC='OC' if OC else 'NOC')
                        proceed(HISTS, DENS, splitString)
    elif colorAxis == 'OC':
        # loop over the correct sub-axes
        for SEL in SELS:
            for CRIT in CRITS:
                for OC in (1,):
                    for SIG4 in SIG4S:
                        # htags is length 2
                        htags = [quantity+'_'+tag.tag+'_Matched' for tag in HTAGS if                  tag.sig4 == SIG4 and tag.crit == CRIT]
                        HISTS = makeHists(htags, SEL)
                        DENS = getDenHist(SIG4, SEL)
                        splitString = '{SEL}_{CRIT}_{SIG4}'.format(SEL=PRETTYSEL[SEL], CRIT=CRIT, SIG4='4S' if SIG4 else 'NO4S')
                        proceed(HISTS, DENS, splitString)

for fs in ('4Mu',):
    for sp in [None] + SIGNALPOINTS:
        for quantity in QUANTITIES:
            for criteria in CRITERIA:
                makeDistPlot(quantity, criteria, fs, sp)
                makeEffPlot(quantity, criteria, fs, sp)
makeComboPlots('GLxy', 'CRIT')
makeComboPlots('GLxy', 'SEL')
makeComboPlots('GLxy', 'SIG4')
makeComboPlots('GLxy', 'OC')
