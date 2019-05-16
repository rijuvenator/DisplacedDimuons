import ROOT as R
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
import DisplacedDimuons.Analysis.Plotter as Plotter
from DisplacedDimuons.Common.Utilities import SPStr, SPLumiStr 
import DisplacedDimuons.Analysis.HistogramGetter as HG
import DisplacedDimuons.Analysis.RootTools as RT
import DisplacedDimuons.Analysis.PlotterParser as PP

FILES = {
    '2Mu2J' : R.TFile.Open('roots/NM1Distributions_Trig_HTo2XTo2Mu2J.root'),
    'MC'    : R.TFile.Open('roots/NM1Distributions_MC.root'               ),
    'MC_I'  : R.TFile.Open('roots/NM1Distributions_IDPHI_MC.root'         ),
    'Data'  : R.TFile.Open('roots/NM1Distributions_DATA.root'             ),
}

CONFIG = {
    'nHits'   : {'val':12. },
    'FPTE'    : {'val':1.  },
    'pT'      : {'val':10. },
    'DCA'     : {'val':100.},
    'LxyErr'  : {'val':99. },
    'mass'    : {'val':10. },
    'vtxChi2' : {'val':20. },
    'cosAlpha': {'val':-0.8},
    'Npp'     : {'val':10. },
    'LxySig'  : {'val':5.  },
    'trkChi2' : {'val':4.  },
}

def makeSignalPlot(hkey):
    HISTS = HG.getAddedSignalHistograms(FILES['2Mu2J'], '2Mu2J', hkey)
    h = HISTS[hkey]
    p = Plotter.Plot(h, '', '', 'hist')
    canvas = Plotter.Canvas(lumi='Signal: H#rightarrow2X#rightarrow2#mu + *', logy=True)
    canvas.addMainPlot(p)
    p.SetLineColor(R.kBlue)
    canvas.firstPlot.SetMinimum(0.9)
    pave = canvas.makeStatsBox(p, color=R.kBlue)
    if hkey in ('nHits', 'LxySig'):
        Plotter.MOVE_OBJECT(pave, Y=-.3)
    canvas.mainPad.Update()
    line = R.TLine(CONFIG[hkey]['val'], canvas.firstPlot.GetMinimum(), CONFIG[hkey]['val'], 10.**(R.TMath.Log10(canvas.firstPlot.GetMaximum())*1.06))
    line.Draw()
    line.SetLineStyle(2)
    canvas.cleanup('pdfs/NM1D_{}_2Mu2J.pdf'.format(hkey))

def makeMCPlot(hkey, DODATA=False):

    if DODATA:
        HISTS, PConfig = HG.getBackgroundHistograms(FILES['MC_I'], hkey)#, extraScale=DATASCALE)
        DATAHISTS, DataPConfig = HG.getDataHistograms(FILES['Data'], hkey)
        lumi = 'MC + Data, |#Delta#Phi| > #pi/2'
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

    canvas = Plotter.Canvas(lumi=lumi, logy=True,
        #ratioFactor=0. if not DODATA else 1./3., fontscale=1. if not DODATA else 1.+1./3.)
    )

    for key in HG.BGORDER:
        PLOTS[key].setColor(HG.PLOTCONFIG[key]['COLOR'], which='LF')

    canvas.addMainPlot(PLOTS['stack'])

    if DODATA:
        canvas.addMainPlot(PLOTS['data'])

    canvas.makeLegend(lWidth=.27, pos='tr', autoOrder=False, fontscale=0.8)# if not DODATA else 1.)
    if DODATA:
        canvas.addLegendEntry(PLOTS['data'])
    for ref in reversed(HG.BGORDER):
        canvas.addLegendEntry(PLOTS[ref])
    canvas.legend.resizeHeight()

    canvas.firstPlot.SetMinimum(1.)
    canvas.firstPlot.SetMaximum(500.)

    canvas.firstPlot.setTitles(X='', Y='', copy=HISTS[HG.BGORDER[0]])
    #if DODATA:
    #    canvas.makeRatioPlot(PLOTS['data'].plot, PLOTS['stack'].plot.GetStack().Last())
    #    canvas.firstPlot.scaleTitleOffsets(0.8, axes='Y')
    #    canvas.rat      .scaleTitleOffsets(0.8, axes='Y')
    #    canvas.rat.setTitles(X='', copy=canvas.firstPlot.plot)

    line = R.TLine(CONFIG[hkey]['val'], canvas.firstPlot.GetMinimum(), CONFIG[hkey]['val'], 10.**(R.TMath.Log10(500.)*1.06))
    line.Draw()
    line.SetLineStyle(2)

    canvas.cleanup('pdfs/NM1D_{}_MC{}.pdf'.format(hkey, '' if not DODATA else 'Data'))
    #canvas.finishCanvas(extrascale=1. if not DODATA else 1.+1./3.)
    #canvas.save()
    #canvas.deleteCanvas()

for hkey in CONFIG:
    makeSignalPlot(hkey)
    makeMCPlot(hkey)
    makeMCPlot(hkey, True)
