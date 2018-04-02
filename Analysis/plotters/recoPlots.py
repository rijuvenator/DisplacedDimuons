import ROOT as R
import DisplacedDimuons.Analysis.Primitives as Primitives
import DisplacedDimuons.Analysis.Selections as Selections
from DisplacedDimuons.Analysis.Constants import DIR_DD, DIR_WS, SIGNALS, RECOSIGNALPOINTS
from DisplacedDimuons.Analysis.Utilities import SPStr
import argparse

R.gROOT.SetBatch(True)

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

	HISTS[sp]['ExtraLxy'  ] = R.TH1F('ExtraLxy_{}'  .format(SPStr(sp)), ';L_{xy} [cm];Efficiency'                       , 1000, 0.  , 1500.)
	HISTS[sp]['ExtraPt'   ] = R.TH1F('ExtraPt_{}'   .format(SPStr(sp)), ';p_{T} [GeV];Efficiency'                       , 1000, 0.  , 500. )

	HISTS[sp]['pTDen'     ] = R.TH1F('pTDen_{}'     .format(SPStr(sp)), ''                                              , 1000, 0.  , 500. )
	HISTS[sp]['LxyDen'    ] = R.TH1F('LxyDen_{}'    .format(SPStr(sp)), ''                                              , 1000, 0.  , 1500.)


	# make any histograms that don't require a loop
	t.Draw('@dsamu_pt.size()>>DSA_nMuon_{}'.format(SPStr(sp)))
	t.Draw('@rsamu_pt.size()>>RSA_nMuon_{}'.format(SPStr(sp)))

	for key in HISTS[sp]:
		HISTS[sp][key].SetDirectory(0)

	# loop over tree
	Primitives.SelectBranches(t, BRANCHKEYS)
	for i, event in enumerate(t):

		if args.DEVELOP:
			if i == 1000: break

		E = Primitives.ETree(t, BRANCHKEYS)
		mu11, mu12, mu21, mu22, X1, X2, H, P = E.getPrimitives('GEN')
		DSAmuons = E.getPrimitives('DSAMUON')
		RSAmuons = E.getPrimitives('RSAMUON')

		def matchedMuons(genMuon, recoMuons):
			matches = []
			for i,muon in enumerate(recoMuons):
				deltaR = muon.p4.DeltaR(genMuon.p4)
				if deltaR < 0.3:
					matches.append((i,deltaR,muon.pt))
			return sorted(matches, key=lambda tup:tup[1])

		# fill histogram
		for genMuon in (mu11, mu12, mu21, mu22):
			# cut genMuons outside the detector acceptance
			genMuonSelection = Selections.MuonSelection(genMuon, cutList='MuonAcceptanceCutList')
			if not genMuonSelection: continue

			genMuonLxy = genMuon.Lxy()
			HISTS[sp]['LxyDen'].Fill(genMuonLxy)
			HISTS[sp]['pTDen' ].Fill(genMuon.pt)

			PREFIX = 'DSA'
			foundDSA = False
			for recoMuons in (DSAmuons, RSAmuons):
				matches = matchedMuons(genMuon, recoMuons)
				if len(matches) != 0:
					closestRecoMuon = recoMuons[matches[0][0]]
					if Selections.MuonCuts['pt'].apply(closestRecoMuon):
						HISTS[sp][PREFIX+'_pTRes' ].Fill((closestRecoMuon.pt - genMuon.pt)/genMuon.pt)
						HISTS[sp][PREFIX+'_d0Dif' ].Fill((closestRecoMuon.d0 - genMuon.d0))
						HISTS[sp][PREFIX+'_LxyEff'].Fill(genMuonLxy)
						HISTS[sp][PREFIX+'_pTEff' ].Fill(genMuon.pt)

						if PREFIX == 'DSA':
							foundDSA = True

						if PREFIX == 'RSA' and not foundDSA:
							HISTS[sp]['ExtraLxy'].Fill(genMuonLxy)
							HISTS[sp]['ExtraPt' ].Fill(genMuon.pt)
				PREFIX = 'RSA'

	# cleanup
	del t
	f.Close()
	del f

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
args = parser.parse_args()

HISTS = {}
DEFAULT_HLIST = [
	'DSA_pTRes' ,
	'DSA_pTEff' ,
	'DSA_pTDen' ,
	'DSA_LxyEff',
	'DSA_LxyDen',
	'DSA_d0Dif' ,
	'DSA_nMuon' ,
	'RSA_pTRes' ,
	'RSA_pTEff' ,
	'RSA_pTDen' ,
	'RSA_LxyEff',
	'RSA_LxyDen',
	'RSA_d0Dif' ,
	'RSA_nMuon' ,
	'ExtraLxy'  ,
	'ExtraPt'   ,
]
HLIST = DEFAULT_HLIST
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

for sp in SIGNALPOINTS:
	HISTS[sp] = {}
	fillPlots(sp)
writeHistograms(sp)
