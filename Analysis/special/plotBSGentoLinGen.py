import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
from DisplacedDimuons.Common.Utilities import SPStr

# first 3 plots are from ResTest
# last 2 plots are from RefPointTest
config = (
    ('pT'    , ('RG', 'BS'), ('normal' , 'beamspot'), 'tr', -.1),
    ('d0'    , ('RG', 'BS'), ('normal' , 'beamspot'), 'tl',   0),
    ('deltaR', ('RG', 'BS'), ('normal' , 'beamspot'), 'tr', -.1),
    ('Lxy'   , ('ZZ', 'BS'), ('(0,0,0)', 'beamspot'), 'tl',   0),
    ('d0G'   , ('ZZ', 'BS'), ('(0,0,0)', 'beamspot'), 'tl',   0),
)

f = R.TFile.Open('roots/ResTest.root')
f = R.TFile.Open('roots/RefPointTest.root')
for fs in ('2Mu2J', '4Mu'):
    for sp in SIGNALPOINTS:
        for quantity, names, legends, lpos, movement in config:
            ResString = 'Res' if quantity != 'deltaR' else ''
            h1 = f.Get('{}{}{}_HTo2XTo{}_{}'.format(quantity, ResString, names[0], fs, SPStr(sp)))
            h2 = f.Get('{}{}{}_HTo2XTo{}_{}'.format(quantity, ResString, names[1], fs, SPStr(sp)))

            p1 = Plotter.Plot(h1, legends[0], 'l', 'hist')
            p2 = Plotter.Plot(h2, legends[1], 'l', 'hist')

            canvas = Plotter.Canvas(lumi='{} ({}, {}, {})'.format(fs, *sp))
            canvas.addMainPlot(p1)
            canvas.addMainPlot(p2)

            canvas.makeLegend(pos=lpos)
            canvas.legend.resizeHeight()
            canvas.legend.moveLegend(X=movement)

            p1.SetLineColor(R.kRed)
            p2.SetLineColor(R.kBlue)

            canvas.setMaximum()

            canvas.cleanup('{}{}_Compare_HTo2XTo{}_{}.pdf'.format(quantity, ResString, fs, SPStr(sp)))
