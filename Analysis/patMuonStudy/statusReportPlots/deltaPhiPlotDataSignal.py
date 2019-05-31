import ROOT as R
import numpy as np
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
from DisplacedDimuons.Common.Constants import BGORDER as BGORDER_REAL
import DisplacedDimuons.Analysis.Plotter as Plotter
from DisplacedDimuons.Common.Utilities import SPStr, SPLumiStr 
import DisplacedDimuons.Analysis.HistogramGetter as HG
import DisplacedDimuons.Analysis.RootTools as RT

CUTSTRING = 'NS_NH_FPTE_HLT_REP_PT_PC_LXYE_MASS_CHI2_VTX_COSA_SFPTE'

DRAW = False
if DRAW:
    R.gROOT.SetBatch(False)

FILES = {
    '2Mu2J' : R.TFile.Open('../../nMinusOne/roots/NM1Distributions_Trig_HTo2XTo2Mu2J.root'),
    'Data'  : R.TFile.Open('../roots/ZephyrPlots_Combined_{}_DATA.root'.format(CUTSTRING)),
}

def makeTestPlot():
    hkey = 'DSA-deltaPhi'
    HISTS = HG.getAddedSignalHistograms(FILES['2Mu2J'], '2Mu2J', ('deltaPhi',))
    DATAHISTS, DataPConfig = HG.getDataHistograms(FILES['Data'], hkey)

    HISTS[hkey] = HISTS['deltaPhi']

    pS = Plotter.Plot(HISTS[hkey], 'H#rightarrow2X#rightarrow2#mu signal', 'l', 'hist')
    pD = Plotter.Plot(DATAHISTS[hkey]['data'], *DataPConfig[hkey]['data'])

    canvas = Plotter.Canvas(lumi='2#mu signal + 10% of 2016 data', logy=True)

    canvas.addMainPlot(pS)
    canvas.addMainPlot(pD)

    pS.setColor(R.kBlue, which='L')

    canvas.makeLegend(lWidth=.25)
    canvas.legend.resizeHeight()
    canvas.legend.moveLegend(X=-.1)

    canvas.firstPlot.SetMinimum(0.5   )
    canvas.firstPlot.SetMaximum(50000.)
    canvas.firstPlot.setTitles(Y='Long-Lived Candidates')

    line = R.TLine(R.TMath.Pi()/2., 0.5, R.TMath.Pi()/2., 50000.)
    line.Draw()
    line.SetLineStyle(2)

    RT.addBinWidth(canvas.firstPlot)
    canvas.cleanup('deltaPhi.pdf')

makeTestPlot()
