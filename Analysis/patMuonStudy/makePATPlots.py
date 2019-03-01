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
def makePercentReplacedPlot():
    keylist = ['PAT-genLxy', 'DSA-genLxy']
    HISTS = HG.getAddedSignalHistograms(FILE, fs, keylist)
    for key, h in HISTS.iteritems():
        pass
        #h.Rebin(5)
    g = R.TGraphAsymmErrors(HISTS[keylist[0]], HISTS[keylist[1]], 'cp')
    p = Plotter.Plot(g, '', '', 'p')

    p.setTitles(Y='% replaced selected DSA dimuons', X='gen L_{xy} [cm]')
    #RT.addBinWidth(p)

    canvas = Plotter.Canvas(lumi=fs)
    #canvas = Plotter.Canvas(lumi=fs, logy=True)
    canvas.addMainPlot(p)
    canvas.firstPlot.SetMinimum(0.)
    #canvas.firstPlot.SetMinimum(0.0001)
    canvas.firstPlot.SetMaximum(1.)
    canvas.cleanup('pdfs/percentReplacedVSgenLxy_{}.pdf'.format(fs))
makePercentReplacedPlot()

# Lxy resolution vs Lxy
def makeLxyResVSLxyPlot(recoType):
    key = recoType + '-LxyResVSgenLxy'
    HISTS = HG.getAddedSignalHistograms(FILE, fs, (key,))

    upperEdge = 35
    xPoints = map(lambda z: float(z)+0.5, range(upperEdge))
    xError = [0.5] * len(xPoints)

    yPoints = []
    yError = []
    for ibin in xrange(1,upperEdge+1):
        h = HISTS[key].ProjectionY('h'+str(ibin), ibin, ibin)
        #lims = .01
        lims = 5. if recoType == 'DSA' else .05
        if recoType == 'PAT' and ibin > 10:
            lims = lims/5.
        func = R.TF1('f', 'gaus', -lims, lims)
        h.Fit('f', 'R')
        yPoints.append(func.GetParameter(2))
        yError.append(func.GetParError(2))

    g = R.TGraphErrors(len(xPoints), np.array(xPoints), np.array(yPoints), np.array(xError), np.array(yError))
    p = Plotter.Plot(g, '', '', 'pe')
    p.setTitles(X='gen L_{xy} [cm]', Y='Fitted #sigma L_{xy} Res. [cm]')

    canvas = Plotter.Canvas(lumi=fs)
    canvas.addMainPlot(p)
    if recoType == 'PAT':
        canvas.firstPlot.SetMaximum(0.020)
        canvas.firstPlot.SetMinimum(0.000)
    canvas.cleanup('pdfs/ResVSLxy_{}.pdf'.format(recoType))
makeLxyResVSLxyPlot('PAT')

# MC plots of LxySig
def makeMCPlots():
    f = R.TFile.Open('roots/PATMuonStudyPlots_Combined_BS8_MC.root')
    #f = R.TFile.Open('roots/PATMuonStudyPlots_Combined_BS8_MC_OldPATMatch.root')
    BGORDER = ('WJets', 'WW', 'WZ', 'ZZ', 'tW', 'tbarW', 'ttbar', 'QCD20toInf-ME', 'DY10to50', 'DY50toInf')
    PC = HG.PLOTCONFIG
    for hkey in ('PAT-LxySig', 'DSA-LxySig', 'PAT-vtxChi2', 'DSA-vtxChi2'):
        HISTS = {}
        HISTS['stack'] = R.THStack('hStack', '')
        PConfig = {'stack':('', '', 'hist')}
        for ref in BGORDER:
           HISTS[ref] = HG.getHistogram(f, ref, hkey).Clone()
           #RT.addFlows(HISTS[ref])
           HISTS[ref].Scale(PC[ref]['WEIGHT'])
           HISTS[ref].Rebin(10)
           HISTS['stack'].Add(HISTS[ref])
           PConfig[ref] = (PC[ref]['LATEX'], 'f', 'hist')

        PLOTS = {}
        for key in BGORDER + ('stack',):
            PLOTS[key] = Plotter.Plot(HISTS[key], *PConfig[key])
        canvas = Plotter.Canvas(logy=True)
        for key in BGORDER:
            PLOTS[key].setColor(PC[key]['COLOR'], which='LF')
        canvas.addMainPlot(PLOTS['stack'])
        # this has to be here because it has to be drawn first
        if 'LxySig' in hkey:
            canvas.firstPlot.GetXaxis().SetRangeUser(0., 1000.)
            pass
        if 'vtxChi2' in hkey:
            #canvas.firstPlot.GetXaxis().SetRangeUser(0., 200.)
            pass
        canvas.firstPlot.setTitles(X=PLOTS[BGORDER[0]].GetXaxis().GetTitle(), Y='Normalized Counts')
        canvas.makeLegend(lWidth=.27, pos='tr', autoOrder=False, fontscale=0.8)
        for ref in reversed(BGORDER):
            canvas.addLegendEntry(PLOTS[ref])
        canvas.legend.resizeHeight()
        RT.addBinWidth(canvas.firstPlot)

        HISTS['sum'] = HISTS['stack'].GetStack().Last()
        nBins = HISTS['sum'].GetNbinsX()

        if 'LxySig' in hkey:
            val = 100.
        if 'vtxChi2' in hkey:
            val = 50.
        print '{} Mean         : {}'.format(hkey,      HISTS['sum'].GetMean())
        print '{} Overflow   % : {}'.format(hkey,      HISTS['sum'].GetBinContent(                           nBins+1)/HISTS['sum'].Integral(0, nBins+1)*100.)
        print '{} > {:<8.0f} % : {}'.format(hkey, val, HISTS['sum'].Integral     (HISTS['sum'].FindBin(val), nBins+1)/HISTS['sum'].Integral(0, nBins+1)*100.)

        if hkey == 'PAT-LxySig':
            h = HG.getHistogram(f, 'DY50toInf', hkey).Clone()
            print '{} DY50toInf    : {}'.format(hkey, h.Integral(h.FindBin(100.), h.GetNbinsX()+1))

        canvas.firstPlot.SetMaximum(HISTS['sum'].GetMaximum()*1.05)
        canvas.firstPlot.SetMinimum(1.)
        canvas.cleanup('pdfs/MC_'+hkey+'.pdf')
makeMCPlots()
