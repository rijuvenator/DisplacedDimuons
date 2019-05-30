import DisplacedDimuons.Analysis.SummaryPlotter as SumPlotter
R, makeSummaryPlot, initializeData, Plotter = SumPlotter.R, SumPlotter.makeSummaryPlot, SumPlotter.initializeData, SumPlotter.Plotter
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
import DisplacedDimuons.Analysis.HistogramGetter as HG

f = R.TFile.Open('roots/ZephyrPlots_Trig_Combined_NS_NH_FPTE_HLT_REP_PQ1_PT_PC_LXYE_MASS_CHI2_DPT_HTo2XTo2Mu2J.root')

DATA = initializeData()

for sp in SIGNALPOINTS:
    h = HG.getHistogram(f, ('2Mu2J', sp), 'PAT-12-isMedium')
    DATA['2Mu2J'][sp]['med'] = h.GetBinContent(2, 2)/(h.GetBinContent(1, 1) + h.GetBinContent(1, 2) + h.GetBinContent(2, 1) + h.GetBinContent(2, 2)) * 100.
    print '{:4d} {:3d} {:4d}'.format(*sp),
    print '{:5.0f} {:5.0f} {:.2%}'.format(
            h.GetBinContent(1, 1) + h.GetBinContent(1, 2) + h.GetBinContent(2, 1) + h.GetBinContent(2, 2),
            h.GetBinContent(2, 2),
            h.GetBinContent(2, 2)/(h.GetBinContent(1, 1) + h.GetBinContent(1, 2) + h.GetBinContent(2, 1) + h.GetBinContent(2, 2))
    )

makeSummaryPlot(
    DATA,
    '2Mu2J',
    ('med',),
    ';;% both medium',
    {'med':'% both medium'},
    {'med':R.kRed},
    {'min':0., 'max':100.},
    'MED.pdf'
)

HISTS = HG.getAddedSignalHistograms(f, '2Mu2J', 'PAT-normChi2VSisMedium')
p = {}
p['not'] = Plotter.Plot(HISTS['PAT-normChi2VSisMedium'].ProjectionY('not', 1, 1), 'not medium', 'lp', 'hist')
p['med'] = Plotter.Plot(HISTS['PAT-normChi2VSisMedium'].ProjectionY('med', 2, 2), 'medium', 'lp', 'hist')
canvas = Plotter.Canvas(logy=True)
canvas.addMainPlot(p['med'])
canvas.addMainPlot(p['not'])
p['not'].setColor(R.kRed, which='LM')
p['med'].setColor(R.kBlue, which='LM')
p['not'].Scale(1./p['not'].Integral(0, p['not'].GetNbinsX()+1))
p['med'].Scale(1./p['med'].Integral(0, p['med'].GetNbinsX()+1))
canvas.makeLegend(lWidth=.2)
canvas.legend.resizeHeight()
canvas.firstPlot.setTitles(X='trk #chi^{2}/dof', Y='Counts')

for key in ('not', 'med'):
    h = p[key]
    binNum = h.FindBin(19.95)
    h.SetBinContent(binNum, h.GetBinContent(binNum) + h.Integral(binNum, h.GetNbinsX()+1))

canvas.firstPlot.GetXaxis().SetRangeUser(0., 20.)
canvas.cleanup('MED_trkChi2.pdf')

#

HISTS = HG.getAddedSignalHistograms(f, '2Mu2J', 'PAT-isMediumVSGEN-Lxy')
h = {}
h['not'] = HISTS['PAT-isMediumVSGEN-Lxy'].ProjectionX('not', 1, 2)
h['med'] = HISTS['PAT-isMediumVSGEN-Lxy'].ProjectionX('med', 2, 2)
for key in h:
    h[key].Rebin(10)
g = R.TGraphAsymmErrors(h['med'], h['not'], 'cp')
p = Plotter.Plot(g, '', '', 'p')
canvas = Plotter.Canvas()
canvas.addMainPlot(p)
p.setColor(R.kBlue, which='LM')
canvas.firstPlot.setTitles(X='gen L_{xy} [cm]', Y='Fraction medium')
canvas.cleanup('MED_medVLxy.pdf')
