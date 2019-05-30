import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.HistogramGetter as HG

f = R.TFile.Open('roots/PTCutPlots_2Mu2J.root')
h = HG.getHistogram(f, ('2Mu2J', (1000, 150, 100)), 'nMatches')
p = Plotter.Plot(h, '', '', 'hist')
c = Plotter.Canvas(lumi='2Mu2J (1000 GeV, 150 GeV, 100 mm)', cWidth=600, fontscale=.8)
c.addMainPlot(p)
p.SetLineColor(R.kBlue)
p.scaleTitleOffsets(1.5, axes='Y')
p.setTitles(X='p_{T} Cut [GeV]', Y='N(signal gen matches)')
c.finishCanvas(extrascale=.8)
c.save('x.pdf')
