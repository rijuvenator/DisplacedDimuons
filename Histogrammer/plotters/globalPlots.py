import ROOT as R
import DisplacedDimuons.Histogrammer.Plotter as Plotter
from DisplacedDimuons.Histogrammer.Constants import DIR_DD, DIR_WS, SIGNALS
from DisplacedDimuons.Histogrammer.Utilities import SPStr

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

# make Efficiency Plot
def makeEffPlot(key):
	f = R.TFile.Open('roots/ResEffPlots.root')
	for i, sp in enumerate(SIGNALPOINTS):
		if i == 0:
			hEff = f.Get('{}Eff_{}'.format(key, SPStr(sp)))
			hDen = f.Get('{}Den_{}'.format(key, SPStr(sp)))
			hEff.SetDirectory(0)
			hDen.SetDirectory(0)
		else:
			hEff.Add(f.Get('{}Eff_{}'.format(key, SPStr(sp))))
			hDen.Add(f.Get('{}Den_{}'.format(key, SPStr(sp))))
	f.Close()

	hEff.Rebin(10)
	hDen.Rebin(10)
	hEff.Divide(hDen)

	p = Plotter.Plot(hEff, '', 'p', 'hist p')
	canvas = Plotter.Canvas()
	canvas.addMainPlot(p)
	canvas.makeTransparent()
	canvas.finishCanvas()
	canvas.save('pdfs/{}Eff.pdf'.format(key))
	canvas.deleteCanvas()

def makeColorPlot(key):
	f = R.TFile.Open('roots/ResEffPlots.root')
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
	canvas.makeTransparent()
	canvas.finishCanvas()
	canvas.save('pdfs/{}.pdf'.format(key))
	canvas.deleteCanvas()


makeEffPlot('Lxy')
makeEffPlot('pT')
