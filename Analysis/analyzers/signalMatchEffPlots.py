import math
import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedMuons

# CONFIG stores the title and axis tuple so that the histograms can be declared in a loop
HEADERS = ('XTITLE', 'AXES', 'LAMBDA', 'PRETTY', 'ACC_LAMBDA')
VALUES  = (
    ('pT' , 'p_{T} [GeV]', (1000,       0.,    500.), lambda muon: muon.pt       , 'p_{T}'  , lambda sel: sel.allExcept('a_pT' )),
    ('eta', '#eta'       , (1000,      -3.,      3.), lambda muon: muon.eta      , '#eta'   , lambda sel: sel.allExcept('a_eta')),
    ('phi', '#phi'       , (1000, -math.pi, math.pi), lambda muon: muon.phi      , '#phi'   , lambda sel: sel                   ),
    ('Lxy', 'L_{xy} [cm]', (1000,       0.,    800.), lambda muon: muon.Lxy()    , 'L_{xy}' , lambda sel: sel.allExcept('a_Lxy')),
    ('d0' , 'd_{0} [cm]' , (1000,       0.,    200.), lambda muon: muon.d0()     , 'd_{0}'  , lambda sel: sel                   ),
)
CONFIG = {}
for VAL in VALUES:
    KEY, VALS = VAL[0], VAL[1:]
    CONFIG[KEY] = dict(zip(HEADERS, VALS))

#### CLASS AND FUNCTION DEFINITIONS ####
# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    for KEY in CONFIG:
        # one Eff, ChargeEff, and ChargeDen plot for each of DSA and RSA
        for MUON in ('DSA', 'RSA'):
            TITLE = ';'+CONFIG[KEY]['XTITLE']+';'+MUON+' Match Efficiency'
            self.HistInit(MUON+'_'+KEY+'Eff'      , TITLE, *CONFIG[KEY]['AXES'])
            TITLE = TITLE.replace('Match', 'Charge Match')
            self.HistInit(MUON+'_'+KEY+'ChargeEff', TITLE, *CONFIG[KEY]['AXES'])
            self.HistInit(MUON+'_'+KEY+'ChargeDen', ''   , *CONFIG[KEY]['AXES'])

        # "extra" and gen denominator plots, can reuse the axes
        self.HistInit(KEY+'Den'        , '', *CONFIG[KEY]['AXES'])
        self.HistInit(KEY+'Extra'      , '', *CONFIG[KEY]['AXES'])

# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    if self.SP is None:
        raise Exception('[ANALYZER ERROR]: This script runs on signal only.')
    if '4Mu' in self.NAME:
        mu11, mu12, mu21, mu22, X1, X2, H, P = E.getPrimitives('GEN', 'HTo2XTo4Mu')
        genMuons = (mu11, mu12, mu21, mu22)
    elif '2Mu2J' in self.NAME:
        mu1, mu2, j1, j2, X, XP, H, P = E.getPrimitives('GEN', 'HTo2XTo2Mu2J')
        genMuons = (mu1, mu2)
    DSAmuons = E.getPrimitives('DSAMUON')
    RSAmuons = E.getPrimitives('RSAMUON')

    SelectMuons = False
    # require reco muons to pass all selections
    if SelectMuons:
        DSASelections = [Selections.MuonSelection(muon) for muon in DSAmuons]
        RSASelections = [Selections.MuonSelection(muon) for muon in RSAmuons]
        selectedDSAmuons = [mu  for idx,mu  in enumerate(DSAmuons) if DSASelections   [idx]]
        selectedRSAmuons = [mu  for idx,mu  in enumerate(RSAmuons) if RSASelections   [idx]]

    # don't require reco muons to pass all selections
    else:
        selectedDSAmuons = DSAmuons
        selectedRSAmuons = RSAmuons

    # loop over genMuons and fill histograms based on matches
    for genMuon in genMuons:
        # cut genMuons outside the detector acceptance
        genMuonSelection = Selections.AcceptanceSelection(genMuon)

        # fill the gen denominator histograms
        for KEY in CONFIG:
            F = CONFIG[KEY]['LAMBDA']
            AF = CONFIG[KEY]['ACC_LAMBDA']
            if AF(genMuonSelection):
                self.HISTS[KEY+'Den'].Fill(F(genMuon))

        # find closest matched reco muon for DSA and RSA
        foundDSA = False
        for MUON, recoMuons in (('DSA', selectedDSAmuons), ('RSA', selectedRSAmuons)):
            matches = matchedMuons(genMuon, recoMuons)
            if len(matches) != 0:
                # take the closest match
                closestRecoMuon = recoMuons[matches[0]['idx']]
                # fill all the quantities
                # also fill the charge denominator histograms: denominator is +1 for each dR match
                for KEY in CONFIG:
                    F = CONFIG[KEY]['LAMBDA']
                    AF = CONFIG[KEY]['ACC_LAMBDA']
                    if not AF(genMuonSelection): continue

                    self.HISTS[MUON+'_'+KEY+'Eff'      ].Fill(F(genMuon))
                    self.HISTS[MUON+'_'+KEY+'ChargeDen'].Fill(F(genMuon))

                    # THEN if the charges are the same, fill. Should be flat and close to 1.
                    if genMuon.charge == closestRecoMuon.charge:
                        self.HISTS[MUON+'_'+KEY+'ChargeEff'].Fill(F(genMuon))

                if MUON == 'DSA':
                    foundDSA = True

                if MUON == 'RSA' and not foundDSA:
                    for KEY in CONFIG:
                        F = CONFIG[KEY]['LAMBDA']
                        AF = CONFIG[KEY]['ACC_LAMBDA']
                        if not AF(genMuonSelection): continue
                        self.HISTS[KEY+'Extra'].Fill(F(genMuon))

#### RUN ANALYSIS ####
if __name__ == '__main__':
    ARGS = Analyzer.PARSER.parse_args()
    Analyzer.setSample(ARGS)
    for METHOD in ('declareHistograms', 'analyze'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])
    analyzer = Analyzer.Analyzer(
        ARGS        = ARGS,
        BRANCHKEYS  = ('GEN', 'DSAMUON', 'RSAMUON'),
    )
    analyzer.writeHistograms('roots/SignalMatchEffPlots_{}.root')
