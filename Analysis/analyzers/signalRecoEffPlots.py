import math
import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedMuons, matchedDimuons

# CONFIG stores the title and axis tuple so that the histograms can be declared in a loop
HEADERS = ('XTITLE', 'AXES', 'LAMBDA', 'PRETTY', 'ACC_LAMBDA')
VALUES  = (
    ('pT'  , 'p_{T} [GeV]'       , (1500,       0.,   1500.), lambda gmu : gmu.pt                         , 'p_{T}'     , lambda sel: sel.allExcept('a_pT' )),
    ('eta' , '#eta'              , (1000,      -3.,      3.), lambda gmu : gmu.eta                        , '#eta'      , lambda sel: sel.allExcept('a_eta')),
    ('phi' , '#phi'              , (1000, -math.pi, math.pi), lambda gmu : gmu.phi                        , '#phi'      , lambda sel: sel                   ),
    ('Lxy' , 'L_{xy} [cm]'       , (1000,       0.,    800.), lambda gmu : gmu.Lxy()                      , 'L_{xy}'    , lambda sel: sel.allExcept('a_Lxy')),
    ('d0'  , 'd_{0} [cm]'        , (1000,       0.,    600.), lambda gmu : gmu.d0()                       , 'd_{0}'     , lambda sel: sel                   ),
    ('dR'  , '#DeltaR(#mu#mu)'   , (1000,       0.,      5.), lambda pair: pair[0].deltaR                 , '#DeltaR'   , lambda sel: sel                   ),
    ('dphi', '#Delta#phi(#mu#mu)', (1000, -math.pi, math.pi), lambda pair: pair[0].p4.DeltaPhi(pair[1].p4), '#Delta#phi', lambda sel: sel                   ),
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
        for MUON in ('DSA', 'RSA', 'REF'):
            TITLE = ';'+CONFIG[KEY]['XTITLE']+';'+MUON+' Reconstruction Efficiency'
            self.HistInit(MUON+'_'+KEY+'Eff'      , TITLE, *CONFIG[KEY]['AXES'])
            TITLE = TITLE.replace('Reconstruction', 'Charge Reconstruction')
            self.HistInit(MUON+'_'+KEY+'ChargeEff', TITLE, *CONFIG[KEY]['AXES'])
            self.HistInit(MUON+'_'+KEY+'ChargeDen', ''   , *CONFIG[KEY]['AXES'])

        # gen denominator plots, can reuse the axes
        self.HistInit(KEY+'Den'        , '', *CONFIG[KEY]['AXES'])
        self.HistInit('REF_'+KEY+'Den' , '', *CONFIG[KEY]['AXES'])

        # descoping extra; not really needed anymore

# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    if self.SP is None:
        raise Exception('[ANALYZER ERROR]: This script runs on signal only.')
    if self.TRIGGER:
        if not Selections.passedTrigger(E): return
    if '4Mu' in self.NAME:
        mu11, mu12, mu21, mu22, X1, X2, H, P, extramu = E.getPrimitives('GEN')
        genMuons = (mu11, mu12, mu21, mu22)
        genMuonPairs = ((mu11, mu12), (mu21, mu22))
    elif '2Mu2J' in self.NAME:
        mu1, mu2, j1, j2, X, XP, H, P, extramu = E.getPrimitives('GEN')
        genMuons = (mu1, mu2)
        genMuonPairs = ((mu1, mu2),)
    DSAmuons = E.getPrimitives('DSAMUON')
    RSAmuons = E.getPrimitives('RSAMUON')
    Dimuons  = E.getPrimitives('DIMUON' )

    ALL = True if 'All' in self.CUTS else False
    # require reco muons to pass all selections
    if ALL:
        DSASelections = [Selections.MuonSelection(muon) for muon in DSAmuons]
        RSASelections = [Selections.MuonSelection(muon) for muon in RSAmuons]
        selectedDSAmuons = [mu  for idx,mu  in enumerate(DSAmuons) if DSASelections   [idx]]
        selectedRSAmuons = [mu  for idx,mu  in enumerate(RSAmuons) if RSASelections   [idx]]
        selectedDimuons  = Dimuons

    # don't require reco muons to pass all selections
    else:
        selectedDSAmuons = DSAmuons
        selectedRSAmuons = RSAmuons
        selectedDimuons  = Dimuons

    # loop over genMuons and fill histograms based on matches
    for genMuonPair in genMuonPairs:
        # genMuonMatches are a dictionary of the return tuple of length 3
        # DSA and RSA get a "DUMMY" dimuons argument so that no dimuon matching will be done but the relevant
        # exitcode information is still preserved; see AnalysisTools
        genMuonMatches = {'DSA':None, 'RSA':None, 'REF':None}
        for MUON, recoMuons in (('DSA', selectedDSAmuons), ('RSA', selectedRSAmuons)):
            genMuonMatches[MUON]  = matchedDimuons(genMuonPair, ('DUMMY',), recoMuons, vertex='BS')
        for MUON in ('REF',):
            genMuonMatches['REF'] = matchedDimuons(genMuonPair, selectedDimuons)

        # now figure out the closest match, or None if they overlap
        # exitcode helps to make sure that both gen muons never match the same reco muon
        # muonMatches is always a list of length 2, corresponding to [[list of matches to gen0], [list of matches to gen1]]
        # sorted by deltaR, so [0] is the closest, etc.
        genMuonMatch = [{'DSA': None, 'RSA': None, 'REF': None}, {'DSA': None, 'RSA': None, 'REF': None}]
        for MUON in ('DSA', 'RSA'):
            dimuonMatches, muonMatches, exitcode = genMuonMatches[MUON]
            if   exitcode == 1:
                genMuonMatch[0][MUON] = muonMatches[0][0]
                genMuonMatch[1][MUON] = muonMatches[1][0]
            elif exitcode == 2:
                genMuonMatch[0][MUON] = muonMatches[0][0]
                genMuonMatch[1][MUON] = muonMatches[1][1]
            elif exitcode == 3:
                genMuonMatch[0][MUON] = muonMatches[0][1]
                genMuonMatch[1][MUON] = muonMatches[1][0]
            elif exitcode == 4:
                genMuonMatch[0][MUON] = muonMatches[0][0]
                genMuonMatch[1][MUON] = None
            elif exitcode == 5:
                genMuonMatch[0][MUON] = None
                genMuonMatch[1][MUON] = muonMatches[1][0]
            elif exitcode == 6:
                genMuonMatch[0][MUON] = muonMatches[0][0]
                genMuonMatch[1][MUON] = None
            elif exitcode == 7:
                genMuonMatch[0][MUON] = None
                genMuonMatch[1][MUON] = muonMatches[1][0]
            elif exitcode == 8:
                genMuonMatch[0][MUON] = None
                genMuonMatch[1][MUON] = None

        # matched refitted muons if there was at least one dimuon
        for MUON in ('REF',):
            dimuonMatches, muonMatches, exitcode = genMuonMatches['REF']
            if len(dimuonMatches) > 0:
                genMuonMatch[0]['REF'] = muonMatches[0][0]
                genMuonMatch[1]['REF'] = muonMatches[1][0]

        # now loop over the quantities and fill. split by whether it's a mu plot or a mumu plot
        genMuonPairSelection = Selections.AcceptanceSelection(genMuonPair)
        genMuonSelections    = [Selections.AcceptanceSelection(genMuonPair[0]), Selections.AcceptanceSelection(genMuonPair[1])]
        for KEY in CONFIG:
            F = CONFIG[KEY]['LAMBDA']
            AF = CONFIG[KEY]['ACC_LAMBDA']

            # mumu plots: check if pair in acceptance, fill den, fill num if both match
            if KEY == 'dphi' or KEY == 'dR':
                if AF(genMuonPairSelection):
                    self.HISTS[       KEY+'Den'].Fill(F(genMuonPair))
                    self.HISTS['REF_'+KEY+'Den'].Fill(F(genMuonPair))

                    for MUON in ('DSA', 'RSA', 'REF'):
                        if genMuonMatch[0][MUON] is not None and genMuonMatch[1][MUON] is not None:
                            self.EffPairFill(MUON, KEY, genMuonPair, genMuonMatch, F)

            # mu plots: for DSA and RSA, check if gen muon in acceptance, fill den, fill num if match
            # for REF, check if pair in acceptance, fill den, full num if both match
            else:
                for idx, genMuon in enumerate(genMuonPair):
                    if AF(genMuonSelections[idx]):
                        self.HISTS[KEY+'Den'].Fill(F(genMuon))

                        for MUON in ('DSA', 'RSA'):
                            if genMuonMatch[idx][MUON] is not None:
                                self.EffSingleFill(MUON, KEY, genMuon, genMuonMatch, F, idx)

                    if AF(genMuonPairSelection):
                        self.HISTS['REF_'+KEY+'Den'].Fill(F(genMuon))

                        for MUON in ('REF',):
                            if genMuonMatch[0][MUON] is not None and genMuonMatch[1][MUON] is not None:
                                self.EffSingleFill(MUON, KEY, genMuon, genMuonMatch, F, idx)

# modular fill functions for use above: gen muon pair
def EffPairFill(self, MUON, KEY, genMuonPair, genMuonMatch, F):

    # first fill the eff plot; the numerator is the denominator for charge
    self.HISTS[MUON+'_'+KEY+'Eff'      ].Fill(F(genMuonPair))
    self.HISTS[MUON+'_'+KEY+'ChargeDen'].Fill(F(genMuonPair))

    # THEN if the charges are the same, fill. Should be flat and close to 1.
    closestRecoMuons = [genMuonMatch[0][MUON]['muon'], genMuonMatch[1][MUON]['muon']]
    if genMuonPair[0].charge == closestRecoMuons[0].charge and genMuonPair[1].charge == closestRecoMuons[1].charge:
        self.HISTS[MUON+'_'+KEY+'ChargeEff'].Fill(F(genMuonPair))

# modular fill functions for use above: individual gen muon
def EffSingleFill(self, MUON, KEY, genMuon, genMuonMatch, F, idx):

    # first fill the eff plot; the numerator is the denominator for charge
    self.HISTS[MUON+'_'+KEY+'Eff'      ].Fill(F(genMuon))
    self.HISTS[MUON+'_'+KEY+'ChargeDen'].Fill(F(genMuon))

    # THEN if the charges are the same, fill. Should be flat and close to 1.
    closestRecoMuon = genMuonMatch[idx][MUON]['muon']
    if genMuon.charge == closestRecoMuon.charge:
        self.HISTS[MUON+'_'+KEY+'ChargeEff'].Fill(F(genMuon))

#### RUN ANALYSIS ####
if __name__ == '__main__':
    ARGS = Analyzer.PARSER.parse_args()
    Analyzer.setSample(ARGS)
    for METHOD in ('declareHistograms', 'analyze', 'EffPairFill', 'EffSingleFill'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])
    analyzer = Analyzer.Analyzer(
        ARGS        = ARGS,
        BRANCHKEYS  = ('GEN', 'DSAMUON', 'RSAMUON', 'TRIGGER', 'DIMUON'),
    )
    analyzer.writeHistograms('roots/SignalRecoEffPlots{}{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else '', ARGS.CUTS))
