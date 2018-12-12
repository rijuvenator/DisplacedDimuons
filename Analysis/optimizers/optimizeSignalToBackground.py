import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
from DisplacedDimuons.Common.Utilities import SPStr, SPLumiStr
import DisplacedDimuons.Analysis.AnalysisTools as AT
import DisplacedDimuons.Analysis.HistogramGetter as HG

R.gStyle.SetPadTickY(0)

FILES = {'PrMC':R.TFile.Open('../analyzers/roots/Main/DimuonPlots_Prompt_NS_NH_FPTE_HLT_PT_PC_NoSignal.root'),
         'NPMC':R.TFile.Open('../analyzers/roots/Main/DimuonPlots_NoPrompt_NS_NH_FPTE_HLT_PT_PC_MCOnly.root'),
         'PrSi':R.TFile.Open('../analyzers/roots/Main/DimuonPlots_Trig_Prompt_NS_NH_FPTE_HLT_PT_PC_SignalOnly.root'),
         'NPSi':R.TFile.Open('../analyzers/roots/Main/DimuonPlots_Trig_NoPrompt_NS_NH_FPTE_HLT_PT_PC_SignalOnly.root')
}

BGORDER = ('WJets', 'WW', 'WZ', 'ZZ', 'tW', 'tbarW', 'ttbar', 'QCD20toInf-ME', 'DY10to50', 'DY50toInf')

PC = HG.PLOTCONFIG

quantity = 'deltaR'
qkeyname = 'Dim_{}VSdeltaPhi'.format(quantity)
sp = (400, 50, 80)

deltaPhiBG = R.THStack('h_deltaPhi_BG', '')
quantityBG2D = HG.getHistogram(FILES['PrMC'], BGORDER[0], qkeyname)
quantityBG2D.Scale(PC[BGORDER[0]]['WEIGHT'])
h = {}
for key in BGORDER:
    for fname in ('PrMC', 'NPMC'):
        h[key+fname+'deltaPhi'] = HG.getHistogram(FILES[fname], key, 'Dim_deltaPhi')
        h[key+fname+'deltaPhi'].Scale(PC[key]['WEIGHT'])
        deltaPhiBG.Add(h[key+fname+'deltaPhi'])

        if fname == 'PrMC' and key == 'WJets': continue

        h[key+fname+'{}VSdeltaPhi'.format(quantity)] = HG.getHistogram(FILES[fname], key, qkeyname)
        h[key+fname+'{}VSdeltaPhi'.format(quantity)].Scale(PC[key]['WEIGHT'])
        quantityBG2D.Add(h[key+fname+quantity+'VSdeltaPhi'])
deltaPhiSig = HG.getHistogram(FILES['PrSi'], ('2Mu2J', sp), 'Dim_deltaPhi')
deltaPhiSig.Add(HG.getHistogram(FILES['NPSi'], ('2Mu2J', sp), 'Dim_deltaPhi'))

tau = deltaPhiBG.GetStack().Last().Integral(501, 1000)/deltaPhiBG.GetStack().Last().Integral(0, 500)

sigDist2D = HG.getHistogram(FILES['PrSi'], ('2Mu2J', sp), qkeyname)
sigDist2D.Add(HG.getHistogram(FILES['NPSi'], ('2Mu2J', sp), qkeyname))
sigDist = sigDist2D.ProjectionY('LessSig', 0, 500)
BGDist = quantityBG2D.ProjectionY('LessBG', 0, 500)

print sigDist.Integral()
print BGDist.Integral()

print sigDist2D.ProjectionY('MoreSig', 501, 1000).Integral()
print quantityBG2D.ProjectionY('MoreBG', 501, 1000).Integral()

FOM = AT.ZBi


def optimizeCut(sig, bg):
    # get histograms
    s = sig
    b = bg

    s.Scale(18043.34)

    # get cumulatives
    sCum = s.GetCumulative()
    bCum = b.GetCumulative()
    fom  = sCum.Clone()

    # fill f.o.m. histogram, and keep track of max f.o.m. and cut value
    nBins = sCum.GetNbinsX()
    xAxis = sCum.GetXaxis()
    fom_max = 0.
    opt_cut = 0.
    for ibin in range(1,nBins+1):
        val = FOM(sCum.GetBinContent(ibin)+bCum.GetBinContent(ibin), bCum.GetBinContent(ibin), tau)
        if val > fom_max:
            fom_max = val
            opt_cut = xAxis.GetBinCenter(ibin)
        fom.SetBinContent(ibin, val)

    # make plots
    p = {}
    p['sig'] = Plotter.Plot(sCum, 'matched'     , 'l', 'hist')
    p['bg' ] = Plotter.Plot(bCum, 'other'       , 'l', 'hist')
    p['fom'] = Plotter.Plot(fom , 'S/#sqrt{S+B}', 'l', 'hist')

    # make canvas, colors, maximum
    canvas = Plotter.Canvas(lumi='')
    canvas.addMainPlot(p['sig'])
    canvas.addMainPlot(p['bg' ])
    canvas.addMainPlot(p['fom'])

    p['sig'].SetLineColor(R.kBlue )
    p['bg' ].SetLineColor(R.kRed  )
    p['fom'].SetLineColor(R.kGreen)

    canvas.setMaximum()

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

    # draw optimum text and line
    x, y = canvas.legend.GetX1(), canvas.legend.GetY2()
    canvas.drawText(text='#color[{:d}]{{opt. cut = {:.2f}}}'.format(R.kBlack, opt_cut), pos=(x, y+0.05), align='bl')

    line = R.TLine(opt_cut, 0., opt_cut, canvas.firstPlot.GetMaximum())
    line.SetLineStyle(2)
    line.Draw()

    # save
    canvas.cleanup('OPT_{}_HTo2XTo{}_{}.pdf'.format(quantity, '2Mu2J', SPStr(sp)))

optimizeCut(sigDist, BGDist)
