import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.HistogramGetter as HG

FILES = {
    'DATA' : R.TFile.Open('roots/RepPlots_DATA.root'),
    'MC'   : R.TFile.Open('roots/RepPlots_MC.root'  ),
}

for rtype in ('DSA', 'PAT'):
    HISTS = {
        #'MC' : HG.getHistogram(FILES['MC'], 'DY50toInf', 'n'+rtype).Clone(),
        #'MC' : HG.getHistogram(FILES['MC'], 'ttbar', 'n'+rtype).Clone(),
        'MC' : HG.getBackgroundHistograms(FILES['MC'  ], 'n'+rtype, stack=False, addFlows=False)[0]['n'+rtype]['stack'],
        'Da' : HG.getDataHistograms      (FILES['DATA'], 'n'+rtype, addFlows=False)[0]['n'+rtype]['data'],
    }

    for nDSA in xrange(2, 16):
        hMC = HISTS['MC'].ProjectionY('_py', nDSA+1, nDSA+1)
        hDa = HISTS['Da'].ProjectionY('_py', nDSA+1, nDSA+1)

        hMC.Scale(1./hMC.Integral() if hMC.Integral() != 0. else 1.)
        hDa.Scale(1./hDa.Integral() if hDa.Integral() != 0. else 1.)

        c = Plotter.Canvas(lumi='{} DSA muons'.format(nDSA), logy=True)
        #c = Plotter.Canvas(lumi='{} DSA muons'.format(nDSA))
        p = {
            'MC': Plotter.Plot(hMC, 'MC'  , 'l', 'hist'),
            'Da': Plotter.Plot(hDa, 'Data', 'l', 'hist'),
        }
        c.addMainPlot(p['MC'])
        c.addMainPlot(p['Da'])

        hMC.SetLineColor(R.kBlue)
        hDa.SetLineColor(R.kRed)

        c.makeLegend(lWidth=0.125)
        c.legend.resizeHeight()

        if rtype == 'DSA':
            c.firstPlot.setTitles(X='Number of not-replaced DSA muons', Y='Normalized Counts')
        else:
            c.firstPlot.setTitles(X='Number of PAT muons', Y='Normalized Counts')

        if c.logy:
            c.firstPlot.SetMaximum(2.)
            c.firstPlot.SetMinimum(1.e-5)
        else:
            c.firstPlot.SetMaximum(1.01)
            c.firstPlot.SetMinimum(0.00)

        pave1 = c.makeStatsBox(p['MC'], color=R.kBlue)
        pave2 = c.makeStatsBox(p['Da'], color=R.kRed )
        Plotter.MOVE_OBJECT(pave1, Y=-.1)
        Plotter.MOVE_OBJECT(pave2, Y=-.3)
        pave2.SetX1(pave1.GetX1())

        c.cleanup('n{}_{}.pdf'.format(rtype, nDSA))
