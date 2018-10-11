import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
from DisplacedDimuons.Common.Utilities import SPStr

# first 3 plots are from ResTest
# last 2 plots are from RefPointTest
config = (
    ('pT'      , ('RG', 'BS'), ('secondary vertex' , 'beamspot'), 'tr', -.15),
    ('d0'      , ('RG', 'BS'), ('secondary vertex' , 'beamspot'), 'tl',    0),
    ('deltaR'  , ('RG', 'BS'), ('secondary vertex' , 'beamspot'), 'tr', -.15),
    ('deltaphi', ('RG', 'BS'), ('secondary vertex' , 'beamspot'), 'tr', -.15),
    ('deltaEta', ('RG', 'BS'), ('secondary vertex' , 'beamspot'), 'tr', -.15),
    ('Lxy'     , ('ZZ', 'BS'), ('(0,0,0)', 'beamspot'), 'tl',   0),
    ('d0G'     , ('ZZ', 'BS'), ('(0,0,0)', 'beamspot'), 'tl',   0),
)

f = R.TFile.Open('roots/ResTest_HTo2XTo2Mu2J_125_20_1300.root')
f = R.TFile.Open('roots/ResTest.root')
f = R.TFile.Open('roots/RefPointTest.root')

for fs in ('2Mu2J', '4Mu'):
    for sp in SIGNALPOINTS:
#for fs in ('2Mu2J',):
#    for sp in ((125, 20, 1300),):
        for quantity, names, legends, lpos, movement in config:
            ResString = 'Res' if quantity not in ('deltaR', 'deltaphi', 'deltaEta') else ''
            h1 = f.Get('{}{}{}_HTo2XTo{}_{}'.format(quantity, ResString, names[0], fs, SPStr(sp)))
            h2 = f.Get('{}{}{}_HTo2XTo{}_{}'.format(quantity, ResString, names[1], fs, SPStr(sp)))

            p1 = Plotter.Plot(h1, legends[0], 'l', 'hist')
            p2 = Plotter.Plot(h2, legends[1], 'l', 'hist')

            canvas = Plotter.Canvas(lumi='{} ({} GeV, {} GeV, {} GeV)'.format(fs, *sp))
            canvas.addMainPlot(p1)
            canvas.addMainPlot(p2)

            canvas.makeLegend(pos=lpos)
            canvas.legend.resizeHeight()
            canvas.legend.moveLegend(X=movement)

            p1.SetLineColor(R.kRed)
            p2.SetLineColor(R.kBlue)

            canvas.setMaximum()

            canvas.cleanup('{}{}_Compare_HTo2XTo{}_{}.pdf'.format(quantity, ResString, fs, SPStr(sp)))

if False:
    fs, sp = '2Mu2J', (125, 20, 1300)
    h = f.Get('deltaDeltaR_HTo2XTo{}_{}'.format(fs, SPStr(sp)))
    p = Plotter.Plot(h, '', 'l', 'hist')

    canvas = Plotter.Canvas(lumi='{} ({} GeV, {} GeV, {} GeV)'.format(fs, *sp))
    canvas.addMainPlot(p)
    p.SetLineColor(R.kBlue)
    canvas.setMaximum()
    canvas.cleanup('deltaDeltaR_HTo2XTo{}_{}.pdf'.format(fs, SPStr(sp)))
