import ROOT as R
import numpy as np
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
from DisplacedDimuons.Common.Constants import BGORDER as BGORDER_REAL
import DisplacedDimuons.Analysis.Plotter as Plotter
from DisplacedDimuons.Common.Utilities import SPStr, SPLumiStr 
import DisplacedDimuons.Analysis.HistogramGetter as HG
import DisplacedDimuons.Analysis.RootTools as RT
import DisplacedDimuons.Analysis.PlotterParser as PP

ARGS = PP.PARSER.parse_args()
CUTSTRING = ARGS.CUTSTRING

if CUTSTRING == '':
    CUTSTRING = 'NS_NH_FPTE_HLT_REP_PQ1_PT_PC_LXYE_MASS_CHI2'
    print 'Defaulting to', CUTSTRING

lumiExtra = {
    'NS_NH_FPTE_HLT_REP_PQ1_PT_PC_LXYE_MASS_CHI2' : '',
    'NS_NH_FPTE_HLT_REP_PQ1_PT_PC_LXYE_MASS_CHI2_DSAPROXMATCH' : ' + DSA Prox',
    'NS_NH_FPTE_HLT_REP_PQ1_PT_PC_LXYE_MASS_CHI2_DPT'          : ' + DSA Prox + Trk #DeltaR < 0.05',
}

DRAW = False
if DRAW:
    R.gROOT.SetBatch(False)

FILES = {
    '2Mu2J' : R.TFile.Open('roots/ZephyrPlots_Trig_Combined_{}_HTo2XTo2Mu2J.root'.format(CUTSTRING)),
    'MC'    : R.TFile.Open('roots/ZephyrPlots_Combined_{}_MC.root'               .format(CUTSTRING))
}

fs = '2Mu2J'

# Lxy resolution vs Lxy
def makeLxyResVSLxyPlot(recoType):
    key = recoType + '-LxyResVSGEN-Lxy'
    HISTS = HG.getAddedSignalHistograms(FILES[fs], fs, (key,))

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

    canvas = Plotter.Canvas(lumi=fs+lumiExtra.get(CUTSTRING)+' ({})'.format(recoType))
    canvas.addMainPlot(p)
    canvas.firstPlot.SetMinimum(0.)
    if recoType == 'PAT':
        canvas.firstPlot.SetMaximum(0.02)
    if recoType == 'HYB':
        canvas.firstPlot.SetMaximum(5.)
    if recoType == 'DSA':
        canvas.firstPlot.SetMaximum(10.)
    canvas.cleanup('pdfs/ZEP_ResVSLxy_{}_{}_{}.pdf'.format(recoType, CUTSTRING, fs))
makeLxyResVSLxyPlot('PAT')
makeLxyResVSLxyPlot('HYB')
makeLxyResVSLxyPlot('DSA')

# make the 1D PAT and DSA plots
def makeSinglePlots():
    quantities = {'DSA':[], 'PAT':[], 'HYB':[]}
    dimQuantities = ['Lxy', 'LxySig', 'LxyErr', 'vtxChi2', 'LxyRes', 'LxyPull', 'mind0Sig', 'mass', 'deltaPhi', 'deltaR', 'cosAlpha']
    for recoType in quantities: quantities[recoType].extend(dimQuantities)

    quantities['DSA'].extend(['pT', 'eta', 'phi', 'FPTE', 'd0Sig', 'trkChi2', 'nStations'])
    quantities['PAT'].extend(['pT', 'eta', 'phi', 'relTrkIso', 'd0Sig', 'trkChi2'])

    for recoType in ('DSA', 'PAT', 'HYB'):
        for quantity in quantities[recoType]:
            key = recoType + '-' + quantity
            HISTS = HG.getAddedSignalHistograms(FILES[fs], fs, (key,))

            p = Plotter.Plot(HISTS[key], key, 'l', 'hist')
            canvas = Plotter.Canvas(lumi=fs+lumiExtra.get(CUTSTRING)+' ({})'.format(recoType), logy=True if quantity in ('vtxChi2', 'relTrkIso', 'deltaPhi', 'trkChi2') else False)
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

            if not canvas.logy:
                canvas.firstPlot.SetMinimum(0.)

            if 'vtxChi2' in key:
                canvas.firstPlot.GetXaxis().SetRangeUser(0., 50.)
                canvas.firstPlot.SetMaximum(40000.)
                canvas.firstPlot.SetMinimum(1.)
            if 'mind0Sig' in key:
                canvas.firstPlot.SetMaximum(200. if recoType == 'PAT' else 900.)
            if 'LxySig' in key:
                canvas.firstPlot.SetMaximum(200. if recoType == 'PAT' else (1200. if recoType == 'DSA' else 2700.))
            if 'relTrkIso' in key:
                canvas.firstPlot.SetMaximum(2000.)

            RT.addBinWidth(canvas.firstPlot)
            canvas.cleanup('pdfs/ZEP_{}_{}_{}_{}.pdf'.format(quantity, recoType, CUTSTRING, fs))
makeSinglePlots()

#### MC PLOTS ####

# MC plots of LxySig
def makeMCPlots():
    quantities = {'DSA':[], 'PAT':[], 'HYB':[]}
    dimQuantities = ['Lxy', 'LxySig', 'LxyErr', 'vtxChi2', 'mind0Sig', 'mass', 'deltaPhi', 'deltaR', 'cosAlpha']
    for recoType in quantities: quantities[recoType].extend(dimQuantities)

    quantities['DSA'].extend(['pT', 'eta', 'phi', 'FPTE', 'd0Sig', 'trkChi2', 'nStations'])
    quantities['PAT'].extend(['pT', 'eta', 'phi', 'relTrkIso', 'd0Sig', 'trkChi2'])

    # for the massZoomed plots, add mass to rebinVeto and uncomment the axis range
    # consider making deltaPhi not log scale. If so, then uncomment the maximum commands at the bottom

    def rebinVeto(key):
        if 'Lxy' in key and 'Sig' not in key and 'Err' not in key and 'DSA' not in key: return True
        if 'deltaPhi' in key or 'phi' in key: return True
        #if 'mass' in key: return True
        if 'nStations' in key: return True
        if 'cosAlpha' in key: return True
        if 'LxySig' in key and 'DSA' in key: return True
        return False

    for recoType in ('DSA', 'PAT', 'HYB'):
        for quantity in quantities[recoType]:
            hkey = recoType + '-' + quantity
            HISTS, PConfig = HG.getBackgroundHistograms(FILES['MC'], hkey, addFlows=True, rebin=10, rebinVeto=rebinVeto)
            HISTS = HISTS[hkey]
            PConfig = PConfig[hkey]

            PLOTS = {}
            for key in HG.BGORDER + ('stack',):
                PLOTS[key] = Plotter.Plot(HISTS[key], *PConfig[key])

            canvas = Plotter.Canvas(lumi='MC'+lumiExtra.get(CUTSTRING)+' ({})'.format(recoType), logy=True)

            for key in HG.BGORDER:
                PLOTS[key].setColor(HG.PLOTCONFIG[key]['COLOR'], which='LF')

            canvas.addMainPlot(PLOTS['stack'])

            # this has to be here because it has to be drawn first
            if 'vtxChi2' in hkey:
                canvas.firstPlot.GetXaxis().SetRangeUser(0., 50.)

            if 'mass' in hkey:
                pass
                #canvas.firstPlot.GetXaxis().SetRangeUser(0., 100.)

            if 'mind0Sig' in hkey and 'DSA' in hkey:
                pass
                #canvas.firstPlot.GetXaxis().SetRangeUser(0., 5.)

            canvas.firstPlot.setTitles(X='', copy=PLOTS[HG.BGORDER[0]])
            canvas.firstPlot.setTitles(Y='Normalized Counts')
            canvas.makeLegend(lWidth=.27, pos='tr', autoOrder=False, fontscale=0.8)
            for ref in reversed(HG.BGORDER):
                canvas.addLegendEntry(PLOTS[ref])
            canvas.legend.resizeHeight()
            RT.addBinWidth(canvas.firstPlot)

            HISTS['sum'] = HISTS['stack'].GetStack().Last()
            nBins = HISTS['sum'].GetNbinsX()

            val = None
            if 'LxySig' in hkey:
                val = 100.
            if 'vtxChi2' in hkey:
                val = 50.
            if 'LxyErr' in hkey:
                val = 10.
            if 'mind0Sig' in hkey:
                val = 3.
            if 'Lxy' == quantity:
                val = 100.

            if val is not None:
                print '{} Mean         : {}'.format(hkey,      HISTS['sum'].GetMean())
                print '{} Overflow   % : {}'.format(hkey,      HISTS['sum'].GetBinContent(                           nBins)/HISTS['sum'].Integral(1, nBins)*100.)
                print '{} > {:<8.0f} % : {}'.format(hkey, val, HISTS['sum'].Integral     (HISTS['sum'].FindBin(val), nBins)/HISTS['sum'].Integral(1, nBins)*100.)

            if hkey == 'PAT-LxySig':
                h = HG.getHistogram(FILES['MC'], 'DY50toInf', hkey).Clone()
                print '{} DY50toInf    : {}'.format(hkey, h.Integral(h.FindBin(100.), h.GetNbinsX()))

            doNotMaximize = True
            canvas.firstPlot.SetMaximum({'DSA':1000., 'PAT':10.**7., 'HYB':2.*10.**5.}[recoType])

            if recoType == 'DSA' and quantity in ['pT', 'eta', 'phi', 'FPTE', 'd0Sig', 'trkChi2', 'nStations']:
                canvas.firstPlot.SetMaximum(10.**5.)

            #if recoType == 'PAT' and 'deltaPhi' in quantity:
            #    canvas.firstPlot.SetMaximum(11.**5.)

            if not doNotMaximize:
                canvas.firstPlot.SetMaximum(HISTS['sum'].GetMaximum()*1.05)
            canvas.firstPlot.SetMinimum(1.)
            canvas.cleanup('pdfs/ZEP_{}_{}_{}_MC.pdf'.format(quantity, recoType, CUTSTRING))
makeMCPlots()

def makeMC2DPlots(BGList=None, SUFFIX=None):
    if BGList is None:
        BGORDER = ('WJets', 'WW', 'WZ', 'ZZ', 'tW', 'tbarW', 'ttbar', 'QCD20toInf-ME', 'DY10to50', 'DY50toInf')
        SUFFIX = 'Full'
    else:
        BGORDER = BGList
        if SUFFIX is None:
            SUFFIX = BGList[0]
    for quantity in ('normChi2', 'nTrkLay', 'nPxlHit', 'highPurity', 'isGlobal', 'isMedium', 'hitsBeforeVtx', 'missingHitsAfterVtx'):
        if quantity == 'nTrkLay':
            R.gStyle.SetPaintTextFormat('.1f')
        else:
            R.gStyle.SetPaintTextFormat('g')

        hkey = 'PAT-12-'+quantity
        HG.BGORDER = BGORDER # don't do this, normally
        HISTS, PConfig = HG.getBackgroundHistograms(FILES['MC'], hkey, stack=False, addFlows=False)
        HG.BGORDER = BGORDER_REAL
        HISTS = HISTS[hkey]
        PConfig = PConfig[hkey]

        if quantity != 'normChi2':
            R.gStyle.SetPalette(55)
            PConfig['stack'] = ('', '', 'colz text')
        else:
            R.gStyle.SetPalette(56)
            PConfig['stack'] = ('', '', 'colz')

        PLOTS = {}
        for key in ('stack',):
            PLOTS[key] = Plotter.Plot(HISTS[key], *PConfig[key])
        canvas = Plotter.Canvas(lumi=SUFFIX+lumiExtra.get(CUTSTRING))
        canvas.addMainPlot(PLOTS['stack'])
        canvas.firstPlot.SetMarkerColor(R.kWhite)

        if quantity == 'normChi2':
            canvas.firstPlot.GetXaxis().SetRangeUser(0., 10.)
            canvas.firstPlot.GetYaxis().SetRangeUser(0., 10.)

        canvas.scaleMargins(1.75, edges='R')
        canvas.scaleMargins(0.8, edges='L')
        canvas.cleanup('pdfs/ZEP_2D_{}_{}_{}_MC.pdf'.format(quantity, SUFFIX, CUTSTRING))
makeMC2DPlots()
makeMC2DPlots(('ttbar', 'QCD20toInf-ME', 'DY50toInf', 'WJets'), 'Major')
makeMC2DPlots(('ttbar',))
makeMC2DPlots(('WJets',))
makeMC2DPlots(('DY50toInf',))
makeMC2DPlots(('QCD20toInf-ME',))

def makeSignal2DPlots():
    for quantity in ('normChi2', 'nTrkLay', 'nPxlHit', 'highPurity', 'isGlobal', 'isMedium', 'hitsBeforeVtx', 'missingHitsAfterVtx'):
        if quantity == 'nTrkLay':
            R.gStyle.SetPaintTextFormat('.1f')
        else:
            R.gStyle.SetPaintTextFormat('g')

        hkey = 'PAT-12-'+quantity
        HISTS = HG.getAddedSignalHistograms(FILES[fs], fs, (hkey,))
        for sp in SIGNALPOINTS:
            HISTS[sp] = HG.getHistogram(FILES[fs], (fs, sp), hkey).Clone()

        if quantity != 'normChi2':
            opt = 'colz text'
        else:
            opt = 'colz'
        PLOTS = {hkey:Plotter.Plot(HISTS[hkey], '', '', opt)}
        for sp in SIGNALPOINTS:
            PLOTS[sp] = Plotter.Plot(HISTS[sp], '', '', opt)

        for sp in [hkey,] + SIGNALPOINTS:
            canvas = Plotter.Canvas(lumi=fs+lumiExtra.get(CUTSTRING) if type(sp) != tuple else SPLumiStr(fs, *sp))
            canvas.addMainPlot(PLOTS[sp])
            canvas.firstPlot.SetMarkerColor(R.kWhite)

            if quantity == 'normChi2':
                canvas.firstPlot.GetXaxis().SetRangeUser(0., 10.)
                canvas.firstPlot.GetYaxis().SetRangeUser(0., 10.)

            canvas.scaleMargins(1.75, edges='R')
            canvas.scaleMargins(0.8, edges='L')
            canvas.cleanup('pdfs/ZEP_2D_{}_{}_{}_{}.pdf'.format(quantity, CUTSTRING, fs, 'Global' if type(sp) != tuple else SPStr(sp)))
makeSignal2DPlots()
