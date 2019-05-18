import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.HistogramGetter as HG
import DisplacedDimuons.Analysis.RootTools as RT

FILES = {
    'MC'    : R.TFile.Open('RepEffect_MC.root'),
    'Signal': R.TFile.Open('Resolutions_2Mu2J.root'),
}

def makeRepEffectPlots(hkey):
    HISTS, PConfig = HG.getBackgroundHistograms(FILES['MC'], hkey)
    HISTS = HISTS[hkey]
    PConfig = PConfig[hkey]

    PLOTS = {}
    for key in HG.BGORDER + ('stack',):
        PLOTS[key] = Plotter.Plot(HISTS[key], *PConfig[key])

    canvas = Plotter.Canvas(lumi='MC, {} replacement'.format(hkey), logy=True)

    for key in HG.BGORDER:
        PLOTS[key].setColor(HG.PLOTCONFIG[key]['COLOR'], which='LF')

    canvas.addMainPlot(PLOTS['stack'])

    canvas.firstPlot.setTitles(X='', copy=PLOTS[HG.BGORDER[0]])
    canvas.firstPlot.setTitles(Y='Normalized Counts')
    canvas.makeLegend(lWidth=.27, pos='tr', autoOrder=False, fontscale=0.8)
    for ref in reversed(HG.BGORDER):
        canvas.addLegendEntry(PLOTS[ref])
    canvas.legend.resizeHeight()
    RT.addBinWidth(canvas.firstPlot)

    canvas.firstPlot.SetMaximum(10.**7.)
    canvas.firstPlot.SetMinimum(10.**0.)
    canvas.cleanup('RepEffect_MC_{}.pdf'.format(hkey))

def makeResPlots(metric, quantity):
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
    witches = ('less', 'more')
    hkeys = ['{}_{}_{}'.format(metric, quantity, which) for which in witches]

    HISTS = HG.getAddedSignalHistograms(FILES['Signal'], '2Mu2J', hkeys)

    PLOTS = {}
    for key in hkeys:
        HISTS[key].Scale(1./HISTS[key].Integral(0, HISTS[key].GetNbinsX()+1))
        RT.addFlows(HISTS[key])
        PLOTS[key] = Plotter.Plot(HISTS[key], PRETTY[key]['leg'], 'l', 'hist')
    
    canvas = Plotter.Canvas(lumi='{} by {}'.format(PRETTY[hkeys[0]]['mnice'], PRETTY[hkeys[0]]['qnice']))

    for key in hkeys:
        canvas.addMainPlot(PLOTS[key])
        PLOTS[key].setColor(PRETTY[key]['col'], which='L')

    canvas.firstPlot.SetMinimum(0.)
    canvas.firstPlot.SetMaximum(0.08 if metric == 'pTRes' else 1.)

    canvas.firstPlot.setTitles(Y='Density')
    if 'qdiff' in hkeys[0]:
        canvas.firstPlot.SetNdivisions(3)

    canvas.makeLegend(lWidth=0.27, pos='tr')
    
    RT.addBinWidth(canvas.firstPlot)
    canvas.cleanup('Res_Sig_{}_{}.pdf'.format(metric, quantity))

makeRepEffectPlots('before')
makeRepEffectPlots('after')
makeResPlots('pTRes', 'hits')
makeResPlots('pTRes', 'fpte')
makeResPlots('qdiff', 'hits')
makeResPlots('qdiff', 'fpte')
