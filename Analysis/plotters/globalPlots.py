import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
from DisplacedDimuons.Analysis.Constants import DIR_DD, DIR_WS, SIGNALS, RECOSIGNALPOINTS
from DisplacedDimuons.Analysis.Utilities import SPStr

def Cleanup(canvas, filename):
	canvas.finishCanvas()
	canvas.save(filename)
	canvas.deleteCanvas()

def MakePlot(key, DenKey=None):
	f = R.TFile.Open('roots/RecoPlots.root')
	for i, sp in enumerate(RECOSIGNALPOINTS):
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
	for i, sp in enumerate(RECOSIGNALPOINTS):
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


MakePlot('DSA_LxyEff', DenKey='LxyDen')
MakePlot('DSA_pTEff' , DenKey='pTDen' )
MakePlot('RSA_LxyEff', DenKey='LxyDen')
MakePlot('RSA_pTEff' , DenKey='pTDen' )
