import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.Primitives as Primitives
import DisplacedDimuons.Analysis.RootTools as RT
import DisplacedDimuons.Analysis.Selections as Selections
from DisplacedDimuons.Analysis.Constants import DIR_DD, DIR_WS, SIGNALS, RECOSIGNALPOINTS
from DisplacedDimuons.Analysis.Utilities import SPStr
import argparse

#### CLASS AND FUNCTION DEFINITIONS ####
# opens file, gets tree, fills histograms, closes file
def fillPlots(sp):
	# get file and tree
	f = R.TFile.Open(DIR_WS + 'simple_ntuple_{}.root'.format(SPStr(sp)))
	t = f.Get('SimpleNTupler/DDTree')

	# declare histogram
	HISTS[sp]['DSA_pTRes' ] = R.TH1F('DSA_pTRes_{}' .format(SPStr(sp)), ';(DSA p_{T} #minus gen p_{T})/gen p_{T};Counts', 1000, -1. , 3.   )
	HISTS[sp]['DSA_pTEff' ] = R.TH1F('DSA_pTEff_{}' .format(SPStr(sp)), ';p_{T} [GeV];DSA Match Efficiency'             , 1000, 0.  , 500. )
	HISTS[sp]['DSA_LxyEff'] = R.TH1F('DSA_LxyEff_{}'.format(SPStr(sp)), ';L_{xy} [cm];DSA Match Efficiency'             , 1000, 0.  , 1500.)
	HISTS[sp]['DSA_d0Dif' ] = R.TH1F('DSA_d0Dif_{}' .format(SPStr(sp)), ';DSA d_{0} #minus gen d_{0};Counts'            , 1000, -10., 10.  )
	HISTS[sp]['DSA_nMuon' ] = R.TH1F('DSA_nMuon_{}' .format(SPStr(sp)), ';DSA Muon Multiplicity;Counts'                 , 11  , 0.  , 11.  )

	HISTS[sp]['RSA_pTRes' ] = R.TH1F('RSA_pTRes_{}' .format(SPStr(sp)), ';(RSA p_{T} #minus gen p_{T})/gen p_{T};Counts', 1000, -1. , 3.   )
	HISTS[sp]['RSA_pTEff' ] = R.TH1F('RSA_pTEff_{}' .format(SPStr(sp)), ';p_{T} [GeV];RSA Match Efficiency'             , 1000, 0.  , 500. )
	HISTS[sp]['RSA_LxyEff'] = R.TH1F('RSA_LxyEff_{}'.format(SPStr(sp)), ';L_{xy} [cm];RSA Match Efficiency'             , 1000, 0.  , 1500.)
	HISTS[sp]['RSA_d0Dif' ] = R.TH1F('RSA_d0Dif_{}' .format(SPStr(sp)), ';RSA d_{0} #minus gen d_{0};Counts'            , 1000, -10., 10.  )
	HISTS[sp]['RSA_nMuon' ] = R.TH1F('RSA_nMuon_{}' .format(SPStr(sp)), ';RSA Muon Multiplicity;Counts'                 , 11  , 0.  , 11.  )

	HISTS[sp]['pTDen'     ] = R.TH1F('pTDen_{}'     .format(SPStr(sp)), ''                                              , 1000, 0.  , 500. )
	HISTS[sp]['LxyDen'    ] = R.TH1F('LxyDen_{}'    .format(SPStr(sp)), ''                                              , 1000, 0.  , 1500.)


	# make any histograms that don't require a loop
	t.Draw('@dsamu_pt.size()>>DSA_nMuon_{}'.format(SPStr(sp)))
	t.Draw('@rsamu_pt.size()>>RSA_nMuon_{}'.format(SPStr(sp)))

	for key in HISTS[sp]:
		HISTS[sp][key].SetDirectory(0)

	nMuons = 0
	nDouble = 0

	# loop over tree
	if DOLOOP:
		Primitives.SelectBranches(t, BRANCHKEYS)
		for i, event in enumerate(t):

			if args.DEVELOP:
				if i == 1000: break

			E = Primitives.ETree(t, BRANCHKEYS)
			mu11, mu12, mu21, mu22, X1, X2, H, P = E.getPrimitives('GEN')
			DSAmuons = E.getPrimitives('DSAMUON')
			RSAmuons = E.getPrimitives('RSAMUON')

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

			# see https://en.wikipedia.org/wiki/Skew_lines#Distance
			def getLineDistance(a, b, c, d):
				return abs((c-a).Dot(b.Cross(d).Unit()))

			alreadyFound = []

			# fill histogram
			for i, genMuon in enumerate((mu11, mu12, mu21, mu22)):
				# cut genMuons outside the detector acceptance
				if not (Selections.MuonCutList['pt'].apply(genMuon) and Selections.MuonCutList['eta'].apply(genMuon)): continue

				nMuons += 1
				X = X1 if i < 2 else X1
				Lxy = getLxy(genMuon, X)
				HISTS[sp]['LxyDen'].Fill(Lxy)
				HISTS[sp]['pTDen' ].Fill(genMuon.pt)

				closestDSAMuonIndex, closestDSAMuon = findClosestMuon(genMuon, DSAmuons)
				if closestDSAMuonIndex is not None:
					if False: #Lxy > 650:
						#genPos = RT.Vector3(genMuon       .pos.X()-X.x, genMuon       .pos.Y()-X.y, 0.)
						#genMom = RT.Vector3(genMuon       .p3 .X()    , genMuon       .p3 .Y()    , 0.)
						#DSAPos = RT.Vector3(closestDSAMuon.pos.X()    , closestDSAMuon.pos.Y()    , 0.)
						#DSAMom = RT.Vector3(closestDSAMuon.p3 .X()    , closestDSAMuon.p3 .Y()    , 0.)

						lineDistance = getLineDistance(genMuon.pos, genMuon.p3, closestDSAMuon.pos, closestDSAMuon.p3)
						nCols = 5
						print ('[DEBUG] ' + '{:8.2f} '*nCols + '\n' + '[DEBUG]          ' + '{:8.2f} '*(nCols) + '\n').format(
							Lxy,
							genMuon.pt,
							genMuon.eta,
							genMuon.phi,
							genMuon.d0,
							#genPos.Cross(genMom).Mag()/genMom.Mag(),
							closestDSAMuon.pt,
							closestDSAMuon.eta,
							closestDSAMuon.phi,
							closestDSAMuon.d0,
							#DSAPos.Cross(DSAMom).Mag()/DSAMom.Mag(),
							lineDistance
						)
					if closestDSAMuonIndex in alreadyFound:
						nDouble += 1
					alreadyFound.append(closestDSAMuonIndex)
				if closestDSAMuon is not None:
					HISTS[sp]['DSA_pTRes' ].Fill((closestDSAMuon.pt - genMuon.pt)/genMuon.pt)
					HISTS[sp]['DSA_d0Dif' ].Fill((closestDSAMuon.d0 - genMuon.d0))#/genMuon.d0)
					HISTS[sp]['DSA_LxyEff'].Fill(Lxy)
					HISTS[sp]['DSA_pTEff' ].Fill(genMuon.pt)

				closestRSAMuonIndex, closestRSAMuon = findClosestMuon(genMuon, RSAmuons)
				if closestRSAMuonIndex is not None:
					if closestRSAMuonIndex in alreadyFound:
						nDouble += 1
					alreadyFound.append(closestRSAMuonIndex)
				if closestRSAMuon is not None:
					HISTS[sp]['RSA_pTRes' ].Fill((closestRSAMuon.pt - genMuon.pt)/genMuon.pt)
					HISTS[sp]['RSA_d0Dif' ].Fill((closestRSAMuon.d0 - genMuon.d0))#/genMuon.d0)
					HISTS[sp]['RSA_LxyEff'].Fill(Lxy)
					HISTS[sp]['RSA_pTEff' ].Fill(genMuon.pt)

		print '{:5} {} {} : {} multiple matches out of {} muons'.format(sp[0], sp[1], sp[2], nDouble, nMuons)
	# cleanup
	del t
	f.Close()
	del f

# makes plot using Plotter class
def makePerSignalPlots(sp):
	CONFIG = {
		'DSA_pTRes' : {'DOFIT' :  True},
		'DSA_d0Dif' : {'DOFIT' : False},
		'DSA_nMuon' : {'DOFIT' : False},
		'RSA_pTRes' : {'DOFIT' :  True},
		'RSA_d0Dif' : {'DOFIT' : False},
		'RSA_nMuon' : {'DOFIT' : False},
	}
	for key in CONFIG:
		if key not in HLIST: continue
		h = HISTS[sp][key]
		p = Plotter.Plot(h, 'H#rightarrow2X#rightarrow4#mu MC', 'l', 'hist')
		fname = 'pdfs/{}_{}.pdf'.format(key, SPStr(sp)) if not args.DEVELOP else 'test_{}.pdf'.format(key)

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
		canvas.finishCanvas()
		canvas.save(fname)
		canvas.deleteCanvas()

# write histograms
def writeHistograms(sp):
	fname = 'roots/RecoPlots_{}.root'.format(SPStr(sp)) if not args.DEVELOP else 'test.root'
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
# name : requiresLoop
DEFAULT_HLIST = {
	'DSA_pTRes'  :True,
	'DSA_pTEff'  :True,
	'DSA_pTDen'  :True,
	'DSA_LxyEff' :True,
	'DSA_LxyDen' :True,
	'DSA_d0Dif'  :True,
	'DSA_nMuon'  :False,
	'RSA_pTRes'  :True,
	'RSA_pTEff'  :True,
	'RSA_pTDen'  :True,
	'RSA_LxyEff' :True,
	'RSA_LxyDen' :True,
	'RSA_d0Dif'  :True,
	'RSA_nMuon'  :False,
}
HLIST = DEFAULT_HLIST.keys()
DOLOOP = any([DEFAULT_HLIST[name] for name in HLIST])
BRANCHKEYS = ('GEN', 'DSAMUON', 'RSAMUON')

if not args.SIGNALPOINT:
	SIGNALPOINTS = [(125, 20, 13)]
else:
	SIGNALPOINTS = [tuple(args.SIGNALPOINT)]

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
		makePerSignalPlots(sp)

	writeHistograms(sp)
else:
	f = R.TFile.Open('roots/RecoPlots.root')

	for sp in RECOSIGNALPOINTS:
		HISTS[sp] = {}
		for key in HLIST:
			HISTS[sp][key] = f.Get(key + '_' + SPStr(sp))

		makePerSignalPlots(sp)
