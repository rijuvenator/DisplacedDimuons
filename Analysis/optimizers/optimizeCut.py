import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
from DisplacedDimuons.Common.Utilities import SPStr, SPLumiStr
import DisplacedDimuons.Analysis.AnalysisTools as AT
import DisplacedDimuons.Analysis.HistogramGetter as HG
from OptimizerTools import SignalInfo, ScaleFactor, calculateFOM

FIGURE_OF_MERIT = 'ZBi'
#FIGURE_OF_MERIT = 'ZPL'

PRETTY_LEG = {'ZBi':'Z_{Bi}', 'ZPL':'Z_{PL}'}[FIGURE_OF_MERIT]

R.gStyle.SetPadTickY(0)

DATA = {'2Mu2J':{}, '4Mu':{}}

FILES = {
    'Signal' : R.TFile.Open('../nMinusOne/roots/NM1Distributions_Trig_HTo2XTo2Mu2J.root'),
    'Data'   : R.TFile.Open('../nMinusOne/roots/NM1Distributions_IDPHI_DATA.root'),
}

CONFIG = {
    'nHits'   : {'forward':False, 'pretty':'muon N(CSC+DT Hits'     },
    'FPTE'    : {'forward':True , 'pretty':'muon sigma pT / pT'     },
    'pT'      : {'forward':False, 'pretty':'muon pT'                },
    'DCA'     : {'forward':True , 'pretty':'dimuon D.C.A.'          },
    'LxyErr'  : {'forward':True , 'pretty':'dimuon sigma Lxy'       },
    'mass'    : {'forward':False, 'pretty':'dimuon M(mu mu)'        },
    'vtxChi2' : {'forward':True , 'pretty':'dimuon vtx chi^2'       },
    'cosAlpha': {'forward':False, 'pretty':'dimuon orig. cos(alpha)'},
    'Npp'     : {'forward':True , 'pretty':'event N(parallel pairs)'},
    'LxySig'  : {'forward':False, 'pretty':'dimuon Lxy / sigma Lxy' },
    'trkChi2' : {'forward':True , 'pretty':'muon trk chi^2/dof'     },
    'nDTHits' : {'forward':False, 'pretty':'barrel muon N(DT Hits)' },
}

if FIGURE_OF_MERIT == 'ZBi':
    def FOM(nOn, nOff):
        return AT.ZBi(nOn, nOff, 1.)
    FOMLeg = 'Z_{Bi}'
elif FIGURE_OF_MERIT == 'ZPL':
    def FOM(nOn, nOff):
        return AT.ZPL(nOn, nOff, 1.)
    FOMLeg = 'Z_{PL}'

def optimizeCut(fs, sp, quantity):
    # get histograms
    s = HG.getHistogram(FILES['Signal'], (fs, sp), quantity)
    DHists, DPConfig = HG.getDataHistograms(FILES['Data'], quantity)
    b = DHists[quantity]['data']

    n = s.Integral(0, s.GetNbinsX()+1)
    s.Scale(ScaleFactor(sp))

    # get cumulatives
    sCum = s.GetCumulative(CONFIG[quantity]['forward'])
    bCum = b.GetCumulative(CONFIG[quantity]['forward'])
    fom  = sCum.Clone()

    print '**** Data (|DeltaPhi| > Pi/2) vs. HTo2XTo{} ({} GeV, {} GeV, {} mm) (|DeltaPhi| < Pi/2)'.format(fs, *sp)
    print '**** Quantity = {:s} ::: Passing (N-1) = {:.0f} ::: N_gen = {:.0f} ::: Sigma*B = {:.3f} pb ::: 2016 ILumi = 35922 /pb'.format(
            CONFIG[quantity]['pretty'], n, SignalInfo[sp]['sumWeights'][1], SignalInfo[sp]['sigmaBLimit'])
    print '{:>8s} {:>7s} {:>7s} {:>7s} {:>6s} {:>6s}'.format('CutVal', 'S', 'B=nOff', 'S+B=nOn', 'ZBi', 'ZPL')

    # fill f.o.m. histogram, and keep track of max f.o.m. and cut value
    nBins = sCum.GetNbinsX()
    xAxis = sCum.GetXaxis()

    fom_max = 0.
    opt_cut = 0.
    opt_s   = 0.
    opt_b   = 0.

    for ibin in range(1,nBins+1):
        S, B, cutVal, FOMs = calculateFOM(s, b, sCum, bCum, nBins, ibin, xAxis, CONFIG[quantity]['forward'])
        print '{:8.3f} {:7.3f} {:7.3f} {:7.3f} {:6.3f} {:6.3f}'.format(cutVal, S, B, S+B, FOMs['ZBi'], FOMs['ZPL'])

        if FOMs[FIGURE_OF_MERIT] > fom_max:
            fom_max = FOMs[FIGURE_OF_MERIT]
            opt_cut = cutVal
            opt_s   = S
            opt_b   = B

        fom.SetBinContent(ibin, FOMs[FIGURE_OF_MERIT])

    # make plots
    p = {}
    p['sig'] = Plotter.Plot(sCum, 'signal'   , 'l', 'hist')
    p['bg' ] = Plotter.Plot(bCum, 'data'     , 'l', 'hist')
    p['fom'] = Plotter.Plot(fom , PRETTY_LEG , 'l', 'hist')

    # make canvas, colors, maximum
    canvas = Plotter.Canvas(lumi=SPLumiStr(fs, *sp))
    canvas.addMainPlot(p['sig'])
    canvas.addMainPlot(p['bg' ])
    canvas.addMainPlot(p['fom'])

    p['sig'].SetLineColor(R.kBlue )
    p['bg' ].SetLineColor(R.kRed  )
    p['fom'].SetLineColor(R.kGreen)

    canvas.setMaximum()
    canvas.firstPlot.SetMinimum(0.)

    # scale f.o.m. and make new axis
    fom.Scale(canvas.firstPlot.GetMaximum()/fom_max/1.05)
    axis = R.TGaxis(xAxis.GetXmax(), 0., xAxis.GetXmax(), canvas.firstPlot.GetMaximum(), 0., fom_max*1.05, 510, '+L')
    for attr in ('LabelFont', 'LabelOffset', 'TitleFont', 'TitleOffset', 'TitleSize'):
        getattr(axis, 'Set'+attr)(getattr(xAxis, 'Get'+attr)())
    axis.SetTitle('Figure of Merit')
    axis.CenterTitle()
    axis.Draw()
    canvas.scaleMargins(1.1, edges='R')

    # make the legend after
    canvas.makeLegend(lWidth=.2, pos='br')
    canvas.legend.resizeHeight()
    canvas.legend.moveLegend(X=-.2, Y=.1)

    # draw optimum text and line
    x, y = canvas.legend.GetX1(), canvas.legend.GetY2()
    canvas.drawText(text='#color[{:d}]{{opt. cut = {:.2f}}}'.format(R.kBlack, opt_cut), pos=(x, y+0.05), align='bl')

    line = R.TLine(opt_cut, 0., opt_cut, canvas.firstPlot.GetMaximum())
    line.SetLineStyle(2)
    line.Draw()

    # save
    canvas.cleanup('pdfs/OPT_{}_{}_HTo2XTo{}_{}.pdf'.format(quantity, FIGURE_OF_MERIT, fs, SPStr(sp)))

for fs in ('2Mu2J',):
    for sp in ((1000, 150, 1000),):
        for quantity in CONFIG:
            optimizeCut(fs, sp, quantity)
