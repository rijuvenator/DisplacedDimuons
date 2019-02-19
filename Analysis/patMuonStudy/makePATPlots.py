import ROOT as R
import numpy as np
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
import DisplacedDimuons.Analysis.Plotter as Plotter
from DisplacedDimuons.Common.Utilities import SPStr, SPLumiStr 
import DisplacedDimuons.Analysis.HistogramGetter as HG
import DisplacedDimuons.Analysis.RootTools as RT

FILE = R.TFile.Open('roots/PATMuonStudyPlots_Trig_Combined_BS8_2Mu2J.root')

fs = '2Mu2J'

# plot of fraction of DSA dimuons that can be replaced
def makePercentReplacedPlot(gen=False):
    keylist = ['PAT-Lxy', 'DSA-Lxy']
    if gen:
        keylist = [i.replace('Lxy', 'genLxy') for i in keylist]
    HISTS = HG.getAddedSignalHistograms(FILE, fs, keylist)
    for key, h in HISTS.iteritems():
        pass
        #h.Rebin(5)
    g = R.TGraphAsymmErrors(HISTS[keylist[0]], HISTS[keylist[1]], 'cp')
    p = Plotter.Plot(g, '', '', 'p')

    p.setTitles(Y='% replaced selected DSA dimuons', X=('gen ' if gen else '')+'L_{xy} [cm]')
    #RT.addBinWidth(p)

    canvas = Plotter.Canvas(lumi=fs)
    #canvas = Plotter.Canvas(lumi=fs, logy=True)
    canvas.addMainPlot(p)
    canvas.firstPlot.SetMinimum(0.)
    #canvas.firstPlot.SetMinimum(0.0001)
    canvas.firstPlot.SetMaximum(1.)
    canvas.cleanup('pdfs/percentReplacedVS{}Lxy_{}.pdf'.format('gen' if gen else '', fs))
makePercentReplacedPlot()
makePercentReplacedPlot(True)

# Lxy resolution vs Lxy
def makeLxyResVSLxyPlot(recoType):
    key = recoType + '-LxyResVSgenLxy'
    HISTS = HG.getAddedSignalHistograms(FILE, fs, (key,))

    upperEdge = 35
    xPoints = map(lambda z: float(z)+0.5, range(upperEdge))

    yPoints = []
    for ibin in xrange(1,upperEdge+1):
        h = HISTS[key].ProjectionY('h'+str(ibin), ibin, ibin)
        #lims = .01
        lims = 5. if recoType == 'DSA' else .05
        if recoType == 'PAT' and ibin > 10:
            lims = lims/5.
        func = R.TF1('f', 'gaus', -lims, lims)
        h.Fit('f', 'R')
        yPoints.append(func.GetParameter(2))

    g = R.TGraph(len(xPoints), np.array(xPoints), np.array(yPoints))
    p = Plotter.Plot(g, '', '', 'pe')
    p.setTitles(X='gen L_{xy} [cm]', Y='Fitted #sigma L_{xy} Res.')

    canvas = Plotter.Canvas(lumi=fs)
    canvas.addMainPlot(p)
    canvas.cleanup('pdfs/ResVSLxy.pdf')
makeLxyResVSLxyPlot('PAT')
