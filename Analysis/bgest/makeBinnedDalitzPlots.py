import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter

R.gStyle.SetMarkerStyle(R.kDot)

f = R.TFile.Open('Dalitz.root')
#f = R.TFile.Open('Dalitz_7.root')
#f = R.TFile.Open('DalitzSignal.root')

#for sample in ('Signal',):
for sample in ('Data','DY50toInf'):
    h = f.Get('hDalitz_{}'.format(sample))

    for ibin in xrange(1, 21):

        M = 50 + (ibin-1)*10

        #pA = h.Project3D('y')
        #pB = h.Project3D('x')

        #print sample, M, pA.GetBinCenter(pA.GetMaximumBin()), pB.GetBinCenter(pB.GetMaximumBin()), pA.GetMean(), pB.GetMean()

        h.GetZaxis().SetRange(ibin, ibin)
        h2D = h.Project3D('{}_xy'.format(ibin))

        num = h2D.Integral(95, 100, 1, 100)+h2D.Integral(1, 100, 95, 100)-h2D.Integral(95, 100, 95, 100)
        print '{:3d} {:4.0f} {:4.0f} {:.2%}'.format( M, h2D.Integral(), num, num/h2D.Integral() )

        p = Plotter.Plot(h2D, '', '', 'colz')
        c = Plotter.Canvas(lumi='{}, M = {}'.format(sample, M))
        c.addMainPlot(p)
        c.scaleMargins(1.5, 'R')
        c.scaleMargins(0.8, 'L')
        c.cleanup('dalitz_{}_{}.pdf'.format(sample, M))
