import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
from DisplacedDimuons.Analysis.Constants import DIR_DD, DIR_WS, SIGNALS, RECOSIGNALPOINTS
from DisplacedDimuons.Analysis.Utilities import SPStr

# get all histograms
HISTS = {}
f = R.TFile.Open('../analyzers/roots/RecoPlots.root')
for hkey in [tkey.GetName() for tkey in f.GetListOfKeys()]:
	parts = hkey.split('_')
	sp = tuple(map(int, parts[-3:]))
	key = '_'.join(parts[:-3])
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
	KEYS = (
#		'DSA_pTRes',
#		'DSA_d0Dif',
#		'DSA_nMuon',
#		'RSA_pTRes',
#		'RSA_d0Dif',
#		'RSA_nMuon',
		'Dim_vtxChi2',
		'Dim_deltaR',
		'Dim_mass',
		'Dim_deltaPhi',
		'Dim_cosAlpha',
	)

	for sp in RECOSIGNALPOINTS:
		for key in KEYS:
			DOFIT = 'pTRes' in key
			h = HISTS[sp][key]
			p = Plotter.Plot(h, 'H#rightarrow2X#rightarrow4#mu MC', 'l', 'hist')
			fname = 'pdfs/{}_{}.pdf'.format(key, SPStr(sp))

			if DOFIT:
				func = R.TF1('f1', 'gaus', -0.5, 0.4)
				h.Fit('f1')
				f = Plotter.Plot(func, 'Gaussian fit', 'l', '')

			canvas = Plotter.Canvas(lumi='({}, {}, {})'.format(*sp))
			canvas.addMainPlot(p)
			if DOFIT:
				canvas.addMainPlot(f)
			canvas.makeLegend(lWidth=.25, pos='tr')
			canvas.legend.moveLegend(Y=-.3)
			canvas.legend.resizeHeight()
			p.SetLineColor(R.kBlue)
			canvas.drawText('#color[4]{' + '#bar{{x}} = {:.4f}'   .format(h.GetMean())   + '}', (.7, .8    ))
			canvas.drawText('#color[4]{' + 's = {:.4f}'           .format(h.GetStdDev()) + '}', (.7, .8-.04))
			if DOFIT:
				f.SetLineColor(R.kRed)
				canvas.setFitBoxStyle(h, lWidth=0.35, pos='tr')
				p.FindObject('stats').SetTextColor(R.kRed)
				Plotter.MOVE_OBJECT(p.FindObject('stats'), Y=-.5, NDC=True)
			Cleanup(canvas, fname)

# make DSA RSA overlaid per signal plots
def makeOverlayPerSignalPlots():
	KEYS = (
		'pTRes',
		'd0Dif',
		'nMuon',
	)
	for sp in RECOSIGNALPOINTS:
		for key in KEYS:
			DOFIT = key == 'pTRes'
			h = {}
			h['DSA'] = HISTS[sp]['DSA_'+key]
			h['RSA'] = HISTS[sp]['RSA_'+key]
			p = {}
			for rtype in h:
				p[rtype] = Plotter.Plot(h[rtype], 'H#rightarrow2X#rightarrow4#mu MC ({})'.format(rtype), 'l', 'hist')
			fname = 'pdfs/{}_{}.pdf'.format('Reco_'+key, SPStr(sp))

			if DOFIT:
				funcs = {}
				fplots = {}
				for rtype in h:
					funcs[rtype] = R.TF1('f'+rtype, 'gaus', -0.5, 0.4)
					h[rtype].Fit('f'+rtype)
					fplots[rtype] = Plotter.Plot(funcs[rtype], 'Gaussian fit ({})'.format(rtype), 'l', '')

			canvas = Plotter.Canvas(lumi='({}, {}, {})'.format(*sp))
			canvas.addMainPlot(p['DSA'])
			canvas.addMainPlot(p['RSA'], addS=True)

			canvas.firstPlot.setTitles(X=canvas.firstPlot.GetXaxis().GetTitle().replace('DSA','Reco'))

			if DOFIT:
				canvas.addMainPlot(fplots['DSA'])
				canvas.addMainPlot(fplots['RSA'])

			canvas.makeLegend(lWidth=.25, pos='tr' if key == 'pTRes' else 'tl')
			canvas.legend.moveLegend(X=-.3 if key == 'pTRes' else 0.)
			canvas.legend.resizeHeight()

			p['DSA'].SetLineColor(R.kBlue)
			p['RSA'].SetLineColor(R.kRed)

			canvas.drawText('#color[4]{' + '#bar{{x}} = {:.4f}'   .format(h['DSA'].GetMean())   + '}', (.75, .8    ))
			canvas.drawText('#color[4]{' + 's = {:.4f}'           .format(h['DSA'].GetStdDev()) + '}', (.75, .8-.04))
			canvas.drawText('#color[2]{' + '#bar{{x}} = {:.4f}'   .format(h['RSA'].GetMean())   + '}', (.75, .8-.08))
			canvas.drawText('#color[2]{' + 's = {:.4f}'           .format(h['RSA'].GetStdDev()) + '}', (.75, .8-.12))

			if key == 'nMuon':
				canvas.firstPlot.SetMaximum(1.05 * max(p['DSA'].GetMaximum(), p['RSA'].GetMaximum()))

			if DOFIT:
				fplots['DSA'].SetLineColor(R.kBlack)
				fplots['RSA'].SetLineColor(R.kGreen+1)

				canvas.setFitBoxStyle(h['DSA'], lWidth=0.35, pos='tr')
				canvas.setFitBoxStyle(h['RSA'], lWidth=0.35, pos='tr')

				p['DSA'].FindObject('stats').SetTextColor(R.kBlack)
				Plotter.MOVE_OBJECT(p['DSA'].FindObject('stats'), Y=-.25, NDC=True)

				p['RSA'].FindObject('stats').SetTextColor(R.kGreen+1)
				Plotter.MOVE_OBJECT(p['RSA'].FindObject('stats'), Y=-.5, NDC=True)

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
		g = R.TGraphAsymmErrors(h, hDen, 'cp')
		g.SetNameTitle('g_'+key, ';'+h.GetXaxis().GetTitle()+';'+h.GetYaxis().GetTitle())
		p = Plotter.Plot(g, '', 'elp', 'pe')
	else:
		p = Plotter.Plot(h, '', 'p', 'hist p')

	canvas = Plotter.Canvas()
	canvas.addMainPlot(p)
	canvas.firstPlot.SetMinimum(0.)
	canvas.firstPlot.SetMaximum(1.)
	Cleanup(canvas, 'pdfs/{}.pdf'.format(key))

# make overlaid plots that combine all signal points
def makeOverlayGlobalPlots(key, DenKey=None):
	ExtraKey = 'ExtraPt' if key == 'pTEff' else 'ExtraLxy'
	for i, sp in enumerate(RECOSIGNALPOINTS):
		if i == 0:
			h = {}
			h['DSA'] = f.Get('{}_{}'.format('DSA_'+key, SPStr(sp)))
			h['RSA'] = f.Get('{}_{}'.format('RSA_'+key, SPStr(sp)))
			h['Ext'] = f.Get('{}_{}'.format(ExtraKey  , SPStr(sp)))

			h['DSA'].SetDirectory(0)
			h['RSA'].SetDirectory(0)
			h['Ext'].SetDirectory(0)

			if DenKey is not None:
				hDen = f.Get('{}_{}'.format(DenKey, SPStr(sp)))
				hDen.SetDirectory(0)
		else:
			h['DSA'].Add(f.Get('{}_{}'.format('DSA_'+key, SPStr(sp))))
			h['RSA'].Add(f.Get('{}_{}'.format('RSA_'+key, SPStr(sp))))
			h['Ext'].Add(f.Get('{}_{}'.format(ExtraKey  , SPStr(sp))))

			if DenKey is not None:
				hDen.Add(f.Get('{}_{}'.format(DenKey, SPStr(sp))))

	h['DSA'].Rebin(10)
	h['RSA'].Rebin(10)
	h['Ext'].Rebin(10)

	p = {}

	if DenKey is not None:
		hDen.Rebin(10)

		g = {}
		g['DSA'] = R.TGraphAsymmErrors(h['DSA'], hDen, 'cp')
		g['RSA'] = R.TGraphAsymmErrors(h['RSA'], hDen, 'cp')
		g['Ext'] = R.TGraphAsymmErrors(h['Ext'], hDen, 'cp')

		g['DSA'].SetNameTitle('g_DSA_'+key, ';'+h['DSA'].GetXaxis().GetTitle()+';'+'Reco Match Efficiency')#+h['DSA'].GetYaxis().GetTitle())
		g['RSA'].SetNameTitle('g_RSA_'+key, ';'+h['RSA'].GetXaxis().GetTitle()+';'+'Reco Match Efficiency')#+h['RSA'].GetYaxis().GetTitle())
		g['Ext'].SetNameTitle('g_Ext_'+key, ';'+h['Ext'].GetXaxis().GetTitle()+';'+'Reco Match Efficiency')#+h['Ext'].GetYaxis().GetTitle())

		p['DSA'] = Plotter.Plot(g['DSA'], 'DSA'  , 'elp', 'pe')
		p['RSA'] = Plotter.Plot(g['RSA'], 'RSA'  , 'elp', 'pe')
		p['Ext'] = Plotter.Plot(g['Ext'], 'Extra', 'elp', 'pe')
	else:
		p['DSA'] = Plotter.Plot(h['DSA'], 'DSA', 'lp', 'hist p')
		p['RSA'] = Plotter.Plot(h['RSA'], 'RSA', 'lp', 'hist p')

	canvas = Plotter.Canvas()
	canvas.addMainPlot(p['DSA'])
	canvas.addMainPlot(p['RSA'])
	canvas.addMainPlot(p['Ext'])
	p['DSA'].SetMarkerColor(R.kRed)
	p['RSA'].SetMarkerColor(R.kBlue)
	p['Ext'].SetMarkerColor(R.kMagenta)
	p['DSA'].SetLineColor(R.kRed)
	p['RSA'].SetLineColor(R.kBlue)
	p['Ext'].SetLineColor(R.kMagenta)

	canvas.makeLegend(pos='br' if key == 'pTEff' else 'tr')
	if key == 'pTEff':
		canvas.legend.moveLegend(Y=.1)
	canvas.firstPlot.SetMinimum(0.)
	canvas.firstPlot.SetMaximum(1.)
	Cleanup(canvas, 'pdfs/{}.pdf'.format('Reco_'+key))

# make 3D color plots
def makeColorPlot(key):
	for i, sp in enumerate(RECOSIGNALPOINTS):
		if i == 0:
			h = f.Get('{}_{}'.format(key, SPStr(sp)))
			h.SetDirectory(0)
		else:
			h.Add(f.Get('{}_{}'.format(key, SPStr(sp))))

	h.Rebin2D(10, 10)
	p = Plotter.Plot(h, '', '', 'colz')
	canvas = Plotter.Canvas()
	canvas.mainPad.SetLogz(True)
	canvas.addMainPlot(p)
	canvas.scaleMargins(1.75, edges='R')
	canvas.scaleMargins(0.8, edges='L')
	Cleanup(canvas, 'pdfs/{}.pdf'.format(key))

#makeGlobalPlot('DSA_LxyEff', DenKey='LxyDen')
#makeGlobalPlot('DSA_pTEff' , DenKey='pTDen' )
#makeGlobalPlot('RSA_LxyEff', DenKey='LxyDen')
#makeGlobalPlot('RSA_pTEff' , DenKey='pTDen' )

makePerSignalPlots()
makeOverlayPerSignalPlots()
makeOverlayGlobalPlots('LxyEff', DenKey='LxyDen')
makeOverlayGlobalPlots('pTEff' , DenKey='pTDen' )
makeColorPlot('DSA_pTResVSLxy')
makeColorPlot('DSA_pTResVSpT')
makeColorPlot('DSA_pTResVSdR')
makeColorPlot('DSA_pTVSpT')
