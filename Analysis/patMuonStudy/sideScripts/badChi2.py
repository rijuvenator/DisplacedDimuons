import ROOT as R
import numpy as np
import DisplacedDimuons.Analysis.Plotter as Plotter
import sys

fname = 'text/MC_eventsWithLxySigAbove20.txt'
if len(sys.argv) > 1:
    fname = sys.argv[1]

# this script takes events with Lxy Sig > 100 and plots the crappy chi^2
# really, it just needs a file with chi2 being the last column
# there are many scripts that do the required event line printing

#h = R.TH1F('h', ';vtx #chi^{2}/dof;Counts', 100, np.logspace(-3., 8., 101))
h = R.TH1F('h', ';vtx #chi^{2}/dof;Counts', 100, 0., 50.)

with open(fname) as f:
    for line in f:
        if 'DY50' not in line: continue
        if 'PAT' not in line: continue
        cols = line.strip('\n').split()
        chi2 = float(cols[-3])
        h.Fill(chi2)

p = Plotter.Plot(h, '', '', 'hist')
canvas = Plotter.Canvas(logy=True)
canvas.addMainPlot(p)
p.setColor(R.kBlue, which='L')
pave = canvas.makeStatsBox(p, R.kBlue)
Plotter.MOVE_OBJECT(pave, X=-.5)
#canvas.mainPad.SetLogx()
canvas.scaleMargins(0.8, 'L')
canvas.firstPlot.scaleTitleOffsets(1.2, 'X')
canvas.cleanup('pdfs/badChi2.pdf')

cum = h.GetCumulative()
cum.Scale(1./h.Integral(0, h.GetNbinsX()+1))

findAt = 50.
for ibin in xrange(1, h.GetNbinsX()):
    if cum.GetXaxis().GetBinLowEdge(ibin) > findAt:
        print '{:.1f} : {:.4f}'.format(findAt, cum.GetBinContent(ibin))
        break

p = Plotter.Plot(cum, '', '', 'hist')
canvas = Plotter.Canvas()
canvas.addMainPlot(p)
p.setColor(R.kBlue, which='L')
canvas.mainPad.SetLogx()
canvas.scaleMargins(0.9, 'L')
canvas.firstPlot.scaleTitleOffsets(1.2, 'X')
canvas.cleanup('pdfs/badChi2_Cum.pdf')
