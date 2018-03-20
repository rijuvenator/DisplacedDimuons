import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
from DisplacedDimuons.Analysis.Constants import DIR_DD, DIR_WS, SIGNALS
from DisplacedDimuons.Analysis.Utilities import SPStr

SIGNALPOINTS = [
	(1000,  20,    2),
	(1000,  20,   20),
	(1000,  20,  200),
	( 400, 150,   40),
	( 400, 150,  400),
	( 400, 150, 4000),
	( 400,  20,    4),
	( 400,  20,   40),
	( 400,  20,  400),
	( 125,  50,   50),
	( 125,  50,  500),
	( 125,  50, 5000),
	( 125,  20,   13),
	( 125,  20,  130),
	( 125,  20, 1300),
]

def Cleanup(canvas, filename):
	canvas.finishCanvas()
	canvas.save(filename)
	canvas.deleteCanvas()

def MakePlot(key, DenKey=None):
	f = R.TFile.Open('roots/RecoPlots.root')
	for i, sp in enumerate(SIGNALPOINTS):
		if i == 0:
			h = f.Get('{}_{}'.format(key, SPStr(sp)))
			h.SetDirectory(0)
			if DenKey is not None:
				hDen = f.Get('{}_{}'.format(DenKey, SPStr(sp)))
				hDen.SetDirectory(0)
		else:
			h.Add(f.Get('{}_{}'.format(key, SPStr(sp))))
			if DenKey is not None:
				hDen.Add(f.Get('{}_{}'.format(DenKey, SPStr(sp))))
	f.Close()

	h.Rebin(10)
	if DenKey is not None:
		hDen.Rebin(10)
		h.Divide(hDen)

	p = Plotter.Plot(h, '', 'p', 'hist p')
	canvas = Plotter.Canvas()
	canvas.addMainPlot(p)
	Cleanup(canvas, 'pdfs/{}.pdf'.format(key))

def makeColorPlot(key):
	f = R.TFile.Open('roots/RecoPlots.root')
	for i, sp in enumerate(SIGNALPOINTS):
		if i == 0:
			h = f.Get('{}_{}'.format(key, SPStr(sp)))
			h.SetDirectory(0)
		else:
			h.Add(f.Get('{}_{}'.format(key, SPStr(sp))))
	f.Close()

	p = Plotter.Plot(h, '', '', 'colz')
	canvas = Plotter.Canvas()
	canvas.addMainPlot(p)
	canvas.scaleMargins(1.75, edges='R')
	canvas.scaleMargins(0.75, edges='L')
	Cleanup(canvas, 'pdfs/{}.pdf'.format(key))


MakePlot('LxyEff' , DenKey='LxyDen')
MakePlot('pTEff'  , DenKey='pTDen' )
MakePlot('nDSALxy', DenKey='LxyDen')
