import re
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.Selections as Selections
from DisplacedDimuons.Common.Utilities import SPStr
import HistogramGetter

# get histograms
HISTS = HistogramGetter.getHistograms('../analyzers/roots/TailCumulativePlots.root')
f = R.TFile.Open('../analyzers/roots/TailCumulativePlots.root')

# make per signal plots
def makePerSignalPlots():
    for ref in HISTS:
        for key in HISTS[ref]:
            if type(ref) == tuple:
                if ref[0] == '4Mu': name = 'HTo2XTo4Mu_'
                elif ref[0] == '2Mu2J' : name = 'HTo2XTo2Mu2J_'
                name += SPStr(ref[1])
                lumi = '{} ({} GeV, {} GeV, {} mm)'.format(ref[0], *ref[1])
            else:
                name = ref
                lumi = ref

            h = HISTS[ref][key]
            p = Plotter.Plot(h, 'H#rightarrow2X#rightarrow4#mu MC', 'l', 'hist')
            fname = 'pdfs/TCUM_{}_{}.pdf'.format(key.rstrip('_TCUM'), name)
            canvas = Plotter.Canvas(lumi=lumi)
            canvas.lumi += ' : |#Delta#Phi| ' + ('<' if '_Less' in key else '>') + ' #pi/2'
            canvas.addMainPlot(p)
            canvas.makeLegend(lWidth=.25, pos='tr')
            canvas.legend.moveLegend(Y=-.3)
            canvas.legend.resizeHeight()
            p.SetLineColor(R.kBlue)

            cutKey = key.replace('_Less','').replace('_More','').rstrip('_TCUM')
            cutVal = Selections.CUTS[cutKey].val

            l = R.TLine(cutVal, p.GetMinimum(), cutVal, p.GetMaximum()*1.05)
            l.SetLineStyle(2)
            l.SetLineWidth(2)
            l.Draw()

            canvas.cleanup(fname)

makePerSignalPlots()
