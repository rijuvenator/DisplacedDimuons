import ROOT as R
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
import DisplacedDimuons.Analysis.Plotter as Plotter
from DisplacedDimuons.Common.Utilities import SPStr, SPLumiStr 
import DisplacedDimuons.Analysis.HistogramGetter as HG
import DisplacedDimuons.Analysis.RootTools as RT
import DisplacedDimuons.Analysis.PlotterParser as PP
import operator

PiO2 = R.TMath.Pi()/2.

DATASCALE = 1433921./14334550.

FILES = {
    '2Mu2J' : R.TFile.Open('roots/NM1Distributions_Trig_HTo2XTo2Mu2J.root'),
    'MC'    : R.TFile.Open('roots/NM1Distributions_MC.root'               ),
    'MC_I'  : R.TFile.Open('roots/NM1Distributions_IDPHI_MC.root'         ),
    'Data'  : R.TFile.Open('roots/NM1Distributions_DATA.root'             ),
    'Data_I': R.TFile.Open('roots/NM1Distributions_IDPHI_DATA.root'       ),
}

CONFIG = {
    'nHits'   : {'val':12. , 'op':operator.gt},
    'FPTE'    : {'val':1.  , 'op':operator.lt},
    'pT'      : {'val':10. , 'op':operator.gt},
    'DCA'     : {'val':100., 'op':operator.lt},
    'LxyErr'  : {'val':99. , 'op':operator.lt},
    'mass'    : {'val':10. , 'op':operator.gt},
    'vtxChi2' : {'val':20. , 'op':operator.lt},
    'cosAlpha': {'val':-0.8, 'op':operator.gt},
    'Npp'     : {'val':10. , 'op':operator.lt},
    'LxySig'  : {'val':5.  , 'op':operator.gt},
    'trkChi2' : {'val':4.  , 'op':operator.lt},
    'nDTHits' : {'val':19. , 'op':operator.gt}, # this one is special, the line needs to be drawn at 19
    'deltaPhi': {'val':PiO2, 'op':operator.lt},
}

def fractionCut(hkey, h):
    val = CONFIG[hkey]['val']
    if hkey == 'deltaPhi':
        val -= 0.03

    if CONFIG[hkey]['op'] == operator.gt:
        total, cut = h.Integral(0, h.GetNbinsX()+1), h.Integral(h.FindBin(val), h.GetNbinsX()+1)
        return total, cut, float(cut)/total
    else:
        total, cut = h.Integral(0, h.GetNbinsX()+1), h.Integral(0, h.FindBin(val))
        return total, cut, float(cut)/total

def makeSignalPlot(hkey):
    HISTS = HG.getAddedSignalHistograms(FILES['2Mu2J'], '2Mu2J', hkey)
    h = HISTS[hkey]
    p = Plotter.Plot(h, '', '', 'hist')
    canvas = Plotter.Canvas(lumi='Signal: H#rightarrow2X#rightarrow2#mu + *', logy=True if hkey != 'nDTHits' else False)
    canvas.addMainPlot(p)
    p.SetLineColor(R.kBlue)
    canvas.firstPlot.SetMinimum(0.9)
    pave = canvas.makeStatsBox(p, color=R.kBlue)
    if hkey in ('nHits', 'LxySig'):
        Plotter.MOVE_OBJECT(pave, Y=-.3)
    canvas.mainPad.Update()
    if canvas.logy:
        line = R.TLine(CONFIG[hkey]['val'], canvas.firstPlot.GetMinimum(), CONFIG[hkey]['val'], 10.**(R.TMath.Log10(canvas.firstPlot.GetMaximum())*1.06))
    else:
        line = R.TLine(CONFIG[hkey]['val'], canvas.firstPlot.GetMinimum(), CONFIG[hkey]['val'],                     canvas.firstPlot.GetMaximum() *1.05 )
    line.Draw()
    line.SetLineStyle(2)
    print '\033[31m{:6s} {:8s} {:5.0f} {:5.0f} {:7.2%}\033[m'.format('Signal', hkey, *fractionCut(hkey, canvas.firstPlot.plot))
    RT.addBinWidth(canvas.firstPlot)
    canvas.cleanup('pdfs/NM1D_{}_2Mu2J.pdf'.format(hkey))

def makeMCPlot(hkey, DODATA=False, TENP=False):

    if DODATA:
        if not TENP:
            HISTS, PConfig = HG.getBackgroundHistograms(FILES['MC_I'], hkey)
            DATAHISTS, DataPConfig = HG.getDataHistograms(FILES['Data_I'], hkey)
            lumi = 'MC + Data, |#Delta#Phi| > #pi/2'
        else:
            HISTS, PConfig = HG.getBackgroundHistograms(FILES['MC'], hkey, extraScale=DATASCALE)
            DATAHISTS, DataPConfig = HG.getDataHistograms(FILES['Data'], hkey)
            lumi = 'MC + 10% Data'
    else:
        HISTS, PConfig = HG.getBackgroundHistograms(FILES['MC'], hkey)
        lumi = 'MC'

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

    canvas = Plotter.Canvas(lumi=lumi, logy=True if hkey != 'nDTHits' else False
        #ratioFactor=0. if not DODATA else 1./3., fontscale=1. if not DODATA else 1.+1./3.)
    )

    for key in HG.BGORDER:
        PLOTS[key].setColor(HG.PLOTCONFIG[key]['COLOR'], which='LF')

    canvas.addMainPlot(PLOTS['stack'])

    if DODATA:
        canvas.addMainPlot(PLOTS['data'])

    canvas.firstPlot.setTitles(X='', copy=HISTS[HG.BGORDER[0]])
    canvas.firstPlot.setTitles(Y='Normalized Counts')
    canvas.makeLegend(lWidth=.27, pos='tr', autoOrder=False, fontscale=0.8)# if not DODATA else 1.)
    if DODATA:
        canvas.addLegendEntry(PLOTS['data'])
    for ref in reversed(HG.BGORDER):
        canvas.addLegendEntry(PLOTS[ref])
    canvas.legend.resizeHeight()
    RT.addBinWidth(canvas.firstPlot)

    if canvas.logy:
        canvas.firstPlot.SetMinimum(1.)
        canvas.firstPlot.SetMaximum(500.)
    else:
        canvas.firstPlot.SetMinimum(0.)
        canvas.firstPlot.SetMaximum(10.)

    #if DODATA:
    #    canvas.makeRatioPlot(PLOTS['data'].plot, PLOTS['stack'].plot.GetStack().Last())
    #    canvas.firstPlot.scaleTitleOffsets(0.8, axes='Y')
    #    canvas.rat      .scaleTitleOffsets(0.8, axes='Y')
    #    canvas.rat.setTitles(X='', copy=canvas.firstPlot.plot)

    if canvas.logy:
        line = R.TLine(CONFIG[hkey]['val'], 0.45, CONFIG[hkey]['val'], 10.**(R.TMath.Log10(500.)*1.06))
    else:
        line = R.TLine(CONFIG[hkey]['val'], 0.  , CONFIG[hkey]['val'],                      10. *1.05 )
    line.Draw()
    line.SetLineStyle(2)
    if DODATA:
        print '\033[32m{:6s} {:8s} {:5.0f} {:5.0f} {:7.2%}\033[m'.format('Data'+('' if not TENP else '10'), hkey, *fractionCut(hkey, PLOTS['data']))

    canvas.cleanup('pdfs/NM1D_{}_MC{}{}.pdf'.format(hkey, '' if not DODATA else 'Data', '' if not TENP else '-10'))
    #canvas.finishCanvas(extrascale=1. if not DODATA else 1.+1./3.)
    #canvas.save()
    #canvas.deleteCanvas()

for hkey in CONFIG:
    makeSignalPlot(hkey)
    makeMCPlot(hkey)
    makeMCPlot(hkey, True)
    makeMCPlot(hkey, True, True)
