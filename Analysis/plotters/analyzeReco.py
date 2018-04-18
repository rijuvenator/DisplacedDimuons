import math
import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Analysis.Utilities as Utilities

#### CLASS AND FUNCTION DEFINITIONS ####
def matchedMuons(genMuon, recoMuons):
	matches = []
	for i,muon in enumerate(recoMuons):
		deltaR = muon.p4.DeltaR(genMuon.p4)
		if deltaR < 0.3 and Selections.MuonCuts['pt'].apply(muon) and muon.charge == genMuon.charge:
			matches.append({'idx':i, 'deltaR':deltaR, 'pt':muon.pt})
	return sorted(matches, key=lambda dic:dic['pt'])

def declareHistograms(self):
	CONFIG = {
			'pTRes'  : {'TITLE':';(*** p_{T} #minus gen p_{T})/gen p_{T};Counts', 'AXES':(1000,  -1., 3.   )},
			'pTEff'  : {'TITLE':';p_{T} [GeV];*** Match Efficiency'             , 'AXES':(1000,   0., 500. )},
			'LxyEff' : {'TITLE':';L_{xy} [cm];*** Match Efficiency'             , 'AXES':(1000,   0., 1500.)},
			'd0Dif'  : {'TITLE':';*** d_{0} #minus gen d_{0};Counts'            , 'AXES':(1000, -10., 10.  )},
			'nMuon'  : {'TITLE':';*** Muon Multiplicity;Counts'                 , 'AXES':(11  ,   0., 11.  )},
	}
	for KEY in CONFIG:
		for MUON in ('DSA', 'RSA'):
			self.HistInit(MUON+'_'+KEY  , CONFIG[KEY     ]['TITLE'].replace('***',MUON), *CONFIG[KEY     ]['AXES'])

	self.HistInit        ('ExtraPt'     , CONFIG['pTEff' ]['TITLE'].replace('*** ','') , *CONFIG['pTEff' ]['AXES'])
	self.HistInit        ('ExtraLxy'    , CONFIG['LxyEff']['TITLE'].replace('*** ','') , *CONFIG['LxyEff']['AXES'])

	self.HistInit        ('pTDen'       , ''                                           , *CONFIG['pTEff' ]['AXES'])
	self.HistInit        ('LxyDen'      , ''                                           , *CONFIG['LxyEff']['AXES'])

	self.HistInit        ('Dim_vtxChi2' , ';vtx #chi^{2}/dof;Counts'                   , 1000,   0., 10.          )
	self.HistInit        ('Dim_deltaR'  , ';#DeltaR;Counts'                            , 1000,   0., 10.          )
	self.HistInit        ('Dim_mass'    , ';M(#mu#mu);Counts'                          , 1000,   0., self.SP.mX*2 )
	self.HistInit        ('Dim_deltaPhi', ';|#Delta#Phi|;Counts'                       , 1000,   0., math.pi      )
	self.HistInit        ('Dim_cosAlpha', ';cos(#alpha);Counts'                        , 1000,  -1., 1.           )

def analyze(self, E):
	mu11, mu12, mu21, mu22, X1, X2, H, P = E.getPrimitives('GEN')
	DSAmuons = E.getPrimitives('DSAMUON')
	RSAmuons = E.getPrimitives('RSAMUON')
	Dimuons  = E.getPrimitives('DIMUON' )

	DSASelections = [Selections.MuonSelection(muon) for muon in DSAmuons]
	RSASelections = [Selections.MuonSelection(muon) for muon in RSAmuons]

	nDSA, nRSA = 0, 0
	for sel in DSASelections:
		if sel.passesAcceptance():
			nDSA += 1
	for sel in RSASelections:
		if sel.passesAcceptance():
			nRSA += 1
	self.HISTS['DSA_nMuon'].Fill(nDSA)
	self.HISTS['RSA_nMuon'].Fill(nRSA)

	# loop over genMuons and fill histograms based on matches
	for genMuon in (mu11, mu12, mu21, mu22):
		# cut genMuons outside the detector acceptance
		genMuonSelection = Selections.MuonSelection(genMuon, cutList='MuonAcceptanceCutList')
		if not genMuonSelection: continue

		genMuonLxy = genMuon.Lxy()
		self.HISTS['LxyDen'].Fill(genMuonLxy)
		self.HISTS['pTDen' ].Fill(genMuon.pt)

		PREFIX = 'DSA'
		foundDSA = False
		for recoMuons in (DSAmuons, RSAmuons):
			matches = matchedMuons(genMuon, recoMuons)
			if len(matches) != 0:
				closestRecoMuon = recoMuons[matches[0]['idx']]
				self.HISTS[PREFIX+'_pTRes' ].Fill((closestRecoMuon.pt - genMuon.pt)/genMuon.pt)
				self.HISTS[PREFIX+'_d0Dif' ].Fill((closestRecoMuon.d0 - genMuon.d0))
				self.HISTS[PREFIX+'_LxyEff'].Fill(genMuonLxy)
				self.HISTS[PREFIX+'_pTEff' ].Fill(genMuon.pt)

				if PREFIX == 'DSA':
					foundDSA = True

				if PREFIX == 'RSA' and not foundDSA:
					self.HISTS['ExtraLxy'].Fill(genMuonLxy)
					self.HISTS['ExtraPt' ].Fill(genMuon.pt)
			PREFIX = 'RSA'

	for dimuon in Dimuons:
		if DSASelections[dimuon.idx1].passesAcceptance() and DSASelections[dimuon.idx2].passesAcceptance():
			self.HISTS['Dim_vtxChi2' ].Fill(dimuon.normChi2)
			self.HISTS['Dim_deltaR'  ].Fill(dimuon.deltaR  )
			self.HISTS['Dim_mass'    ].Fill(dimuon.mass    )
			self.HISTS['Dim_deltaPhi'].Fill(dimuon.deltaPhi)
			self.HISTS['Dim_cosAlpha'].Fill(dimuon.cosAlpha)
			#dimuonSelection = Selections.DimuonSelection(dimuon)

#### RUN ANALYSIS ####
if __name__ == '__main__':
	ARGS = Analyzer.PARSER.parse_args()
	for METHOD in ('declareHistograms', 'analyze'):
		setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])
	analyzer = Analyzer.Analyzer(
		SIGNALPOINT = Utilities.SignalPoint(ARGS.SIGNALPOINT),
		BRANCHKEYS  = ('GEN', 'DSAMUON', 'RSAMUON', 'DIMUON'),
		DEVELOP     = ARGS.DEVELOP
	)
	analyzer.writeHistograms('roots/RecoPlots_{}.root')
