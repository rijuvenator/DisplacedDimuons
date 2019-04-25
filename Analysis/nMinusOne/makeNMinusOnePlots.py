import ROOT as R
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
import DisplacedDimuons.Analysis.Plotter as Plotter
from DisplacedDimuons.Common.Utilities import SPStr, SPLumiStr 
import DisplacedDimuons.Analysis.HistogramGetter as HG
import DisplacedDimuons.Analysis.RootTools as RT
import DisplacedDimuons.Analysis.PlotterParser as PP

PP.PARSER.add_argument('--bump', dest='BUMP', action='store_true')
ARGS = PP.PARSER.parse_args()
BUMPSTRING = ''
if ARGS.BUMP:
    BUMPSTRING = '_Bump'

DODATA = True
DATASCALE = 1433921./14334550.

FILES = {
    '2Mu2J' : R.TFile.Open('roots/NM1Plots_Trig{}_HTo2XTo2Mu2J.root'.format(BUMPSTRING)),
    'MC'    : R.TFile.Open('roots/NM1Plots{}_MC.root'               .format(BUMPSTRING)),
    'Data'  : R.TFile.Open('roots/NM1Plots{}_DATA.root'             .format(BUMPSTRING)),
}

CUTS = ('NS_NH', 'FPTE', 'HLT', 'PT', 'LXYE', 'MASS', 'CHI2', 'VTX', 'COSA', 'SFPTE')
PRETTY = ('n_{st/hits}', '#sigma_{p_{T}}/p_{T}', 'HLT-m', 'p_{T}', '#sigma_{L_{xy}}', 'M(#mu#mu)', 'vtx #chi^{2}', 'pv', 'cos(#alpha)', 'sFPTE')
#PRETTY = CUTS[:]
PRETTY = dict(zip(CUTS, PRETTY))

def setBinLabels(canvas, plot=None):
    if plot is None:
        plot = canvas.firstPlot
    else:
        plot = canvas.rat

    xaxis = plot.GetXaxis()
    xaxis.SetBinLabel(1, 'none')
    for ibin, cut in enumerate(CUTS):
        xaxis.SetBinLabel(ibin+2, PRETTY[cut])

    Plotter.Plot.scaleLabels(plot, 1.4, axes='X')

def makeIntegratedSEQMC(hkey='SEQ'):
    if DODATA:
        HISTS, PConfig = HG.getBackgroundHistograms(FILES['MC'], hkey, extraScale=DATASCALE)
        DATAHISTS, DataPConfig = HG.getDataHistograms(FILES['Data'], hkey)
    else:
        HISTS, PConfig = HG.getBackgroundHistograms(FILES['MC'], hkey)

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

    canvas = Plotter.Canvas(lumi='MC' if not DODATA else 'MC + Data', logy=True, cWidth=1000,
        ratioFactor=0. if not DODATA else 1./3., fontscale=1. if not DODATA else 1.+1./3.)

    for key in HG.BGORDER:
        PLOTS[key].setColor(HG.PLOTCONFIG[key]['COLOR'], which='LF')

    canvas.addMainPlot(PLOTS['stack'])

    if DODATA:
        canvas.addMainPlot(PLOTS['data'])

    setBinLabels(canvas)

    canvas.makeLegend(lWidth=.27, pos='tr', autoOrder=False, fontscale=0.8 if not DODATA else 1.)
    if DODATA:
        canvas.addLegendEntry(PLOTS['data'])
    for ref in reversed(HG.BGORDER):
        canvas.addLegendEntry(PLOTS[ref])
    canvas.legend.resizeHeight()

    canvas.firstPlot.setTitles(X='Cut', Y='Normalized Counts')
    canvas.firstPlot.SetMaximum(2.e7)
    canvas.firstPlot.SetMinimum(1.e4 if 'DSA' not in hkey else 1.e-1)

    if DODATA:
        canvas.makeRatioPlot(PLOTS['data'].plot, PLOTS['stack'].plot.GetStack().Last())
        canvas.firstPlot.scaleTitleOffsets(0.8, axes='Y')
        canvas.rat      .scaleTitleOffsets(0.8, axes='Y')
        canvas.rat.setTitles(X='', copy=canvas.firstPlot.plot)
        setBinLabels(canvas, '')

    #canvas.cleanup('pdfs/NM1_{}_MC.pdf'.format(hkey))
    canvas.finishCanvas(extrascale=1. if not DODATA else 1.+1./3.)
    canvas.save('pdfs/NM1_{}{}_MC.pdf'.format(hkey, BUMPSTRING))
    canvas.deleteCanvas()
makeIntegratedSEQMC()
makeIntegratedSEQMC(hkey='DSA-SEQ')

def makeIntegratedSEQSignal(hkey='SEQ'):
    HISTS = HG.getAddedSignalHistograms(FILES['2Mu2J'], '2Mu2J', hkey)

    h = HISTS[hkey]
    p = Plotter.Plot(h, '', '', 'hist')

    canvas = Plotter.Canvas(lumi='2Mu2J', cWidth=1000)
    canvas.addMainPlot(p)

    p.SetLineColor(R.kBlue)

    setBinLabels(canvas)

    canvas.firstPlot.setTitles(X='Cut', Y='Normalized Counts')
    canvas.firstPlot.SetMaximum(3.e5 if 'DSA' not in hkey else 1.e5)
    canvas.firstPlot.SetMinimum(0.)

    canvas.cleanup('pdfs/NM1_{}{}_2Mu2J.pdf'.format(hkey, BUMPSTRING))
makeIntegratedSEQSignal()
makeIntegratedSEQSignal(hkey='DSA-SEQ')

def makeIntegratedNM1MC(hkey='NM1'):

    ### modified version of getBackgroundHistograms

    FILE = FILES['MC']
    keylist = [hkey]
    stack = True
    addFlows=False
    rebin=None
    rebinVeto=None

    HISTS = {}
    PConfig = {}
    for key in keylist:
        HISTS[key] = {}
        PConfig[key] = {'stack':('', '', 'hist')}

        if stack:
            HISTS[key]['stack'] = R.THStack('hStack', '')

        for ref in HG.BGORDER:
            HISTS[key][ref] = HG.getHistogram(FILE, ref, key).Clone()

            #if addFlows:
            #    RT.addFlows(HISTS[key][ref])

            HISTS[key][ref].Scale(HG.PLOTCONFIG[ref]['WEIGHT'])
            if DODATA:
                HISTS[key][ref].Scale(DATASCALE)

            #if rebin is not None and (rebinVeto is None or (rebinVeto is not None and not rebinVeto(key))):
            #    is2D = 'TH2' in str(HISTS[key][ref].__class__)
            #    if is2D:
            #        if not hasattr(rebin, '__iter__'):
            #            print '[HISTOGRAMGETTER ERROR]: For 2D plots, "rebin" must be a list of 2 rebin values'
            #            exit()
            #        HISTS[key][ref].Rebin2D(*rebin)
            #    else:
            #        HISTS[key][ref].Rebin(rebin)

            PConfig[key][ref] = (HG.PLOTCONFIG[ref]['LATEX'], 'f', 'hist')

            #if not stack and ref == BGORDER[0]:
            #    HISTS[key]['stack'] = HISTS[key][ref].Clone()
            #    continue

        ### modification

        totalBin1 = sum([HISTS[key][ref].GetBinContent(1) for ref in HG.BGORDER])
        for ibin in range(1, len(CUTS)+2):
            totalBin = sum([HISTS[key][ref].GetBinContent(ibin) for ref in HG.BGORDER])
            scaleFactor = totalBin1/totalBin
            for ref in HG.BGORDER:
                HISTS[key][ref].SetBinContent(ibin, HISTS[key][ref].GetBinContent(ibin)/totalBin*scaleFactor)

        ### end modification

        # NOW add to the stack
        for ref in HG.BGORDER:
            HISTS[key]['stack'].Add(HISTS[key][ref])

    ### end modified version of getBackgroundHistograms

    HISTS = HISTS[hkey]
    PConfig = PConfig[hkey]

    if DODATA:
        DATAHISTS, DataPConfig = HG.getDataHistograms(FILES['Data'], hkey)
        DATAHISTS = DATAHISTS[hkey]
        PConfig['data'] = DataPConfig[hkey]['data']
        #PConfig['data'] = ('DoubleMuon2016', 'pe', 'pe')

        totalBin1 = DATAHISTS['data'].GetBinContent(1)
        for ibin in range(1, len(CUTS)+2):
            totalBin = DATAHISTS['data'].GetBinContent(ibin)
            scaleFactor = totalBin1/totalBin
            DATAHISTS['data'].SetBinContent(ibin, DATAHISTS['data'].GetBinContent(ibin)/totalBin*scaleFactor)

        for ibin in range(1, len(CUTS)+2):
            DATAHISTS['data'].SetBinError(ibin, 1.e-7)

    PLOTS = {}
    for key in HG.BGORDER + ('stack',):
        PLOTS[key] = Plotter.Plot(HISTS[key], *PConfig[key])

    if DODATA:
        PLOTS['data'] = Plotter.Plot(DATAHISTS['data'], *PConfig['data'])

    canvas = Plotter.Canvas(lumi='MC' if not DODATA else 'MC + Data', logy=True, cWidth=1000,
        ratioFactor=0. if not DODATA else 1./3., fontscale=1. if not DODATA else 1.+1./3.)

    for key in HG.BGORDER:
        PLOTS[key].setColor(HG.PLOTCONFIG[key]['COLOR'], which='LF')

    canvas.addMainPlot(PLOTS['stack'])

    if DODATA:
        canvas.addMainPlot(PLOTS['data'])

    setBinLabels(canvas)

    canvas.makeLegend(lWidth=.27, pos='bl', autoOrder=False, fontscale=0.8 if not DODATA else 1.)
    if DODATA:
        canvas.addLegendEntry(PLOTS['data'])
    for ref in reversed(HG.BGORDER):
        canvas.addLegendEntry(PLOTS[ref])
    canvas.legend.resizeHeight()

    canvas.firstPlot.setTitles(X='Cut', Y='n#minus1 Eff.')
    canvas.firstPlot.SetMaximum(1.e0)
    canvas.firstPlot.SetMinimum(1.e-3 if 'DSA' not in hkey else 1.e-6)

    if DODATA:
        canvas.makeRatioPlot(PLOTS['data'].plot, PLOTS['stack'].plot.GetStack().Last())
        canvas.firstPlot.scaleTitleOffsets(0.8, axes='Y')
        canvas.rat      .scaleTitleOffsets(0.8, axes='Y')
        canvas.rat.setTitles(X='', copy=canvas.firstPlot.plot)
        setBinLabels(canvas, '')
        for ibin in range(1, len(CUTS)+2):
            canvas.rat.SetBinError(ibin, 1.e-7)

    #canvas.cleanup('pdfs/NM1_{}_MC.pdf'.format(hkey))
    canvas.finishCanvas(extrascale=1. if not DODATA else 1.+1./3.)
    canvas.save('pdfs/NM1_{}{}_MC.pdf'.format(hkey, BUMPSTRING))
    canvas.deleteCanvas()
makeIntegratedNM1MC()
makeIntegratedNM1MC(hkey='DSA-NM1')

def makeIntegratedNM1Signal(hkey='NM1'):

    #HISTS, INDIV = HG.getAddedSignalHistograms(FILES['2Mu2J'], '2Mu2J', 'NM1', getIndividuals=True)

    #totalBin1 = sum([INDIV['NM1'][ref].GetBinContent(1) for ref in SIGNALPOINTS])
    #for ibin in range(1, len(CUTS)+2):
    #    totalBin = sum([INDIV['NM1'][ref].GetBinContent(ibin) for ref in SIGNALPOINTS])
    #    scaleFactor = totalBin1/totalBin
    #    for ref in SIGNALPOINTS:
    #        INDIV['NM1'][ref].SetBinContent(ibin, INDIV['NM1'][ref].GetBinContent(ibin)/totalBin*scaleFactor)

    HISTS = HG.getAddedSignalHistograms(FILES['2Mu2J'], '2Mu2J', hkey)
    totalBin1 = HISTS[hkey].GetBinContent(1)
    for ibin in range(1, len(CUTS)+2):
        totalBin = HISTS[hkey].GetBinContent(ibin)
        scaleFactor = totalBin1/totalBin
        HISTS[hkey].SetBinContent(ibin, scaleFactor)

    h = HISTS[hkey]
    p = Plotter.Plot(h, '', '', 'hist')

    canvas = Plotter.Canvas(lumi='2Mu2J', cWidth=1000)
    canvas.addMainPlot(p)

    p.SetLineColor(R.kBlue)

    setBinLabels(canvas)

    canvas.firstPlot.setTitles(X='Cut', Y='n#minus1 Eff.')
    canvas.firstPlot.SetMaximum(1.1)
    canvas.firstPlot.SetMinimum(0.)

    canvas.cleanup('pdfs/NM1_{}{}_2Mu2J.pdf'.format(hkey, BUMPSTRING))
makeIntegratedNM1Signal()
makeIntegratedNM1Signal(hkey='DSA-NM1')
