import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
from DisplacedDimuons.Analysis.Constants import DIR_DD, DIR_WS, SIGNALS, RECOSIGNALPOINTS
from DisplacedDimuons.Analysis.Utilities import SPStr

# get all histograms
HISTS = {}
f = R.TFile.Open('roots/RecoPlots.root')
for hkey in [tkey.GetName() for tkey in f.GetListOfKeys()]:
	parts = hkey.split('_')
	sp = tuple(map(int, parts[-3:]))
	key = parts[0] + '_' + parts[1] # this is peculiar to my DSA RSA naming convention
	if sp not in HISTS:
		HISTS[sp] = {}
	HISTS[sp][key] = f.Get(hkey)

# end of plot function boilerplate
def Cleanup(canvas, filename):
	canvas.finishCanvas()
	canvas.save(filename)
	canvas.deleteCanvas()

# make plots that are per signal point
def makePerSignalPlots():
	CONFIG = {
		'DSA_pTRes' : {'DOFIT' :  True},
		'DSA_d0Dif' : {'DOFIT' : False},
		'DSA_nMuon' : {'DOFIT' : False},
		'RSA_pTRes' : {'DOFIT' :  True},
		'RSA_d0Dif' : {'DOFIT' : False},
		'RSA_nMuon' : {'DOFIT' : False},
	}
	for sp in RECOSIGNALPOINTS:
		for key in CONFIG:
			h = HISTS[sp][key]
			p = Plotter.Plot(h, 'H#rightarrow2X#rightarrow4#mu MC', 'l', 'hist')
			fname = 'pdfs/{}_{}.pdf'.format(key, SPStr(sp))

			if CONFIG[key]['DOFIT']:
				func = R.TF1('f1', 'gaus', -0.5, 0.4)
				h.Fit('f1')
				f = Plotter.Plot(func, 'Gaussian fit', 'l', '')

			canvas = Plotter.Canvas(lumi='({}, {}, {})'.format(*sp))
			canvas.addMainPlot(p)
			if CONFIG[key]['DOFIT']:
				canvas.addMainPlot(f)
			canvas.makeLegend(lWidth=.25, pos='tr')
			canvas.legend.moveLegend(Y=-.3)
			canvas.legend.resizeHeight()
			p.SetLineColor(R.kBlue)
			canvas.drawText('#color[4]{' + '#bar{{x}} = {:.4f}'   .format(h.GetMean())   + '}', (.7, .8    ))
			canvas.drawText('#color[4]{' + 's = {:.4f}'           .format(h.GetStdDev()) + '}', (.7, .8-.04))
			if CONFIG[key]['DOFIT']:
				f.SetLineColor(R.kRed)
				canvas.setFitBoxStyle(h, lWidth=0.35, pos='tr')
				p.FindObject('stats').SetTextColor(R.kRed)
				p.FindObject('stats').SetY1NDC(p.FindObject('stats').GetY1NDC() - .5)
				p.FindObject('stats').SetY2NDC(p.FindObject('stats').GetY2NDC() - .5)
			canvas.makeTransparent()
			Cleanup(canvas, fname)

# make plots that combine all signal points
def makeGlobalPlot(key, DenKey=None):
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

	h.Rebin(10)
	if DenKey is not None:
		hDen.Rebin(10)
		h.Divide(hDen)

	p = Plotter.Plot(h, '', 'p', 'hist p')
	canvas = Plotter.Canvas()
	canvas.addMainPlot(p)
	Cleanup(canvas, 'pdfs/{}.pdf'.format(key))

# make 3D color plots
def makeColorPlot(key):
	for i, sp in enumerate(RECOSIGNALPOINTS):
		if i == 0:
			h = f.Get('{}_{}'.format(key, SPStr(sp)))
			h.SetDirectory(0)
		else:
			h.Add(f.Get('{}_{}'.format(key, SPStr(sp))))

	p = Plotter.Plot(h, '', '', 'colz')
	canvas = Plotter.Canvas()
	canvas.addMainPlot(p)
	canvas.scaleMargins(1.75, edges='R')
	canvas.scaleMargins(0.75, edges='L')
	Cleanup(canvas, 'pdfs/{}.pdf'.format(key))

makePerSignalPlots()
makeGlobalPlot('DSA_LxyEff', DenKey='LxyDen')
makeGlobalPlot('DSA_pTEff' , DenKey='pTDen' )
makeGlobalPlot('RSA_LxyEff', DenKey='LxyDen')
makeGlobalPlot('RSA_pTEff' , DenKey='pTDen' )
