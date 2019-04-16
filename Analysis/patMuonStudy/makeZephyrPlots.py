import ROOT as R
import numpy as np
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
from DisplacedDimuons.Common.Constants import BGORDER as BGORDER_REAL
import DisplacedDimuons.Analysis.Plotter as Plotter
from DisplacedDimuons.Common.Utilities import SPStr, SPLumiStr 
import DisplacedDimuons.Analysis.HistogramGetter as HG
import DisplacedDimuons.Analysis.RootTools as RT
import DisplacedDimuons.Analysis.PlotterParser as PP

DATASCALE = 1433921./14334550.

PP.PARSER.add_argument('--zoomed', dest='ZOOMED', action='store_true')
ARGS = PP.PARSER.parse_args()
CUTSTRING = ARGS.CUTSTRING
LXYZOOMEDFULL = ARGS.ZOOMED
MASSZOOMED = ARGS.ZOOMED

if CUTSTRING == '':
    CUTSTRING = 'NS_NH_FPTE_HLT_REP_PT_PC_LXYE_MASS_CHI2'
    print 'Defaulting to', CUTSTRING

lumiExtra = {
    'NS_NH_FPTE_HLT_REP_PT_PC_LXYE_MASS_CHI2'                : '',
    'NS_NH_FPTE_HLT_REP_PT_PC_LXYE_MASS_CHI2_VTX'            : ' + P.V.',
    'NS_NH_FPTE_HLT_REP_PT_PC_LXYE_MASS_CHI2_VTX_COSA'       : ' + P.V. + cos(#alpha)',
    'NS_NH_FPTE_HLT_REP_PT_PC_LXYE_MASS_CHI2_VTX_COSA_SFPTE' : ' + P.V. + cos(#alpha) + ref. FPTE',
}

DRAW = False
if DRAW:
    R.gROOT.SetBatch(False)

FILES = {
    '2Mu2J' : R.TFile.Open('roots/ZephyrPlots_Trig_Combined_{}_HTo2XTo2Mu2J.root'.format(CUTSTRING)),
    'MC'    : R.TFile.Open('roots/ZephyrPlots_Combined_{}_MC.root'               .format(CUTSTRING)),
    'Data'  : R.TFile.Open('roots/ZephyrPlots_Combined_{}_DATA.root'             .format(CUTSTRING)),
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
    quantities = {'DSA':[], 'PAT':[], 'HYB':[], 'HYB-DSA':[], 'HYB-PAT':[]}
    dimQuantities = ['Lxy', 'LxySig', 'LxyErr', 'vtxChi2', 'LxyRes', 'LxyPull', 'mind0Sig', 'mass', 'deltaPhi', 'deltaR', 'cosAlpha']
    for recoType in quantities:
        if 'HYB-' in recoType: continue
        quantities[recoType].extend(dimQuantities)

    quantities['HYB-DSA'].extend(['pT', 'eta', 'phi', 'd0', 'FPTE', 'd0Sig', 'trkChi2', 'nStations'])
    quantities['HYB-PAT'].extend(['pT', 'eta', 'phi', 'd0', 'relTrkIso', 'd0Sig', 'trkChi2'])

    quantities['REF-DSA'] = ['FPTE']
    quantities[''] = ['nDimuon']

    for recoType in ('DSA', 'PAT'):
        quantities[recoType].extend(quantities['HYB-'+recoType])

    for recoType in quantities:
        for quantity in quantities[recoType]:
            key = recoType + '-' + quantity
            if key[0] == '-':
                key = quantity
                recoType = 'DSAPlus'
            HISTS = HG.getAddedSignalHistograms(FILES[fs], fs, (key,))

            LXYZOOMED = LXYZOOMEDFULL and recoType == 'DSA'

            p = Plotter.Plot(HISTS[key], key, 'l', 'hist')
            canvas = Plotter.Canvas(lumi=fs+lumiExtra.get(CUTSTRING)+' ({})'.format(recoType), logy=True if quantity in ('vtxChi2', 'relTrkIso', 'deltaPhi', 'trkChi2', 'nDimuon') else False)

            if key == 'REF-DSA-FPTE':
                canvas.mainPad.SetLogx()

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

            if 'Lxy' == quantity and LXYZOOMED:
                canvas.firstPlot.GetXaxis().SetRangeUser(0., 50.)

            RT.addBinWidth(canvas.firstPlot)
            canvas.cleanup('pdfs/ZEP_{}_{}_{}_{}.pdf'.format(quantity + ('Zoomed' if quantity == 'Lxy' and LXYZOOMED else ''), recoType, CUTSTRING, fs))
makeSinglePlots()

#### MC PLOTS ####

# MC plots of LxySig
def makeMCPlots():
    quantities = {'DSA':[], 'PAT':[], 'HYB':[], 'HYB-DSA':[], 'HYB-PAT':[]}
    dimQuantities = ['Lxy', 'LxySig', 'LxyErr', 'vtxChi2', 'mind0Sig', 'mass', 'deltaPhi', 'deltaR', 'cosAlpha']
    for recoType in quantities:
        if 'HYB-' in recoType: continue
        quantities[recoType].extend(dimQuantities)

    quantities['HYB-DSA'].extend(['pT', 'eta', 'phi', 'd0', 'FPTE', 'd0Sig', 'trkChi2', 'nStations'])
    quantities['HYB-PAT'].extend(['pT', 'eta', 'phi', 'd0', 'relTrkIso', 'd0Sig', 'trkChi2'])

    for recoType in ('DSA', 'PAT'):
        quantities[recoType].extend(quantities['HYB-'+recoType])

    quantities['REF-DSA'] = ['FPTE']
    quantities[''] = ['nDimuon']

    # consider making deltaPhi not log scale. If so, then uncomment the maximum commands at the bottom

    def rebinVeto(key):
        if 'Lxy' in key and 'Sig' not in key and 'Err' not in key and 'DSA' not in key: return True
        if 'deltaPhi' in key or 'phi' in key: return True
        if 'mass' in key and MASSZOOMED: return True
        if 'nStations' in key: return True
        if 'cosAlpha' in key: return True
        if 'LxySig' in key and 'DSA' in key: return True
        if 'mind0Sig' in key and 'DSA' in key: return True
        if 'd0' in key and 'Sig' not in key and 'DSA' in key: return True
        if 'trkChi2' in key: return True
        if 'nDimuon' in key: return True
        if 'REF-DSA-FPTE' in key: return True
        return False

    for recoType in quantities:
        for quantity in quantities[recoType]:
            hkey = recoType + '-' + quantity
            if hkey[0] == '-':
                hkey = quantity
                recoType = 'DSAPlus'

            DODATA = recoType == 'DSA' or recoType == 'REF-DSA'

            if DODATA:
                HISTS, PConfig = HG.getBackgroundHistograms(FILES['MC'], hkey, addFlows=True, rebin=10, rebinVeto=rebinVeto, extraScale=DATASCALE)
                DATAHISTS, DataPConfig = HG.getDataHistograms(FILES['Data'], hkey, addFlows=True, rebin=10, rebinVeto=rebinVeto)
            else:
                HISTS, PConfig = HG.getBackgroundHistograms(FILES['MC'], hkey, addFlows=True, rebin=10, rebinVeto=rebinVeto)

            HISTS = HISTS[hkey]
            PConfig = PConfig[hkey]

            if DODATA:
                DATAHISTS = DATAHISTS[hkey]
                PConfig['data'] = DataPConfig[hkey]['data']

            PLOTS = {}
            for key in HG.BGORDER + ('stack',):
                PLOTS[key] = Plotter.Plot(HISTS[key], *PConfig[key])

            if DODATA:
                PLOTS['data'] = Plotter.Plot(DATAHISTS['data'], *PConfig['data'])

            canvas = Plotter.Canvas(lumi=('MC' if not DODATA else 'MC + Data')+lumiExtra.get(CUTSTRING)+' ({})'.format(recoType), logy=True,
                    ratioFactor=0. if not DODATA else 1./3., fontscale=1. if not DODATA else 1.+1./3.)

            if hkey == 'REF-DSA-FPTE':
                canvas.mainPad.SetLogx()

            for key in HG.BGORDER:
                PLOTS[key].setColor(HG.PLOTCONFIG[key]['COLOR'], which='LF')

            canvas.addMainPlot(PLOTS['stack'])

            if DODATA:
                canvas.addMainPlot(PLOTS['data'])

            # this has to be here because it has to be drawn first
            if 'vtxChi2' in hkey:
                canvas.firstPlot.GetXaxis().SetRangeUser(0., 50.)

            if 'mass' in hkey:
                if MASSZOOMED:
                    canvas.firstPlot.GetXaxis().SetRangeUser(0., 100.)

            if 'mind0Sig' in hkey and 'DSA' in hkey:
                pass
                #canvas.firstPlot.GetXaxis().SetRangeUser(0., 5.)

            canvas.firstPlot.setTitles(X='', copy=PLOTS[HG.BGORDER[0]])
            canvas.firstPlot.setTitles(Y='Normalized Counts')
            canvas.makeLegend(lWidth=.27, pos='tr' if hkey != 'REF-DSA-FPTE' else 'tl', autoOrder=False, fontscale=0.8 if not DODATA else 1.)
            if DODATA:
                canvas.addLegendEntry(PLOTS['data'])
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

            if DODATA:
                canvas.makeRatioPlot(PLOTS['data'].plot, PLOTS['stack'].plot.GetStack().Last())
                canvas.firstPlot.scaleTitleOffsets(0.8, axes='Y')
                canvas.rat      .scaleTitleOffsets(0.8, axes='Y')

                if 'mass' in hkey:
                    if MASSZOOMED:
                        canvas.rat.GetXaxis().SetRangeUser(0., 100.)

                if 'REF-DSA-FPTE' in hkey:
                    canvas.ratPad.SetLogx()

            doNotMaximize = True
            canvas.firstPlot.SetMaximum({'DSA'    :1000.     ,
                                         'PAT'    :10.**7.   ,
                                         'HYB'    :2.*10.**5.,
                                         'HYB-DSA':2.*10.**5.,
                                         'HYB-PAT':2.*10.**5.,
                                         'REF-DSA':1000.     ,
                                         'DSAPlus':1000.      }[recoType])

            if recoType == 'DSA' and quantity in ['pT', 'eta', 'phi', 'FPTE', 'd0Sig', 'trkChi2', 'nStations']:
                canvas.firstPlot.SetMaximum(10.**5.)

            #if recoType == 'PAT' and 'deltaPhi' in quantity:
            #    canvas.firstPlot.SetMaximum(11.**5.)

            if not doNotMaximize:
                canvas.firstPlot.SetMaximum(HISTS['sum'].GetMaximum()*1.05)
            canvas.firstPlot.SetMinimum(1.)
            #canvas.cleanup('pdfs/ZEP_{}_{}_{}_MC.pdf'.format(quantity, recoType, CUTSTRING))
            canvas.finishCanvas(extrascale=1. if not DODATA else 1.+1./3.)
            canvas.save('pdfs/ZEP_{}_{}_{}_MC.pdf'.format(quantity + ('Zoomed' if 'mass' in quantity and MASSZOOMED else ''), recoType, CUTSTRING))
            canvas.deleteCanvas()
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

### temporary: new functions for the DSA 2D histograms
# easier than carefully adapting the above

def makeDSAMC2DPlots():
    for quantity in ('pT', 'eta', 'trkChi2'):

        hkey = 'DSA-12-'+quantity
        HISTS, PConfig = HG.getBackgroundHistograms(FILES['MC'], hkey, stack=False, addFlows=False, rebin=(10, 10), rebinVeto=lambda key: 'trkChi2' in key)
        HISTS = HISTS[hkey]
        PConfig = PConfig[hkey]

        R.gStyle.SetPalette(56)
        PConfig['stack'] = ('', '', 'colz')
        #PConfig['stack'] = ('', '', 'scat=0.2')

        PLOTS = {}
        for key in ('stack',):
            PLOTS[key] = Plotter.Plot(HISTS[key], *PConfig[key])
        canvas = Plotter.Canvas(lumi='MC'+lumiExtra.get(CUTSTRING))
        canvas.addMainPlot(PLOTS['stack'])
        canvas.mainPad.SetLogz()

        if quantity == 'trkChi2':
            canvas.firstPlot.GetXaxis().SetRangeUser(0., 10.)
            canvas.firstPlot.GetYaxis().SetRangeUser(0., 10.)

        canvas.scaleMargins(1.75, edges='R')
        canvas.scaleMargins(0.8, edges='L')
        canvas.cleanup('pdfs/ZEP_2D_{}_{}_MC.pdf'.format(quantity, CUTSTRING))
makeDSAMC2DPlots()

def makeDSASignal2DPlots():
    for quantity in ('pT', 'eta', 'trkChi2'):

        hkey = 'DSA-12-'+quantity
        HISTS = HG.getAddedSignalHistograms(FILES[fs], fs, (hkey,))
        if 'trkChi2' not in hkey: HISTS[hkey].Rebin2D(10, 10)
        for sp in SIGNALPOINTS:
            HISTS[sp] = HG.getHistogram(FILES[fs], (fs, sp), hkey).Clone()
            if 'trkChi2' not in hkey: HISTS[sp].Rebin2D(10, 10)

        opt = 'colz'
        #opt = 'scat=0.2'
        PLOTS = {hkey:Plotter.Plot(HISTS[hkey], '', '', opt)}
        for sp in SIGNALPOINTS:
            PLOTS[sp] = Plotter.Plot(HISTS[sp], '', '', opt)

        for sp in [hkey,] + SIGNALPOINTS:
            canvas = Plotter.Canvas(lumi=fs+lumiExtra.get(CUTSTRING) if type(sp) != tuple else SPLumiStr(fs, *sp))
            canvas.addMainPlot(PLOTS[sp])
            canvas.mainPad.SetLogz()

            if quantity == 'trkChi2':
                canvas.firstPlot.GetXaxis().SetRangeUser(0., 10.)
                canvas.firstPlot.GetYaxis().SetRangeUser(0., 10.)

            canvas.scaleMargins(1.75, edges='R')
            canvas.scaleMargins(0.8, edges='L')
            canvas.cleanup('pdfs/ZEP_2D_{}_{}_{}_{}.pdf'.format(quantity, CUTSTRING, fs, 'Global' if type(sp) != tuple else SPStr(sp)))
makeDSASignal2DPlots()
