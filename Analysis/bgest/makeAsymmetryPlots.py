import ROOT as R
import DisplacedDimuons.Analysis.HistogramGetter as HG
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT

f = R.TFile.Open('roots/Hists.root')

keyList = {
    'hLessLxySig'      : 'LxySig-SplitDPhi'        ,
    'hMoreLxySig'      : 'LxySig-SplitDPhi'        ,
    'hLessLxySigBig'   : 'LxySig-SplitDPhi-Big'    ,
    'hMoreLxySigBig'   : 'LxySig-SplitDPhi-Big'    ,
    'hLessLxySigEdges' : 'LxySig-SplitDPhi-Edges'  ,
    'hMoreLxySigEdges' : 'LxySig-SplitDPhi-Edges'  ,
    'hLessDeltaPhi'    : 'deltaPhi-SplitLxySig'    ,
    'hMoreDeltaPhi'    : 'deltaPhi-SplitLxySig'    ,
    'hLessDeltaPhiBig' : 'deltaPhi-SplitLxySig-Big',
    'hMoreDeltaPhiBig' : 'deltaPhi-SplitLxySig-Big',
    'hDeltaPhi'        : 'deltaPhi'                ,
    'hDeltaPhiBig'     : 'deltaPhi-Big'            ,
}

HISTS, PConfig = HG.getBackgroundHistograms(f, keyList.keys(), addFlows=False)
DHists = {}
for key in keyList:
    DHists[key] = HG.getHistogram(f, 'Data', key).Clone()

def makeSinglePlots(hkey, logy=True):
    PLOTS = {}
    for key in HG.BGORDER + ('stack',):
        PLOTS[key] = Plotter.Plot(HISTS[hkey][key], *PConfig[hkey][key])
    PLOTS['Data'] = Plotter.Plot(DHists[hkey], 'DoubleMuon2016', 'pe', 'pe')

    canvas = Plotter.Canvas(lumi='36.3 fb^{-1} (13 TeV)', logy=logy)

    for key in HG.BGORDER:
        PLOTS[key].setColor(HG.PLOTCONFIG[key]['COLOR'], which='LF')

    canvas.addMainPlot(PLOTS['stack'])
    canvas.addMainPlot(PLOTS['Data' ])

    canvas.firstPlot.setTitles(X='', copy=PLOTS[HG.BGORDER[0]])
    canvas.firstPlot.setTitles(Y='Event Yield')
    canvas.makeLegend(lWidth=.3, pos='tr', autoOrder=False, fontscale=0.8)
    for ref in reversed(HG.BGORDER):
        canvas.addLegendEntry(PLOTS[ref])
    canvas.legend.resizeHeight()
    RT.addBinWidth(canvas.firstPlot)

    if logy:
        canvas.firstPlot.SetMaximum(10.**7.)
        canvas.firstPlot.SetMinimum(10.**0.)
    else:
        if 'Big' in hkey:
            canvas.firstPlot.SetMaximum(1500.)
            canvas.firstPlot.SetMinimum(200. )
        else:
            canvas.firstPlot.SetMaximum(120000.)
            canvas.firstPlot.SetMinimum(30000. )

    z = PLOTS['stack'].GetStack().Last()

    paveData = canvas.makeStatsBox(PLOTS['Data'])
    Plotter.MOVE_OBJECT(paveData, X=-.55, Y=-.02)
    canvas.drawText('Data', pos=(paveData.GetX1(), paveData.GetY2()-.006), align='bl', fontcode='b')

    paveMC = canvas.makeStatsBox(z)
    Plotter.MOVE_OBJECT(paveMC, X=-.35, Y=-.02)
    canvas.drawText('MC', pos=(paveMC.GetX1(), paveMC.GetY2()-.006), align='bl', fontcode='b')

    canvas.cleanup('pdfs/{}_{}.pdf'.format(keyList[hkey], 'Lin' if not logy else 'Log'))

for hkey in ('hDeltaPhi', 'hDeltaPhiBig'):
    makeSinglePlots(hkey, logy=True)
    makeSinglePlots(hkey, logy=False)

def makeLessMorePlots(quantity, LxyRange, logy=True):
    legDict = {'Less':'<  #pi/4', 'More':'> 3#pi/4'}
    hkeys  = {key:'h{}{}{}'.format(key, quantity, LxyRange) for key in ('Less', 'More')}
    PLOTS  = {key:Plotter.Plot( HISTS[hkeys[key]]['stack'].GetStack().Last(), '  MC |#Delta#Phi| {}'.format(legDict[key]), 'l' , 'hist') for key in ('Less', 'More')}
    DPLOTS = {key:Plotter.Plot(DHists[hkeys[key]]                           , 'Data |#Delta#Phi| {}'.format(legDict[key]), 'pe', 'pe'  ) for key in ('Less', 'More')}

    canvas = Plotter.Canvas(lumi='36.3 fb^{-1} (13 TeV)', logy=logy)

    colors = {'Less':R.kRed, 'More':R.kBlue}
    for key in hkeys:
        canvas.addMainPlot(PLOTS [key])
        canvas.addMainPlot(DPLOTS[key])

        PLOTS [key].setColor(colors[key])
        DPLOTS[key].setColor(colors[key])

    canvas.firstPlot.setTitles(X='', copy=DHists[hkeys['Less']])
    canvas.firstPlot.setTitles(Y='Event Yield')
    canvas.makeLegend(lWidth=.3, pos='tr')
    canvas.legend.resizeHeight()
    RT.addBinWidth(canvas.firstPlot)

    if logy:
        canvas.firstPlot.SetMaximum(10.**7.)
        canvas.firstPlot.SetMinimum(10.**0.)
    else:
        if 'Big' in LxyRange:
            if quantity == 'LxySig':
                canvas.firstPlot.SetMaximum(10000.)
            else:
                canvas.firstPlot.SetMaximum(1400.)
            canvas.firstPlot.SetMinimum(0.)
        elif 'Edges' in LxyRange:
            canvas.firstPlot.SetMinimum(0.)
            canvas.firstPlot.SetMaximum(1000.)
        else:
            if quantity == 'LxySig':
                canvas.firstPlot.SetMaximum(1000000.)
            else:
                canvas.firstPlot.SetMaximum(120000.)
            canvas.firstPlot.SetMinimum(0.)

    for key in DPLOTS:
        print 'Data', key, DPLOTS[key].Integral(0,  PLOTS[key].GetNbinsX()+1)
    for key in PLOTS:
        print 'MC  ', key,  PLOTS[key].Integral(0, DPLOTS[key].GetNbinsX()+1)


    paveDataLess = canvas.makeStatsBox(DHists[hkeys['Less']], color=colors['Less'])
    Plotter.MOVE_OBJECT(paveDataLess, X=-.55, Y=-.02)
    canvas.drawText('Data SR', pos=(paveDataLess.GetX1(), paveDataLess.GetY2()-.006), align='bl', fontcode='b')

    paveMCLess = canvas.makeStatsBox(PLOTS['Less'], color=colors['Less'])
    Plotter.MOVE_OBJECT(paveMCLess, X=-.35, Y=-.02)
    canvas.drawText('MC SR', pos=(paveMCLess.GetX1(), paveMCLess.GetY2()-.006), align='bl', fontcode='b')

    paveDataMore = canvas.makeStatsBox(DHists[hkeys['More']], color=colors['More'])
    Plotter.MOVE_OBJECT(paveDataMore, X=-.55, Y=-.3)
    if paveDataMore.GetX1() != paveDataLess.GetX1():
        Plotter.MOVE_OBJECT(paveDataMore, X=-(paveDataMore.GetX1()-paveDataLess.GetX1()))
    canvas.drawText('Data CR', pos=(paveDataMore.GetX1(), paveDataMore.GetY2()-.006), align='bl', fontcode='b')

    paveMCMore = canvas.makeStatsBox(PLOTS['More'], color=colors['More'])
    Plotter.MOVE_OBJECT(paveMCMore, X=-.35, Y=-.3)
    if paveMCMore.GetX1() != paveMCLess.GetX1():
        Plotter.MOVE_OBJECT(paveMCMore, X=-(paveMCMore.GetX1()-paveMCLess.GetX1()))
    canvas.drawText('MC CR', pos=(paveMCMore.GetX1(), paveMCMore.GetY2()-.006), align='bl', fontcode='b')

    canvas.cleanup('pdfs/{}_{}.pdf'.format(keyList[hkeys['Less']], 'Lin' if not canvas.logy else 'Log'))

def makeRatioPlots(quantity, LxyRange):
    legDict = {'Less':'<  #pi/4', 'More':'> 3#pi/4'}
    hkeys  = {key:'h{}{}{}'.format(key, quantity, LxyRange) for key in ('Less', 'More')}

    a = HISTS[hkeys['Less']]['stack'].GetStack().Last().Clone()
    den = HISTS[hkeys['More']]['stack'].GetStack().Last().Clone()
    a.Rebin(2), den.Rebin(2)
    a.Divide(den)
    d = DHists[hkeys['Less']].Clone()
    den = DHists[hkeys['More']].Clone()
    d.Rebin(2), den.Rebin(2)
    d.Divide(den)

    PLOTS  = {'':Plotter.Plot(a, '  MC SR/CR', 'lp', 'hist p')}
    DPLOTS = {'':Plotter.Plot(d, 'Data SR/CR', 'lp', 'hist p')}

    canvas = Plotter.Canvas(lumi='36.3 fb^{-1} (13 TeV)', logy=False)

    colors = {'':R.kBlue}
    canvas.addMainPlot(PLOTS [''])
    canvas.addMainPlot(DPLOTS[''])

    PLOTS [''].setColor(R.kBlue)
    DPLOTS[''].setColor(R.kBlack)

    canvas.firstPlot.setTitles(X='', copy=DHists[hkeys['Less']])
    canvas.firstPlot.setTitles(Y='Event Yield')
    canvas.makeLegend(lWidth=.3, pos='tr')
    canvas.legend.resizeHeight()
    RT.addBinWidth(canvas.firstPlot)

    canvas.firstPlot.SetMaximum( 2.)
    canvas.firstPlot.SetMinimum(-1.)

    canvas.cleanup('pdfs/Ratio_{}_{}.pdf'.format(keyList[hkeys['Less']], 'Lin' if not canvas.logy else 'Log'))

for quantity in ('LxySig', 'DeltaPhi'):
    for LxyRange in ('', 'Big', 'Edges'):
        if LxyRange == 'Edges' and quantity != 'LxySig': continue
        makeLessMorePlots(quantity, LxyRange, logy=True)
        makeLessMorePlots(quantity, LxyRange, logy=False)
        makeRatioPlots(quantity, LxyRange)
