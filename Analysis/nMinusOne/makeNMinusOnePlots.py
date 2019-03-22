import ROOT as R
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
import DisplacedDimuons.Analysis.Plotter as Plotter
from DisplacedDimuons.Common.Utilities import SPStr, SPLumiStr 
import DisplacedDimuons.Analysis.HistogramGetter as HG
import DisplacedDimuons.Analysis.RootTools as RT
import DisplacedDimuons.Analysis.PlotterParser as PP

FILES = {
    '2Mu2J' : R.TFile.Open('roots/NM1Plots_Trig_HTo2XTo2Mu2J.root'),
    'MC'    : R.TFile.Open('roots/NM1Plots_MC.root'               )
}

CUTS = ('NS', 'NH', 'FPTE', 'HLT', 'PT', 'LXYE', 'MASS', 'CHI2')
PRETTY = ('n_{st}', 'n_{hits}', '#sigma_{p_{T}}/p_{T}', 'HLT-m', 'p_{T}', '#sigma_{L_{xy}}', 'M(#mu#mu)', 'vtx #chi^{2}')
#PRETTY = CUTS[:]
PRETTY = dict(zip(CUTS, PRETTY))

def setBinLabels(canvas):
    xaxis = canvas.firstPlot.GetXaxis()
    xaxis.SetBinLabel(1, 'none')
    for ibin, cut in enumerate(CUTS):
        xaxis.SetBinLabel(ibin+2, PRETTY[cut])

    canvas.firstPlot.scaleLabels(1.4, axes='X')

def makeIntegratedSEQMC():
    HISTS, PConfig = HG.getBackgroundHistograms(FILES['MC'], 'SEQ')
    HISTS = HISTS['SEQ']
    PConfig = PConfig['SEQ']

    PLOTS = {}
    for key in HG.BGORDER + ('stack',):
        PLOTS[key] = Plotter.Plot(HISTS[key], *PConfig[key])

    canvas = Plotter.Canvas(lumi='MC', logy=True)

    for key in HG.BGORDER:
        PLOTS[key].setColor(HG.PLOTCONFIG[key]['COLOR'], which='LF')

    canvas.addMainPlot(PLOTS['stack'])

    setBinLabels(canvas)

    canvas.makeLegend(lWidth=.27, pos='tr', autoOrder=False, fontscale=0.8)
    for ref in reversed(HG.BGORDER):
        canvas.addLegendEntry(PLOTS[ref])
    canvas.legend.resizeHeight()

    canvas.firstPlot.setTitles(X='Cut', Y='Normalized Counts')
    canvas.firstPlot.SetMaximum(2.e7)
    canvas.firstPlot.SetMinimum(1.e4)

    canvas.cleanup('pdfs/NM1_{}_MC.pdf'.format('SEQ'))
makeIntegratedSEQMC()

def makeIntegratedSEQSignal():
    HISTS = HG.getAddedSignalHistograms(FILES['2Mu2J'], '2Mu2J', 'SEQ')

    h = HISTS['SEQ']
    p = Plotter.Plot(h, '', '', 'hist')

    canvas = Plotter.Canvas(lumi='2Mu2J')
    canvas.addMainPlot(p)

    p.SetLineColor(R.kBlue)

    setBinLabels(canvas)

    canvas.firstPlot.setTitles(X='Cut', Y='Normalized Counts')
    canvas.firstPlot.SetMaximum(3.e5)
    canvas.firstPlot.SetMinimum(0.)

    canvas.cleanup('pdfs/NM1_{}_2Mu2J.pdf'.format('SEQ'))
makeIntegratedSEQSignal()

def makeIntegratedNM1MC():

    ### modified version of getBackgroundHistograms

    FILE = FILES['MC']
    keylist = ['NM1']
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

    HISTS = HISTS['NM1']
    PConfig = PConfig['NM1']

    PLOTS = {}
    for key in HG.BGORDER + ('stack',):
        PLOTS[key] = Plotter.Plot(HISTS[key], *PConfig[key])

    canvas = Plotter.Canvas(lumi='MC', logy=False)

    for key in HG.BGORDER:
        PLOTS[key].setColor(HG.PLOTCONFIG[key]['COLOR'], which='LF')

    canvas.addMainPlot(PLOTS['stack'])

    setBinLabels(canvas)

    canvas.makeLegend(lWidth=.27, pos='tr', autoOrder=False, fontscale=0.8)
    for ref in reversed(HG.BGORDER):
        canvas.addLegendEntry(PLOTS[ref])
    canvas.legend.resizeHeight()

    canvas.firstPlot.setTitles(X='Cut', Y='n#minus1 Eff.')
    canvas.firstPlot.SetMaximum(1.e0)
    canvas.firstPlot.SetMinimum(1.e-3)

    canvas.cleanup('pdfs/NM1_{}_MC.pdf'.format('NM1'))
makeIntegratedNM1MC()

def makeIntegratedNM1Signal():

    #HISTS, INDIV = HG.getAddedSignalHistograms(FILES['2Mu2J'], '2Mu2J', 'NM1', getIndividuals=True)

    #totalBin1 = sum([INDIV['NM1'][ref].GetBinContent(1) for ref in SIGNALPOINTS])
    #for ibin in range(1, len(CUTS)+2):
    #    totalBin = sum([INDIV['NM1'][ref].GetBinContent(ibin) for ref in SIGNALPOINTS])
    #    scaleFactor = totalBin1/totalBin
    #    for ref in SIGNALPOINTS:
    #        INDIV['NM1'][ref].SetBinContent(ibin, INDIV['NM1'][ref].GetBinContent(ibin)/totalBin*scaleFactor)

    HISTS = HG.getAddedSignalHistograms(FILES['2Mu2J'], '2Mu2J', 'NM1')
    totalBin1 = HISTS['NM1'].GetBinContent(1)
    for ibin in range(1, len(CUTS)+2):
        totalBin = HISTS['NM1'].GetBinContent(ibin)
        scaleFactor = totalBin1/totalBin
        HISTS['NM1'].SetBinContent(ibin, scaleFactor)

    h = HISTS['NM1']
    p = Plotter.Plot(h, '', '', 'hist')

    canvas = Plotter.Canvas(lumi='2Mu2J')
    canvas.addMainPlot(p)

    p.SetLineColor(R.kBlue)

    setBinLabels(canvas)

    canvas.firstPlot.setTitles(X='Cut', Y='n#minus1 Eff.')
    canvas.firstPlot.SetMaximum(1.1)
    canvas.firstPlot.SetMinimum(0.)

    canvas.cleanup('pdfs/NM1_{}_2Mu2J.pdf'.format('NM1'))
makeIntegratedNM1Signal()
