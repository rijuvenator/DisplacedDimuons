import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Common.Utilities as Utilities

PATSIGNALPOINTS = ((125, 20, 13), (1000, 150, 1000))

f = R.TFile.Open('roots/LxyEffTest.root')
HISTS = {}
for sp in PATSIGNALPOINTS:
    HISTS[sp] = {}
    for TYPE in ('OLD', 'NEW'):
        HISTS[sp][TYPE] = {}
        for plot in ('LxyEff', 'LxyDen'):
            HISTS[sp][TYPE][plot] = f.Get(plot+TYPE+'_HTo2XTo2Mu2J_'+Utilities.SPStr(sp))
            HISTS[sp][TYPE][plot].SetDirectory(0)

def makeDistributions():
    for sp in PATSIGNALPOINTS:
        p = {}
        p['OLD'] = Plotter.Plot(HISTS[sp]['OLD']['LxyEff'], 'with constraint'   , 'l', 'hist')
        p['NEW'] = Plotter.Plot(HISTS[sp]['NEW']['LxyEff'], 'without constraint', 'l', 'hist')
        canvas = Plotter.Canvas(lumi='2Mu2J ({}, {}, {})'.format(*sp))
        canvas.addMainPlot(p['OLD'])
        canvas.addMainPlot(p['NEW'])
        canvas.makeLegend(lWidth=.3)
        canvas.legend.resizeHeight()
        canvas.setMaximum()
        canvas.firstPlot.setTitles(Y='Counts')
        p['OLD'].SetLineColor(R.kRed )
        p['NEW'].SetLineColor(R.kBlue)
        p['OLD'].SetMarkerColor(R.kRed )
        p['NEW'].SetMarkerColor(R.kBlue)
        canvas.cleanup('pdfs/Lxy_HTo2XTo2Mu2J_'+Utilities.SPStr(sp)+'.pdf')

def makeEfficiencies():
    for sp in PATSIGNALPOINTS:
        g = {}
        g['OLD'] = R.TGraphAsymmErrors(HISTS[sp]['OLD']['LxyEff'], HISTS[sp]['OLD']['LxyDen'])
        g['NEW'] = R.TGraphAsymmErrors(HISTS[sp]['NEW']['LxyEff'], HISTS[sp]['NEW']['LxyDen'])
        g['OLD'].SetNameTitle('g_OLD', ';'+HISTS[sp]['OLD']['LxyEff'].GetXaxis().GetTitle()+';'+HISTS[sp]['OLD']['LxyEff'].GetYaxis().GetTitle())
        g['NEW'].SetNameTitle('g_NEW', ';'+HISTS[sp]['NEW']['LxyEff'].GetXaxis().GetTitle()+';'+HISTS[sp]['NEW']['LxyEff'].GetYaxis().GetTitle())
        p = {}
        p['OLD'] = Plotter.Plot(g['OLD'], 'with constraint'   , 'pe', 'P')
        p['NEW'] = Plotter.Plot(g['NEW'], 'without constraint', 'pe', 'P')
        canvas = Plotter.Canvas(lumi='2Mu2J ({}, {}, {})'.format(*sp))
        canvas.addMainPlot(p['OLD'])
        canvas.addMainPlot(p['NEW'])
        canvas.makeLegend(lWidth=.3)
        canvas.legend.resizeHeight()
        canvas.setMaximum()
        p['OLD'].SetLineColor(R.kRed )
        p['NEW'].SetLineColor(R.kBlue)
        p['OLD'].SetMarkerColor(R.kRed )
        p['NEW'].SetMarkerColor(R.kBlue)
        canvas.cleanup('pdfs/LxyEff_HTo2XTo2Mu2J_'+Utilities.SPStr(sp)+'.pdf')

makeDistributions()
makeEfficiencies()
