import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
from DisplacedDimuons.Common.Utilities import SPStr

# get all histograms
HISTS = {}
f = R.TFile.Open('../analyzers/roots/GenPlots.root')
for hkey in [tkey.GetName() for tkey in f.GetListOfKeys()]:
	parts = hkey.split('_')
	sp = tuple(map(int, parts[-3:]))
	key = '_'.join(parts[:-3])
	if sp not in HISTS:
		HISTS[sp] = {}
	HISTS[sp][key] = f.Get(hkey)

# make plots using Plotter class per signal point
def makePerSignalPlots():
	for sp in SIGNALPOINTS:
		for key in HISTS[sp]:
			h = HISTS[sp][key]
			p = Plotter.Plot(h, '', 'p', 'hist')
			canvas = Plotter.Canvas(lumi='({}, {}, {})'.format(*sp))
			canvas.addMainPlot(p)
			p.SetLineColor(R.kBlue)
			canvas.drawText('#color[4]{' + '#bar{{x}} = {:.4f}'   .format(h.GetMean())   + '}', (.7, .8    ))
			canvas.drawText('#color[4]{' + 's = {:.4f}'           .format(h.GetStdDev()) + '}', (.7, .8-.04))
			canvas.cleanup('pdfs/Gen_{}_HTo2XTo4Mu_{}.pdf'.format(key, SPStr(sp)))

makePerSignalPlots()
