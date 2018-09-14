import math
import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedMuons

# CONFIG stores the title and axis tuple so that the histograms can be declared in a loop
HEADERS = ('XTITLE', 'AXES', 'LAMBDA', 'PRETTY', 'ACC_LAMBDA')
VALUES  = (
    ('pT'  , 'p_{T} [GeV]'       , (1000,       0.,    500.), lambda muon: muon.pt       , 'p_{T}'     , lambda sel: sel.allExcept('a_pT' )),
    ('eta' , '#eta'              , (1000,      -3.,      3.), lambda muon: muon.eta      , '#eta'      , lambda sel: sel.allExcept('a_eta')),
    ('phi' , '#phi'              , (1000, -math.pi, math.pi), lambda muon: muon.phi      , '#phi'      , lambda sel: sel                   ),
    ('Lxy' , 'L_{xy} [cm]'       , (1000,       0.,    800.), lambda muon: muon.Lxy()    , 'L_{xy}'    , lambda sel: sel.allExcept('a_Lxy')),
    ('d0'  , 'd_{0} [cm]'        , (1000,       0.,    200.), lambda muon: muon.d0()     , 'd_{0}'     , lambda sel: sel                   ),
    ('dR'  , '#DeltaR(#mu#mu)'   , (1000,       0.,      5.), lambda pair: pair[0].deltaR, '#DeltaR'   , lambda sel: sel                   ),
    ('dphi', '#Delta#phi(#mu#mu)', (1000, -math.pi, math.pi), None                       , '#Delta#phi', lambda sel: sel                   ),
)
CONFIG = {}
for VAL in VALUES:
    KEY, VALS = VAL[0], VAL[1:]
    CONFIG[KEY] = dict(zip(HEADERS, VALS))

def getMuMuDeltaPhi(pair):
    return pair[0].p4.DeltaPhi(pair[1].p4)
CONFIG['dphi']['LAMBDA'] = getMuMuDeltaPhi

#### CLASS AND FUNCTION DEFINITIONS ####
# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    for KEY in CONFIG:
        # one Eff, ChargeEff, and ChargeDen plot for each of DSA and RSA
        for MUON in ('DSA', 'RSA'):
            TITLE = ';'+CONFIG[KEY]['XTITLE']+';'+MUON+' Reconstruction Efficiency'
            self.HistInit(MUON+'_'+KEY+'Eff'      , TITLE, *CONFIG[KEY]['AXES'])
            TITLE = TITLE.replace('Reconstruction', 'Charge Reconstruction')
            self.HistInit(MUON+'_'+KEY+'ChargeEff', TITLE, *CONFIG[KEY]['AXES'])
            self.HistInit(MUON+'_'+KEY+'ChargeDen', ''   , *CONFIG[KEY]['AXES'])

        # "extra" and gen denominator plots, can reuse the axes
        self.HistInit(KEY+'Den'        , '', *CONFIG[KEY]['AXES'])
        self.HistInit(KEY+'Extra'      , '', *CONFIG[KEY]['AXES'])

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

    SelectMuons = False
    SelectMuons_pT30 = False
    # require reco muons to pass all selections
    if SelectMuons:
        DSASelections = [Selections.MuonSelection(muon) for muon in DSAmuons]
        RSASelections = [Selections.MuonSelection(muon) for muon in RSAmuons]
        selectedDSAmuons = [mu  for idx,mu  in enumerate(DSAmuons) if DSASelections   [idx]]
        selectedRSAmuons = [mu  for idx,mu  in enumerate(RSAmuons) if RSASelections   [idx]]

    # require DSA muons to pass only the pT cut
    elif SelectMuons_pT30:
        DSASelections = [Selections.MuonSelection(muon, cutList=('pT',)) for muon in DSAmuons]
        RSASelections = [Selections.MuonSelection(muon, cutList=('pT',)) for muon in RSAmuons]
        selectedDSAmuons = [mu  for idx,mu  in enumerate(DSAmuons) if DSASelections   [idx]]
        selectedRSAmuons = [mu  for idx,mu  in enumerate(RSAmuons) if RSASelections   [idx]]

    # don't require reco muons to pass all selections
    else:
        selectedDSAmuons = DSAmuons
        selectedRSAmuons = RSAmuons

    # loop over genMuons and fill histograms based on matches
    for genMuonPair in genMuonPairs:
        # first make lists of matches
        genMuonMatches = [{'DSA':None, 'RSA':None}, {'DSA':None, 'RSA':None}]
        for idx, genMuon in enumerate(genMuonPair):
            for MUON, recoMuons in (('DSA', selectedDSAmuons), ('RSA', selectedRSAmuons)):
                genMuonMatches[idx][MUON] = matchedMuons(genMuon, recoMuons)

        # now determine if both genMuons matched, accounting for multiple matches
        genMuonMatch   = [{'DSA':None, 'RSA':None}, {'DSA':None, 'RSA':None}]
        for MUON in ('DSA', 'RSA'):
            lens = [len(genMuonMatches[0][MUON]), len(genMuonMatches[1][MUON])]
            # both gen muons matched
            if   lens[0] >  0 and lens[1] >  0:
                matches = [genMuonMatches[0][MUON], genMuonMatches[1][MUON]]
                # but to different reco muons
                if matches[0][0]['idx'] != matches[1][0]['idx']:
                    genMuonMatch[0][MUON] = genMuonMatches[0][MUON][0]
                    genMuonMatch[1][MUON] = genMuonMatches[1][MUON][0]
                # to the SAME reco muon
                else:
                    # which one wins the deltaR competition?
                    # 0 won. 1 gets second best or None.
                    if matches[0][0]['deltaR'] < matches[1][0]['deltaR']:
                        genMuonMatch[0][MUON] = genMuonMatches[0][MUON][0]
                        if lens[1] > 1:
                            genMuonMatch[1][MUON] = genMuonMatches[1][MUON][1]
                        else:
                            genMuonMatch[1][MUON] = None
                    # 1 won. 0 gets second best or None.
                    else:
                        genMuonMatch[1][MUON] = genMuonMatches[1][MUON][0]
                        if lens[0] > 1:
                            genMuonMatch[0][MUON] = genMuonMatches[0][MUON][1]
                        else:
                            genMuonMatch[0][MUON] = None
            # second gen muon didn't match
            elif lens[0] >  0 and lens[1] == 0:
                genMuonMatch[0][MUON] = genMuonMatches[0][MUON][0]
            # first gen muon didn't match
            elif lens[0] == 0 and lens[1] >  0:
                genMuonMatch[1][MUON] = genMuonMatches[1][MUON][0]
            # neither gen muon matched
            elif lens[0] == 0 and lens[1] == 0:
                pass

        # now loop over the quantities and fill. split by whether it's a mu plot or a mumu plot.
        for KEY in CONFIG:
            F = CONFIG[KEY]['LAMBDA']
            AF = CONFIG[KEY]['ACC_LAMBDA']
            # mu mu plot
            if KEY == 'dphi' or KEY == 'dR':
                # cut genMuons outside the detector acceptance
                genMuonPairSelection = Selections.AcceptanceSelection(genMuonPair)
                if AF(genMuonPairSelection):
                    self.HISTS[KEY+'Den'].Fill(F(genMuonPair))

                    foundDSA = False
                    for MUON, recoMuons in (('DSA', selectedDSAmuons), ('RSA', selectedRSAmuons)):
                        if genMuonMatch[0][MUON] is not None and genMuonMatch[1][MUON] is not None:
                            self.HISTS[MUON+'_'+KEY+'Eff'      ].Fill(F(genMuonPair))
                            self.HISTS[MUON+'_'+KEY+'ChargeDen'].Fill(F(genMuonPair))

                            # THEN if the charges are the same, fill. Should be flat and close to 1.
                            closestRecoMuons = [recoMuons[genMuonMatch[0][MUON]['idx']], recoMuons[genMuonMatch[1][MUON]['idx']]]
                            if genMuonPair[0].charge == closestRecoMuons[0].charge and genMuonPair[1].charge == closestRecoMuons[1].charge:
                                self.HISTS[MUON+'_'+KEY+'ChargeEff'].Fill(F(genMuonPair))

                            if MUON == 'DSA':
                                foundDSA = True

                            if MUON == 'RSA' and not foundDSA:
                                self.HISTS[KEY+'Extra'].Fill(F(genMuonPair))
            # mu plot
            else:
                for idx, genMuon in enumerate(genMuonPair):
                    # cut genMuons outside the detector acceptance
                    genMuonSelection = Selections.AcceptanceSelection(genMuon)
                    if AF(genMuonSelection):
                        self.HISTS[KEY+'Den'].Fill(F(genMuon))

                        foundDSA = False
                        for MUON, recoMuons in (('DSA', selectedDSAmuons), ('RSA', selectedRSAmuons)):
                            if genMuonMatch[idx][MUON] is not None:
                                self.HISTS[MUON+'_'+KEY+'Eff'      ].Fill(F(genMuon))
                                self.HISTS[MUON+'_'+KEY+'ChargeDen'].Fill(F(genMuon))

                                # THEN if the charges are the same, fill. Should be flat and close to 1.
                                closestRecoMuon = recoMuons[genMuonMatch[idx][MUON]['idx']]
                                if genMuon.charge == closestRecoMuon.charge:
                                    self.HISTS[MUON+'_'+KEY+'ChargeEff'].Fill(F(genMuon))

                                if MUON == 'DSA':
                                    foundDSA = True

                                if MUON == 'RSA' and not foundDSA:
                                    self.HISTS[KEY+'Extra'].Fill(F(genMuon))

#### RUN ANALYSIS ####
if __name__ == '__main__':
    ARGS = Analyzer.PARSER.parse_args()
    Analyzer.setSample(ARGS)
    for METHOD in ('declareHistograms', 'analyze'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])
    analyzer = Analyzer.Analyzer(
        ARGS        = ARGS,
        BRANCHKEYS  = ('GEN', 'DSAMUON', 'RSAMUON', 'TRIGGER'),
    )
    analyzer.writeHistograms('roots/SignalMatchEffPlots{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else ''))
