import ROOT as R
import DisplacedDimuons.Histogrammer.Plotter as Plotter
import DisplacedDimuons.Histogrammer.Primitives as Primitives
from DisplacedDimuons.Histogrammer.Constants import DIR_DD, DIR_WS, SIGNALS

#### CLASS AND FUNCTION DEFINITIONS ####
# this works for a tuple OR 3 arguments
def SPStr(*args):
	if len(args) == 3:
		return '{}_{}_{}'.format(*args)
	elif len(args) == 1:
		return '{}_{}_{}'.format(*args[0])

# opens file, gets tree, fills histograms, closes file
def fillPlots(sp):
	# get file and tree
	f = R.TFile.Open(DIR_WS + 'simple_ntuple_{}.root'.format(SPStr(sp)))
	t = f.Get('SimpleNTupler/DDTree')

	# declare histogram
	HISTS[sp]['pTRes'] = R.TH1F('pTRes_{}'.format(SPStr(sp)), ';(DSA p_{T} #minus gen p_{T})/gen p_{T};Counts', 100, -5., 5.)
	HISTS[sp]['pTRes'].SetDirectory(0)

	# loop over tree
	Primitives.SelectBranches(t, BRANCHKEYS)
	for i, event in enumerate(t):

		#if i == 1000: break

		E = Primitives.ETree(t, BRANCHKEYS)
		mu11, mu12, mu21, mu22, X1, X2, H, P = E.getPrimitives('GEN')
		DSAmuons = E.getPrimitives('DSAMUON')

		def findClosestMuon(muon, muons):
			closestDeltaR = float('inf')
			closestMuon = None
			for mu in muons:
				thisDeltaR = muon.p4.DeltaR(mu.p4)
				if thisDeltaR < 0.3 and thisDeltaR < closestDeltaR:
					closestDeltaR = thisDeltaR
					closestMuon = mu
			return closestMuon

		notFound = False
		# fill histogram
		for genMuon in (mu11, mu12, mu21, mu22):
			closestDSAMuon = findClosestMuon(genMuon, DSAmuons)
			if closestDSAMuon is not None:
				HISTS[sp]['pTRes'].Fill((closestDSAMuon.pt - genMuon.pt)/genMuon.pt)
			else:
				notFound = True
				COUNTERS[sp]['muons'] += 1
		if notFound:
			COUNTERS[sp]['events'] += 1


	print '{} : {} gen muons across {} events (out of {}) with no closest DSA muon'.format(
		SPStr(sp),
		COUNTERS[sp]['muons'],
		COUNTERS[sp]['events'],
		t.GetEntries(),
	)
	
	# cleanup
	del t
	f.Close()
	del f

# makes plot using Plotter class
def makePlots(sp):
	h = HISTS[sp]['pTRes']

	p = Plotter.Plot(h, '', 'p', 'hist')
	canvas = Plotter.Canvas()
	canvas.addMainPlot(p)
	p.SetLineColor(R.kBlue)
	canvas.drawText('#mu = {:.4f}'   .format(h.GetMean())  , (.7, .8    ))
	canvas.drawText('#sigma = {:.4f}'.format(h.GetStdDev()), (.7, .8-.04))
	canvas.makeTransparent()
	canvas.finishCanvas()
	canvas.save('pdfs/{}_{}.pdf'.format('pTRes', SPStr(sp)))
	canvas.deleteCanvas()

#### ALL GLOBAL VARIABLES DECLARED HERE ####
HISTS = {}
COUNTERS = {}
BRANCHKEYS = ('GEN', 'DSAMUON')

#SIGNALPOINTS = [
#	(1000,  20,    2),
#	(1000,  20,   20),
#	(1000,  20,  200),
#	( 400, 150,   40),
#	( 400, 150,  400),
#	( 400, 150, 4000),
#	( 400,  20,    4),
#	( 400,  20,   40),
#	( 400,  20,  400),
#	( 125,  50,   50),
#	( 125,  50,  500),
#	( 125,  50, 5000),
#	( 125,  20,   13),
#	( 125,  20,  130),
#	( 125,  20, 1300),
#]

import sys
SIGNALPOINTS = [(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))]

#### MAIN CODE ####
# loop over signal points
# uncomment these when all signal points are ready
#for mH in SIGNALS:
#	for mX in SIGNALS[mH]:
#		for cTau in SIGNALS[mH][mX]:
#			sp = (mH, mX, cTau)

for sp in SIGNALPOINTS:
	HISTS[sp] = {}
	COUNTERS[sp] = {'events':0, 'muons':0}

	print 'Starting', SPStr(sp)
	fillPlots(sp)
	makePlots(sp)
