import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.HistogramGetter as HG
import DisplacedDimuons.Analysis.RootTools as RT
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
from DisplacedDimuons.Common.Utilities import SPStr
import DisplacedDimuons.Analysis.PlotterParser as PP

PP.PARSER.add_argument('--square', dest='SQUARE', action='store_true')
ARGS = PP.PARSER.parse_args()

FILES = {
    'MC'    : R.TFile.Open('roots/RepEffectPlots_MC.root'),
    'Signal': R.TFile.Open('roots/Resolutions_2Mu2J.root'),
}

def makeRepEffectPlots(hkey):
    HISTS, PConfig = HG.getBackgroundHistograms(FILES['MC'], hkey)
    HISTS = HISTS[hkey]
    PConfig = PConfig[hkey]

    PLOTS = {}
    for key in HG.BGORDER + ('stack',):
        PLOTS[key] = Plotter.Plot(HISTS[key], *PConfig[key])

    canvas = Plotter.Canvas(lumi='MC Background, {} PAT association (36.3 fb^{{-1}})'.format(hkey.replace('LxySig-','').replace('Lxy-','')), logy=True, cWidth=600 if ARGS.SQUARE else 800)

    for key in HG.BGORDER:
        PLOTS[key].setColor(HG.PLOTCONFIG[key]['COLOR'], which='LF')

    canvas.addMainPlot(PLOTS['stack'])

    canvas.firstPlot.setTitles(X='', copy=PLOTS[HG.BGORDER[0]])
    canvas.firstPlot.setTitles(Y='Event Yield')
    canvas.makeLegend(lWidth=.3, pos='tr', autoOrder=False, fontscale=0.8)
    for ref in reversed(HG.BGORDER):
        canvas.addLegendEntry(PLOTS[ref])
    canvas.legend.resizeHeight()
    RT.addBinWidth(canvas.firstPlot)

    canvas.firstPlot.SetMaximum(10.**7.)
    canvas.firstPlot.SetMinimum(10.**0.)

    if ARGS.SQUARE:
        canvas.firstPlot.scaleTitleOffsets(1.1, 'X')

    z = PLOTS['stack'].plot.GetStack().Last()
    print 'MC', hkey, z.Integral(0, z.GetNbinsX()+1)
    canvas.cleanup('pdfs/REPEFF_MC_{}.pdf'.format(hkey), mode='LUMI')

def makeResPlots(metric, quantity, sp=None):
    PRETTY = {
            'pTRes_hits_less' : {'mnice':'p_{T} res.'  , 'qnice':'N(hits)'             , 'leg':'N(hits) #leq 12'            , 'col':R.kRed },
            'pTRes_hits_more' : {'mnice':'p_{T} res.'  , 'qnice':'N(hits)'             , 'leg':'N(hits) > 12'               , 'col':R.kBlue},
            'pTRes_fpte_less' : {'mnice':'p_{T} res.'  , 'qnice':'#sigma_{p_{T}}/p_{T}', 'leg':'#sigma_{p_{T}}/p_{T} < 1'   , 'col':R.kBlue},
            'pTRes_fpte_more' : {'mnice':'p_{T} res.'  , 'qnice':'#sigma_{p_{T}}/p_{T}', 'leg':'#sigma_{p_{T}}/p_{T} #geq 1', 'col':R.kRed },
            'qdiff_hits_less' : {'mnice':'charge diff.', 'qnice':'N(hits)'             , 'leg':'N(hits) #leq 12'            , 'col':R.kRed },
            'qdiff_hits_more' : {'mnice':'charge diff.', 'qnice':'N(hits)'             , 'leg':'N(hits) > 12'               , 'col':R.kBlue},
            'qdiff_fpte_less' : {'mnice':'charge diff.', 'qnice':'#sigma_{p_{T}}/p_{T}', 'leg':'#sigma_{p_{T}}/p_{T} < 1'   , 'col':R.kBlue},
            'qdiff_fpte_more' : {'mnice':'charge diff.', 'qnice':'#sigma_{p_{T}}/p_{T}', 'leg':'#sigma_{p_{T}}/p_{T} #geq 1', 'col':R.kRed },
    }
    witches = ('less', 'more') if quantity == 'fpte' else ('more', 'less')
    hkeys = ['{}_{}_{}'.format(metric, quantity, which) for which in witches]

    if sp is None:
        HISTS = HG.getAddedSignalHistograms(FILES['Signal'], '2Mu2J', hkeys)
    else:
        HISTS = {}
        for key in hkeys:
            HISTS[key] = HG.getHistogram(FILES['Signal'], ('2Mu2J', sp), key).Clone()

    PLOTS = {}
    for key in hkeys:
        HISTS[key].Scale(1./HISTS[key].Integral(0, HISTS[key].GetNbinsX()+1))
        #RT.addFlows(HISTS[key])
        PLOTS[key] = Plotter.Plot(HISTS[key], PRETTY[key]['leg'], 'l', 'hist')
    
    #canvas = Plotter.Canvas(lumi='{} by {}'.format(PRETTY[hkeys[0]]['mnice'], PRETTY[hkeys[0]]['qnice']))
    lumi = 'H#rightarrow2X#rightarrow2#mu'
    if sp is None:
        lumi += ', all samples combined'
    else:
        lumi += ' ({} GeV, {} GeV, {} mm)'.format(*sp)
    canvas = Plotter.Canvas(lumi=lumi, cWidth=600 if ARGS.SQUARE else 800)

    for key in hkeys:
        canvas.addMainPlot(PLOTS[key])
        PLOTS[key].setColor(PRETTY[key]['col'], which='L')

    canvas.firstPlot.SetMinimum(0.)
    canvas.setMaximum()
    if metric == 'qdiff':
        canvas.firstPlot.SetMaximum(1.)

    canvas.firstPlot.setTitles(Y='Density')
    if 'qdiff' in hkeys[0]:
        canvas.firstPlot.SetNdivisions(3)

    canvas.makeLegend(lWidth=0.27, pos='tr')
    canvas.legend.resizeHeight()
    
    RT.addBinWidth(canvas.firstPlot)

    if ARGS.SQUARE:
        canvas.firstPlot.scaleTitleOffsets(1.1, 'X')
        if metric == 'pTRes':
            canvas.firstPlot.scaleTitleOffsets(1.3, 'Y')
    canvas.cleanup('pdfs/QCUTRES_Sig_{}_{}_{}.pdf'.format(metric, quantity, 'Global' if sp is None else SPStr(sp)), mode='LUMI')

makeRepEffectPlots('Lxy-before')
makeRepEffectPlots('Lxy-after')
makeRepEffectPlots('LxySig-before')
makeRepEffectPlots('LxySig-after')
for sp in [(1000, 350, 350)] + [None]:
    makeResPlots('pTRes', 'hits', sp)
    makeResPlots('pTRes', 'fpte', sp)
    makeResPlots('qdiff', 'hits', sp)
    makeResPlots('qdiff', 'fpte', sp)
