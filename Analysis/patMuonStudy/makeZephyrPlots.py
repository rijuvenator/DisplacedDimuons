import ROOT as R
import numpy as np
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
import DisplacedDimuons.Analysis.Plotter as Plotter
from DisplacedDimuons.Common.Utilities import SPStr, SPLumiStr 
import DisplacedDimuons.Analysis.HistogramGetter as HG
import DisplacedDimuons.Analysis.RootTools as RT

DRAW = False
if DRAW:
    R.gROOT.SetBatch(False)

FILE = R.TFile.Open('roots/ZephyrPlots_Trig_Combined_BS9_Hybrids_2Mu2J.root')

fs = '2Mu2J'

# Lxy resolution vs Lxy
def makeLxyResVSLxyPlot(recoType):
    key = recoType + '-LxyResVSGEN-Lxy'
    HISTS = HG.getAddedSignalHistograms(FILE, fs, (key,))

    config = {
        'PAT' : (35 ,  1),
        'HYB' : (70 ,  2),
        'DSA' : (350, 10),
    }

    upperEdge = config[recoType][0]
    step      = config[recoType][1]
    xPoints   = map(lambda z: float(z)+float(step)/2., range(0, upperEdge, step))
    xError    = [float(step)/2.] * len(xPoints)

    yPoints = []
    yError = []
    for ibin in xrange(1,upperEdge+1):
        if (ibin+step/2)%step != 0: continue
        binRange = (ibin-int(step/2.-1), ibin+int(step/2.))
        h = HISTS[key].ProjectionY('h'+str(ibin), *binRange)
        #lims = .01
        #lims = 5. if recoType == 'DSA' else .05
        lims = {'DSA':15., 'PAT':.05, 'HYB':5.}
        lims = lims[recoType]
        if recoType == 'PAT' and ibin > 10:
            lims = lims/5.
        func = R.TF1('f', 'gaus', -lims, lims)
        h.Fit('f', 'Rq')
        yPoints.append(func.GetParameter(2))
        yError.append(func.GetParError(2))

    g = R.TGraphErrors(len(xPoints), np.array(xPoints), np.array(yPoints), np.array(xError), np.array(yError))
    p = Plotter.Plot(g, '', '', 'pe')
    p.setTitles(X='gen L_{xy} [cm]', Y='Fitted #sigma L_{xy} Res. [cm]')

    canvas = Plotter.Canvas(lumi=fs)
    canvas.addMainPlot(p)
    canvas.firstPlot.SetMinimum(0.)
    if recoType == 'PAT':
        canvas.firstPlot.SetMaximum(0.02)
    if recoType == 'HYB':
        canvas.firstPlot.SetMaximum(5.)
    if recoType == 'DSA':
        canvas.firstPlot.SetMaximum(10.)
    canvas.cleanup('pdfs/ZEP_ResVSLxy_BS9_{}.pdf'.format(recoType))
makeLxyResVSLxyPlot('PAT')
makeLxyResVSLxyPlot('HYB')
makeLxyResVSLxyPlot('DSA')

# make the 1D PAT and DSA plots
def makeSinglePlots():
    for recoType in ('DSA', 'PAT', 'HYB'):
        for quantity in ('LxySig', 'LxyErr', 'vtxChi2', 'LxyRes', 'LxyPull'):
            key = recoType + '-' + quantity
            HISTS = HG.getAddedSignalHistograms(FILE, fs, (key,))

            p = Plotter.Plot(HISTS[key], key, 'l', 'hist')
            canvas = Plotter.Canvas(lumi=fs)
            canvas.addMainPlot(p, addS=True)
            p.setColor(R.kBlue, which='L')
            nbox = canvas.makeStatsBox(p.plot, color=R.kBlue)
            if quantity == 'LxyPull':
                func = R.TF1('f', 'gaus', -4., 4.)
                HISTS[key].Fit('f', 'R')
                fplot = Plotter.Plot(func, 'Fit', 'l', '')
                fplot.SetLineColor(R.kRed)
                canvas.addMainPlot(fplot)
                canvas.setFitBoxStyle(p.plot, lWidth=0.275, pos='tl')
                sbox = p.plot.FindObject('stats')
                sbox.SetTextColor(R.kRed)
            canvas.cleanup('pdfs/ZEP_{}.pdf'.format(key))
makeSinglePlots()

#### MC PLOTS ####

FILE = R.TFile.Open('roots/ZephyrPlots_Combined_BS9_Hybrids_MC.root')
# MC plots of LxySig
def makeMCPlots():
    BGORDER = ('WJets', 'WW', 'WZ', 'ZZ', 'tW', 'tbarW', 'ttbar', 'QCD20toInf-ME', 'DY10to50', 'DY50toInf')
    PC = HG.PLOTCONFIG
    for recoType in ('PAT', 'DSA', 'HYB'):
        for quantity in ('LxySig', 'LxyErr', 'vtxChi2'):
            hkey = recoType + '-' + quantity
            HISTS = {}
            HISTS['stack'] = R.THStack('hStack', '')
            PConfig = {'stack':('', '', 'hist')}
            for ref in BGORDER:
               HISTS[ref] = HG.getHistogram(FILE, ref, hkey).Clone()
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
            canvas.firstPlot.setTitles(X='', copy=PLOTS[BGORDER[0]])
            canvas.firstPlot.setTitles(Y='Normalized Counts')
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
                h = HG.getHistogram(FILE, 'DY50toInf', hkey).Clone()
                print '{} DY50toInf    : {}'.format(hkey, h.Integral(h.FindBin(100.), h.GetNbinsX()+1))

            canvas.firstPlot.SetMaximum(HISTS['sum'].GetMaximum()*1.05)
            canvas.firstPlot.SetMinimum(1.)
            canvas.cleanup('pdfs/ZEP_MC_'+hkey+'.pdf')
makeMCPlots()

R.gStyle.SetPalette(55)
def makeMC2DPlots(BGList=None, SUFFIX=None):
    if BGList is None:
        BGORDER = ('WJets', 'WW', 'WZ', 'ZZ', 'tW', 'tbarW', 'ttbar', 'QCD20toInf-ME', 'DY10to50', 'DY50toInf')
        SUFFIX = 'Full'
    else:
        BGORDER = BGList
        if SUFFIX is None:
            SUFFIX = BGList[0]
    PC = HG.PLOTCONFIG
    for quantity in ('chi2', 'nTrkLay', 'nPxlHit', 'highPurity', 'isGlobal'):
        if quantity == 'nTrkLay':
            R.gStyle.SetPaintTextFormat('.1f')
        else:
            R.gStyle.SetPaintTextFormat('g')
        hkey = 'PAT-12-LxySig100-'+quantity
        HISTS = {}
        HISTS['stack'] = HG.getHistogram(FILE, BGORDER[0], hkey).Clone()
        HISTS['stack'].Scale(PC[BGORDER[0]]['WEIGHT'])
        if quantity != 'chi2':
            PConfig = {'stack':('', '', 'colz text')}
        else:
            PConfig = {'stack':('', '', 'colz')}
        for ref in BGORDER:
           HISTS[ref] = HG.getHistogram(FILE, ref, hkey).Clone()
           #RT.addFlows(HISTS[ref])
           HISTS[ref].Scale(PC[ref]['WEIGHT'])
           #HISTS[ref].Rebin(10)
           if ref != BGORDER[0]:
               HISTS['stack'].Add(HISTS[ref])
           PConfig[ref] = (PC[ref]['LATEX'], 'f', 'hist')

        PLOTS = {}
        for key in ('stack',):
            PLOTS[key] = Plotter.Plot(HISTS[key], *PConfig[key])
        canvas = Plotter.Canvas(lumi=SUFFIX)
        canvas.addMainPlot(PLOTS['stack'])
        canvas.firstPlot.SetMarkerColor(R.kWhite)

        if quantity == 'chi2':
            canvas.firstPlot.GetXaxis().SetRangeUser(0., 100.)
            canvas.firstPlot.GetYaxis().SetRangeUser(0., 100.)

        canvas.scaleMargins(1.75, edges='R')
        canvas.scaleMargins(0.8, edges='L')
        canvas.cleanup('pdfs/ZEP_MC2D_'+quantity+'_'+SUFFIX+'.pdf')
makeMC2DPlots()
makeMC2DPlots(('ttbar', 'QCD20toInf-ME', 'DY50toInf', 'WJets'), 'Major')
makeMC2DPlots(('ttbar',))
makeMC2DPlots(('WJets',))
makeMC2DPlots(('DY50toInf',))
makeMC2DPlots(('QCD20toInf-ME',))

FILE = R.TFile.Open('roots/ZephyrPlots_Trig_Combined_BS9_Hybrids_2Mu2J.root')
def makeSignal2DPlots():
    for quantity in ('chi2', 'nTrkLay', 'nPxlHit', 'highPurity', 'isGlobal'):
        if quantity == 'nTrkLay':
            R.gStyle.SetPaintTextFormat('.1f')
        else:
            R.gStyle.SetPaintTextFormat('g')
        hkey = 'PAT-12-'+quantity
        HISTS = HG.getAddedSignalHistograms(FILE, fs, (hkey,))
        for sp in SIGNALPOINTS:
            HISTS[sp] = HG.getHistogram(FILE, (fs, sp), hkey).Clone()

        if quantity != 'chi2':
            opt = 'colz text'
        else:
            opt = 'colz'
        PLOTS = {hkey:Plotter.Plot(HISTS[hkey], '', '', opt)}
        for sp in SIGNALPOINTS:
            PLOTS[sp] = Plotter.Plot(HISTS[sp], '', '', opt)

        for sp in [hkey,] + SIGNALPOINTS:
            canvas = Plotter.Canvas(lumi=fs if type(sp) != tuple else SPLumiStr(fs, *sp))
            canvas.addMainPlot(PLOTS[sp])
            canvas.firstPlot.SetMarkerColor(R.kWhite)

            if quantity == 'chi2':
                canvas.firstPlot.GetXaxis().SetRangeUser(0., 100.)
                canvas.firstPlot.GetYaxis().SetRangeUser(0., 100.)

            canvas.scaleMargins(1.75, edges='R')
            canvas.scaleMargins(0.8, edges='L')
            canvas.cleanup('pdfs/ZEP_2D_{}_{}_{}.pdf'.format(quantity, fs, 'Global' if type(sp) != tuple else SPStr(sp)))
makeSignal2DPlots()
