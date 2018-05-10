import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.Selections as Selections
from DisplacedDimuons.Common.Utilities import SPStr
from DisplacedDimuons.Common.Constants import RECOSIGNALPOINTS
import re

MuonCutListPlusNone = Selections.CutLists['MuonCutListPlusNone']
data = []
headers = ('mH', 'mX', 'cTau') + MuonCutListPlusNone

f = open('../dumpers/cutTable.txt')
for line in f:
	if not re.match(r'MUO CUM: \d', line): continue
	cols = line.strip('\n').split()

	fields = {}
	for i,header in enumerate(headers):
		fields[header] = cols[i+2]
	data.append(fields)
f.close()

HISTS = {}
for fields in data:
	sp = (int(fields['mH']), int(fields['mX']), int(fields['cTau']))
	HISTS[sp] = R.TH1F('CutTable_HTo2XTo4Mu_{}'.format(SPStr(sp)), ';Cuts;Efficiency', len(MuonCutListPlusNone), 0, len(MuonCutListPlusNone))

	for i,header in enumerate(MuonCutListPlusNone):
		HISTS[sp].SetBinContent(i+1, float(fields[header]))
		HISTS[sp].GetXaxis().SetBinLabel(i+1, Selections.PrettyTitles[header])

f = R.TFile('../analyzers/roots/CutTable.root', 'RECREATE')
for sp in HISTS:
	HISTS[sp].Write()

COLORS = {
	(1000,  20,    2) : R.kRed,
	(1000,  20,   20) : R.kRed+1,
	(1000,  20,  200) : R.kRed+2,
	( 400, 150,   40) : R.kBlue,
	( 400, 150,  400) : R.kBlue+1,
	( 400, 150, 4000) : R.kBlue+2,
	( 400,  20,    4) : R.kMagenta,
	( 400,  20,   40) : R.kMagenta+1,
	( 400,  20,  400) : R.kMagenta+2,
	( 125,  50,   50) : R.kGreen,
	( 125,  50,  500) : R.kGreen+1,
	( 125,  50, 5000) : R.kGreen+2,
	( 125,  20,   13) : R.kOrange,
	( 125,  20,  130) : R.kOrange+1,
	( 125,  20, 1300) : R.kOrange+2,
}

PLOTS = {}
for sp in HISTS:
	PLOTS[sp] = Plotter.Plot(HISTS[sp], legName='({}, {}, {})'.format(*sp), legType='lp', option='hist p')

def makeCombinedPlot():
	canvas = Plotter.Canvas(lumi='CutTable Plot', cWidth=1000)
	for sp in RECOSIGNALPOINTS:
		canvas.addMainPlot(PLOTS[sp])
		PLOTS[sp].SetMarkerColor(COLORS[sp])
		PLOTS[sp].SetLineColor(COLORS[sp])

	canvas.firstPlot.SetMaximum(1.)
	canvas.firstPlot.SetMinimum(0.)
	canvas.scaleMargins(3.5, 'R')

	canvas.makeLegend()
	canvas.legend.resizeHeight(scale=.8)
	canvas.legend.moveLegend(X=.18)

	canvas.finishCanvas()
	canvas.save('CutTable.pdf')
	canvas.deleteCanvas()

def makeIndividualPlots():
	for sp in RECOSIGNALPOINTS:
		canvas = Plotter.Canvas(lumi='({}, {}, {})'.format(*sp))
		canvas.addMainPlot(PLOTS[sp])
		canvas.firstPlot.SetMaximum(1.)
		canvas.firstPlot.SetMinimum(0.)
		canvas.firstPlot.SetMarkerColor(R.kBlue)
		canvas.firstPlot.SetLineColor(R.kBlue)
		canvas.finishCanvas()
		canvas.save('pdfs/CutTable_HTo2XTo4Mu_{}.pdf'.format(SPStr(sp)))
		canvas.deleteCanvas()

makeIndividualPlots()
makeCombinedPlot()
