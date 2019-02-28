import ROOT as R
import numpy as np
import DisplacedDimuons.Analysis.Plotter as Plotter
import sys

fname = 'text/DY50toInf_eventsWithLxySigAbove100.txt'
if len(sys.argv) > 1:
    fname = sys.argv[1]

# this script takes DY events with Lxy Sig > 100 and plots the crappy chi^2
# uses event lines from dumpEvent.py

h = R.TH1F('h', ';vtx #chi^{2}/dof;Counts', 200, np.logspace(-3., 8., 201))

with open(fname) as f:
    for line in f:
        cols = line.strip('\n').split()
        chi2 = float(cols[-1])
        h.Fill(chi2)

p = Plotter.Plot(h, '', '', 'hist')
canvas = Plotter.Canvas()
canvas.addMainPlot(p)
p.setColor(R.kBlue, which='L')
pave = canvas.makeStatsBox(p, R.kBlue)
Plotter.MOVE_OBJECT(pave, X=-.5)
canvas.mainPad.SetLogx()
canvas.scaleMargins(0.8, 'L')
canvas.firstPlot.scaleTitleOffsets(1.2, 'X')
canvas.cleanup('pdfs/badChi2.pdf')

cum = h.GetCumulative()
cum.Scale(1./h.Integral(0, h.GetNbinsX()+1))

findAt = 10.
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
