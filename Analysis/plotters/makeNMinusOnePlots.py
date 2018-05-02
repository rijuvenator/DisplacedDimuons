import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.Selections as Selections
from DisplacedDimuons.Common.Constants import RECOSIGNALPOINTS
from DisplacedDimuons.Common.Utilities import SPStr

# get all histograms
HISTS = {}
f = R.TFile.Open('../analyzers/roots/nMinusOne.root')
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

# make per signal plots
def makePerSignalPlots():
	for sp in RECOSIGNALPOINTS:
		for key in HISTS[sp]:
			h = HISTS[sp][key]
			p = Plotter.Plot(h, 'H#rightarrow2X#rightarrow4#mu MC', 'l', 'hist')
			fname = 'pdfs/NM1_{}_{}.pdf'.format(key, SPStr(sp))
			canvas = Plotter.Canvas(lumi='({}, {}, {})'.format(*sp))
			canvas.lumi += ' : |#Delta#Phi| ' + ('<' if '_Less' in key else '>') + ' #pi/2'
			canvas.addMainPlot(p)
			canvas.makeLegend(lWidth=.25, pos='tr')
			canvas.legend.moveLegend(Y=-.3)
			canvas.legend.resizeHeight()
			p.SetLineColor(R.kBlue)

			cutKey = key.replace('_Less','').replace('_More','')
			try:
				cutVal = Selections.MuonCuts[cutKey].val
			except:
				cutVal = Selections.DimuonCuts[cutKey].val

			l = R.TLine(cutVal, p.GetMinimum(), cutVal, p.GetMaximum()*1.05)
			l.SetLineStyle(2)
			l.SetLineWidth(2)
			l.Draw()

			Cleanup(canvas, fname)
makePerSignalPlots()
