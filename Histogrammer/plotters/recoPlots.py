import ROOT as R
import DisplacedDimuons.Histogrammer.Plotter as Plotter
import DisplacedDimuons.Histogrammer.Primitives as Primitives
from DisplacedDimuons.Histogrammer.Constants import DIR_DD, DIR_WS, SIGNALS
import argparse

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
	HISTS[sp]['pTRes' ] = R.TH1F('pTRes_{}' .format(SPStr(sp)), ';(DSA p_{T} #minus gen p_{T})/gen p_{T};Counts', 100 , -5., 5.    )
	HISTS[sp]['pTEff' ] = R.TH1F('pTEff_{}' .format(SPStr(sp)), ';p_{T} [GeV];DSA Match Efficiency'             , 1000, 0. , 500.  )
	HISTS[sp]['pTDen' ] = R.TH1F('pTDen_{}' .format(SPStr(sp)), ''                                              , 1000, 0. , 500.  )
	HISTS[sp]['LxyEff'] = R.TH1F('LxyEff_{}'.format(SPStr(sp)), ';L_{xy} [cm];DSA Match Efficiency'             , 1000, 0. , 1500. )
	HISTS[sp]['LxyDen'] = R.TH1F('LxyDen_{}'.format(SPStr(sp)), ''                                              , 1000, 0. , 1500. )

	HISTS[sp]['pTRes' ].SetDirectory(0)
	HISTS[sp]['pTEff' ].SetDirectory(0)
	HISTS[sp]['pTDen' ].SetDirectory(0)
	HISTS[sp]['LxyEff'].SetDirectory(0)
	HISTS[sp]['LxyDen'].SetDirectory(0)

	nMuons = 0
	nDouble = 0

	# loop over tree
	Primitives.SelectBranches(t, BRANCHKEYS)
	for i, event in enumerate(t):

		if args.DEVELOP:
			if i == 1000: break

		E = Primitives.ETree(t, BRANCHKEYS)
		mu11, mu12, mu21, mu22, X1, X2, H, P = E.getPrimitives('GEN')
		DSAmuons = E.getPrimitives('DSAMUON')

		def findClosestMuon(muon, muons):
			closestDeltaR = float('inf')
			closestMuon = None
			closestMuonIndex = None
			for i, mu in enumerate(muons):
				thisDeltaR = muon.p4.DeltaR(mu.p4)
				if thisDeltaR < 0.3 and thisDeltaR < closestDeltaR:
					closestDeltaR = thisDeltaR
					closestMuon = mu
					closestMuonIndex = i
			return closestMuonIndex, closestMuon

		def getLxy(muon, X):
			return ((muon.x-X.x)**2. + (muon.y-X.y)**2.)**0.5

		alreadyFound = []

		# fill histogram
		for i, genMuon in enumerate((mu11, mu12, mu21, mu22)):
			nMuons += 1
			Lxy = getLxy(genMuon, X1 if i < 2 else X2)
			HISTS[sp]['LxyDen'].Fill(Lxy)
			HISTS[sp]['pTDen' ].Fill(genMuon.pt)
			closestDSAMuonIndex, closestDSAMuon = findClosestMuon(genMuon, DSAmuons)
			if closestDSAMuonIndex is not None:
				if closestDSAMuonIndex in alreadyFound:
					nDouble += 1
				alreadyFound.append(closestDSAMuonIndex)
			if closestDSAMuon is not None:
				HISTS[sp]['pTRes' ].Fill((closestDSAMuon.pt - genMuon.pt)/genMuon.pt)
				HISTS[sp]['LxyEff'].Fill(Lxy)
				HISTS[sp]['pTEff' ].Fill(genMuon.pt)

	print '{} {} {} :'.format(*sp), nDouble, 'multiple matches out of', nMuons, 'muons'

	# cleanup
	del t
	f.Close()
	del f

# makes plot using Plotter class
def makePlots(sp):
	h = HISTS[sp]['pTRes']
	p = Plotter.Plot(h, 'H#rightarrow2X#rightarrow4#mu MC', 'l', 'hist')
	fname = 'pdfs/{}_{}.pdf'.format('pTRes', SPStr(sp)) if not args.DEVELOP else 'test.pdf'

	func = R.TF1('f1', 'gaus', -0.4, 0.4)
	h.Fit('f1')
	f = Plotter.Plot(func, 'Gaussian fit', 'l', '')

	canvas = Plotter.Canvas(lumi='({}, {}, {})'.format(*sp))
	canvas.addMainPlot(p)
	canvas.addMainPlot(f)
	canvas.makeLegend(lWidth=.25)
	canvas.legend.moveLegend(Y=-.3)
	canvas.legend.resizeHeight()
	p.SetLineColor(R.kBlue)
	f.SetLineColor(R.kRed)
	p.FindObject('stats').SetTextColor(R.kRed)
	canvas.drawText('#color[4]{' + '#bar{{x}} = {:.4f}'   .format(h.GetMean())   + '}', (.7, .8    ))
	canvas.drawText('#color[4]{' + 's = {:.4f}'           .format(h.GetStdDev()) + '}', (.7, .8-.04))
	canvas.setFitBoxStyle(h, lWidth=0.35, pos='tl')
	canvas.makeTransparent()
	canvas.finishCanvas()
	canvas.save(fname)
	canvas.deleteCanvas()

# write histograms
def writeHistograms(sp):
	fname = 'roots/ResEffPlots_{}.root'.format(SPStr(sp)) if not args.DEVELOP else 'test.root'
	f = R.TFile.Open(fname, 'RECREATE')

	for key in HISTS[sp]:
		HISTS[sp][key].Write()

	f.Close()

#### ALL GLOBAL VARIABLES DECLARED HERE ####

parser = argparse.ArgumentParser()
parser.add_argument('--signalpoints', dest='SIGNALPOINT', type=int, nargs=3  , help='the mH mX cTau tuple'         )
parser.add_argument('--develop'     , dest='DEVELOP'    , action='store_true', help='run test mode for 1000 events')
parser.add_argument('--fromfile'    , dest='FROMFILE'   , action='store_true', help='whether to rerun over trees'  )
args = parser.parse_args()

HISTS = {}
BRANCHKEYS = ('GEN', 'DSAMUON')

if not args.SIGNALPOINT:
	SIGNALPOINTS = [(125, 20, 13)]
else:
	SIGNALPOINTS = [(args.SIGNALPOINT[0], args.SIGNALPOINT[1], args.SIGNALPOINT[2])]

#### MAIN CODE ####
# loop over signal points
# uncomment these when all signal points are ready
#for mH in SIGNALS:
#	for mX in SIGNALS[mH]:
#		for cTau in SIGNALS[mH][mX]:
#			sp = (mH, mX, cTau)

if not args.FROMFILE:
	for sp in SIGNALPOINTS:
		HISTS[sp] = {}

		fillPlots(sp)
		makePlots(sp)

	writeHistograms(sp)
else:
	f = R.TFile.Open('roots/ResEffPlots.root')

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

	for sp in SIGNALPOINTS:
		HISTS[sp] = {}
		for key in ('pTRes', 'pTEff', 'pTDen', 'LxyEff', 'LxyDen'):
			HISTS[sp][key] = f.Get(key + '_' + SPStr(sp))

		makePlots(sp)
