import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter

R.gStyle.SetMarkerStyle(R.kDot)

f = R.TFile.Open('Dalitz.root')

for M in xrange(50, 201, 10):
    for sample in ('Data', 'DY50toInf'):
        h = f.Get('hDalitz_{}_{}'.format(M, sample))

        pA = h.ProjectionY('_py'+str(M), 100, 100)
        pB = h.ProjectionX('_px'+str(M), 100, 100)

        print sample, M, pA.GetBinCenter(pA.GetMaximumBin()), pB.GetBinCenter(pB.GetMaximumBin()), pA.GetMean(), pB.GetMean()

        p = Plotter.Plot(h, '', '', 'colz')
        c = Plotter.Canvas(lumi='{}, M = {}'.format(sample, M))
        c.addMainPlot(p)
        c.scaleMargins(1.5, 'R')
        c.scaleMargins(0.8, 'L')
        c.cleanup('dalitz_{}_{}.pdf'.format(sample, M))

