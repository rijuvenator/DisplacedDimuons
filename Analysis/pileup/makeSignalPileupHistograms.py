import numpy as np
import ROOT as R
import DisplacedDimuons.Analysis.HistogramGetter as HG
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.PlotterParser as PP

PP.PARSER.add_argument('--thesis', dest='THESIS', action='store_true')
ARGS = PP.PARSER.parse_args()

##################################
#### Get histograms and scale ####
##################################

FILES = {
    'DataNom' : R.TFile.Open('roots/MyDataPileupHistogram.root'),
    'DataLow' : R.TFile.Open('roots/MyDataPileupHistogram_Low.root'),
    'DataHigh': R.TFile.Open('roots/MyDataPileupHistogram_High.root'),
    'Signal'  : R.TFile.Open('roots/pileup_HTo2XTo2Mu2J.root'),
}

HISTS, INDIV = HG.getAddedSignalHistograms(FILES['Signal'], '2Mu2J', 'pileup', True)
HISTS, INDIV = HISTS['pileup'], INDIV['pileup']

KEYS = ('Nom', 'Low', 'High')

DATA = {key:FILES['Data'+key].Get('pileup').Clone() for key in KEYS}

for key in DATA:
    DATA[key].Scale(1./DATA[key].Integral())

for sp in INDIV:
    INDIV[sp].Scale(1./INDIV[sp].Integral())

HISTS.Scale(1./HISTS.Integral())

# saves the weight for a printing pass afterwards
# so that WEIGHTS doesn't have to be a multidimensional dict
printWeights = {key:[] for key in KEYS}

for key in KEYS:

    ##########################################
    #### Make a graph of the distributions ###
    ##########################################

    x, y, ylow, yhigh = [], [], [], []
    for ibin in xrange(1,101):
        x.append(ibin+.5)
        
        high = -HISTS.GetBinContent(ibin) + max([INDIV[sp].GetBinContent(ibin) for sp in INDIV])
        low  =  HISTS.GetBinContent(ibin) - min([INDIV[sp].GetBinContent(ibin) for sp in INDIV])
        mid  =  HISTS.GetBinContent(ibin)

        y.append(mid)
        ylow.append(low)
        yhigh.append(high)

    GRAPH = R.TGraphAsymmErrors(len(x), np.array(x), np.array(y), np.array([.5]*len(x)), np.array([.5]*len(x)), np.array(ylow), np.array(yhigh))

    p = {
        'Signal' : Plotter.Plot(GRAPH        , '2#mu signal: bounds'    , 'f' , 'e3'),
        'SigMid' : Plotter.Plot(GRAPH.Clone(), '2#mu signal: combined'  , 'l' , 'lx'),
        'Data'   : Plotter.Plot(DATA[key]    , 'Data, 2016 Re-Reco Muon', 'lp', 'p' ),
    }

    c = Plotter.Canvas(lumi = key + ('' if key != 'Nom' else 'inal'), cWidth=600 if ARGS.THESIS else 800)
    c.addMainPlot(p['Signal'])
    c.addMainPlot(p['SigMid'])
    c.addMainPlot(p['Data'])

    p['Signal'].setColor(R.kOrange, which='FL')
    p['SigMid'].plot.SetLineColor(R.kRed)

    c.makeLegend(lWidth=.4)
    c.legend.resizeHeight()
    c.legend.SetMargin(.15)

    c.firstPlot.setTitles(X='N(true primary vertices)', Y='Density')
    c.firstPlot.GetXaxis().SetRangeUser(0., 100.)

    if ARGS.THESIS:
        c.legend.moveLegend(X=-.1)
        c.firstPlot.scaleTitleOffsets(1.1, 'XY')
    c.cleanup('pdfs/distribution{}.pdf'.format(key), mode='LUMI' if ARGS.THESIS else None)

    #####################################
    #### Make a graph of the weights ####
    #####################################

    WEIGHTS = {}
    WEIGHTS['total'] = DATA[key].Clone()
    WEIGHTS['total'].Divide(HISTS)
    for sp in INDIV:
        WEIGHTS[sp] = DATA[key].Clone()
        WEIGHTS[sp].Divide(INDIV[sp])

    x, y, ylow, yhigh = [], [], [], []
    for ibin in xrange(1,101):
        x.append(ibin+.5)
        
        high = -WEIGHTS['total'].GetBinContent(ibin) + max([WEIGHTS[sp].GetBinContent(ibin) for sp in INDIV])
        low  =  WEIGHTS['total'].GetBinContent(ibin) - min([WEIGHTS[sp].GetBinContent(ibin) for sp in INDIV])
        mid  =  WEIGHTS['total'].GetBinContent(ibin)

        printWeights[key].append(mid)

        y.append(mid)
        ylow.append(low)
        yhigh.append(high)

    GRAPH = R.TGraphAsymmErrors(len(x), np.array(x), np.array(y), np.array([.5]*len(x)), np.array([.5]*len(x)), np.array(ylow), np.array(yhigh))

    p = {
        'Signal' : Plotter.Plot(GRAPH        , '2#mu signal: bounds'      , 'f' , 'e3'),
        'SigMid' : Plotter.Plot(GRAPH.Clone(), '2#mu signal: combined'    , 'lp', 'px'),
    }

    c = Plotter.Canvas(lumi = key + ('' if key != 'Nom' else 'inal'), cWidth=600 if ARGS.THESIS else 800)
    c.addMainPlot(p['Signal'])
    c.addMainPlot(p['SigMid'])

    p['Signal'].setColor(R.kOrange, which='FL')
    p['SigMid'].setColor(R.kRed, which='LM')

    c.makeLegend(lWidth=.3)
    c.legend.resizeHeight()
    c.legend.SetMargin(.15)

    c.firstPlot.setTitles(X='N(true primary vertices)', Y='Event Weight')
    c.firstPlot.GetXaxis().SetRangeUser(0., 100.)
    c.firstPlot.SetMaximum(2.)

    if ARGS.THESIS:
        c.legend.moveLegend(X=-.1)
        c.firstPlot.scaleTitleOffsets(1.1, 'XY')
    c.cleanup('pdfs/weight{}.pdf'.format(key), mode='LUMI' if ARGS.THESIS else None)


#######################
#### Print weights ####
#######################

for ibin in xrange(100):
    print '{:3d} : {:7.5f} {:7.5f} {:7.5f}'.format(ibin, *[printWeights[key][ibin] for key in KEYS])
