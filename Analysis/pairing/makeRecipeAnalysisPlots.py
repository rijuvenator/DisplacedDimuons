import re
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
from DisplacedDimuons.Common.Utilities import SPStr, SPLumiStr
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
import DisplacedDimuons.Analysis.HistogramGetter as HistogramGetter
import DisplacedDimuons.Analysis.PlotterParser as PlotterParser

ARGS = PlotterParser.PARSER.parse_args()
f = R.TFile.Open('roots/Main/RecipeAnalysisPlots_Trig{}.root'.format(ARGS.CUTSTRING))

hnames = ('Triggers', 'Events', 'Matches', 'Correct')
mnames = ('All', '2', '3', '4')
keysM = ('Events', 'Matches', 'Correct', 'Signal')
keysE = mnames
colors = (R.kBlack, R.kBlue, R.kRed, R.kGreen)

def makeEffPlot(key, colorAxis, fs, sp):

    config = {
        'Events'  : ('Events' , 'Triggers'),
        'Matches' : ('Matches', 'Events'  ),
        'Correct' : ('Correct', 'Matches' ),
        'Signal'  : ('Matches', None      ),
    }
    if colorAxis == 'nMuons':
        num, den = config[key]

        if den is None:
            tags = ('nMatches_All',)
            nums, dens = ['nMatches_All'], [None]
            legs = {'nMatches_All':'All'}
            cols = {'nMatches_All':R.kBlue}
        else:
            nums = ['n'+num+'_'+m for m in mnames]
            dens = ['n'+den+'_'+m for m in mnames]
            tags = list(set(nums + dens))
            legs = {num:m if 'All' in m else m+' #mu' for num,m in zip(nums,mnames)}
            cols = {num:c for num,c in zip(nums,colors)}

    elif colorAxis == 'Eff':
        nums = []
        dens = []
        for k in keysM:
            if k == 'Signal': continue
            nums.append('n'+config[k][0]+'_'+key)
            dens.append('n'+config[k][1]+'_'+key)
        tags = list(set(nums + dens))
        legs = {num:k for num,k in zip(nums,keysM)}
        cols = {num:c for num,c in zip(nums,colors)}

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
    graphs = {}
    for num, den in zip(nums,dens):
        if den is None:
            scaledH = h[num].Clone()
            scaledH.Scale(1./scaledH.GetBinContent(1))
            p[num] = Plotter.Plot(scaledH, legs[num], 'l', 'hist p')
        else:
            realDen = h[den].Clone()
            if fs == '4Mu' and 'Matches' in num and 'Events' in den:
                realDen.Scale(2.)
            graphs[num] = R.TGraphAsymmErrors(h[num], realDen, 'cp')
            p     [num] = Plotter.Plot(graphs[num], legs[num], 'l', 'px')

    canvas = Plotter.Canvas(lumi=SPLumiStr(fs, sp) if sp is not None else fs)
    for tag in nums:
        canvas.addMainPlot(p[tag])
    canvas.firstPlot.SetMaximum(1.01)
    canvas.firstPlot.SetMinimum(0.)
    canvas.firstPlot.setTitles(X=h[tags[0]].GetXaxis().GetTitle(), Y='Efficiency')
    for tag in p:
        p[tag].setColor(cols[tag], which='LM')

    canvas.makeLegend(lWidth=.275, pos='tr')
    canvas.legend.resizeHeight()

    canvas.cleanup('pdfs/RA_{}-{}{}_HTo2XTo{}_{}.pdf'.format('ComboMu' if colorAxis=='nMuons' else 'ComboEff', key, ARGS.CUTSTRING, fs, SPStr(sp) if sp is not None else 'Global'))

def makeStackPlot(key, colorAxis, fs, sp):

    if colorAxis == 'nMuons':
        tags = ['n'+key+'_'+m for m in mnames[1:]]
        legs = {tag:m+' #mu' for tag,m in zip(tags,mnames[1:])}
        cols = {tag:R.kRed+i for i,tag in enumerate(tags)}

    elif colorAxis == 'Eff':
        tags = ['n'+k+'_'+key for k in hnames[1:]]
        legs = {tag:k for tag,k in zip(tags,hnames[1:])}
        cols = {tag:c for tag,c in zip(tags,colors[1:])}

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

    h['stack'] = R.THStack('hBG'+key, '')
    p = {}
    for tag in tags:
        if fs == '4Mu' and 'Event' in tag and colorAxis == 'Eff':
            h[tag].Scale(2.)
        h['stack'].Add(h[tag])
    p['stack'] = Plotter.Plot(h['stack'], '', '' , 'hist' if colorAxis=='nMuons' else 'nostack')
    for tag in tags:
        p[tag] = Plotter.Plot(h[tag    ], legs[tag], 'f', 'hist')

    for tag in tags:
        p[tag].setColor(cols[tag], which='LMF')

    canvas = Plotter.Canvas(lumi=SPLumiStr(fs, sp) if sp is not None else fs)
    for tag in ('stack',):
        canvas.addMainPlot(p[tag])
    if colorAxis == 'nMuons':
        canvas.setMaximum(recompute=True)
    canvas.firstPlot.SetMinimum(0.)
    canvas.makeLegend(lWidth=.2, pos='tr', autoOrder=False)
    canvas.firstPlot.setTitles(X=h[tags[0]].GetXaxis().GetTitle(),Y='Counts')
    for tag in tags:
        canvas.addLegendEntry(p[tag])
    canvas.legend.resizeHeight()

    canvas.cleanup('pdfs/RA_{}-{}{}_HTo2XTo{}_{}.pdf'.format('StackMu' if colorAxis=='nMuons' else 'StackEff', key, ARGS.CUTSTRING, fs, sp if sp is not None else 'Global'))

def makeLxyEffPlot(key, colorAxis, fs, sp, pTCut=''):

    config = {
        'Correct' : ('Correct', 'Matches' ),
    }
    if colorAxis == 'nMuons':
        num, den = config[key]

        nums = ['Lxy'+pTCut+'_n'+num+'_'+m for m in mnames]
        dens = ['Lxy'+pTCut+'_n'+den+'_'+m for m in mnames]
        tags = list(set(nums + dens))
        legs = {num:m if 'All' in m else m+' #mu' for num,m in zip(nums,mnames)}
        cols = {num:c for num,c in zip(nums,colors)}

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

    for z in h:
        h[z].Rebin(10)

    p = {}
    graphs = {}
    for num, den in zip(nums,dens):
        realDen = h[den].Clone()
        graphs[num] = R.TGraphAsymmErrors(h[num], realDen, 'cp')
        p     [num] = Plotter.Plot(graphs[num], legs[num], 'l', 'px')

    canvas = Plotter.Canvas(lumi=SPLumiStr(fs, sp) if sp is not None else fs)
    for tag in nums:
        canvas.addMainPlot(p[tag])
    canvas.firstPlot.SetMaximum(1.01)
    canvas.firstPlot.SetMinimum(0.)
    canvas.firstPlot.setTitles(X=h[tags[0]].GetXaxis().GetTitle(), Y='Efficiency')
    for tag in p:
        p[tag].setColor(cols[tag], which='LM')

    canvas.makeLegend(lWidth=.275, pos='tr')
    canvas.legend.resizeHeight()

    canvas.cleanup('pdfs/RA_{}-Lxy{}-{}{}_HTo2XTo{}_{}.pdf'.format('ComboMu' if colorAxis=='nMuons' else 'ComboEff', pTCut, key, ARGS.CUTSTRING, fs, SPStr(sp) if sp is not None else 'Global'))

for fs in ('4Mu', '2Mu2J'):
    for sp in [None] + SIGNALPOINTS:
        for key in keysM:
            makeEffPlot(key, 'nMuons', fs, sp)
        for key in keysE:
            makeEffPlot(key, 'Eff', fs, sp)
        for key in hnames[1:]:
            makeStackPlot(key, 'nMuons', fs, sp)
        for key in mnames:
            makeStackPlot(key, 'Eff', fs, sp)

        if fs == '2Mu2J':
            makeLxyEffPlot('Correct', 'nMuons', fs, sp)
            makeLxyEffPlot('Correct', 'nMuons', fs, sp, '5')
