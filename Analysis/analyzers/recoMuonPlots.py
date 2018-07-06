import math
import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedMuons

# CONFIG stores the axis and function information so that histograms can be filled and declared in a loop
CONFIG = {
    'pT'       : {'AXES':(1000, 0., 500.), 'LAMBDA': lambda muon: muon.pt                                     , 'PRETTY':'p_{T} [GeV]'      },
    'eta'      : {'AXES':(1000,-3., 3.  ), 'LAMBDA': lambda muon: muon.eta                                    , 'PRETTY':None               },
    'd0'       : {'AXES':(1000, 0., 200.), 'LAMBDA': lambda muon: muon.d0()                                   , 'PRETTY':'d_{0} [cm]'       },
    'd0Sig'    : {'AXES':(1000, 0., 20. ), 'LAMBDA': lambda muon: muon.d0Sig()                                , 'PRETTY':None               },
    'normChi2' : {'AXES':(1000, 0., 5.  ), 'LAMBDA': lambda muon: muon.chi2/muon.ndof if muon.ndof != 0 else 0, 'PRETTY':None               },
    'nMuonHits': {'AXES':(50  , 0., 50. ), 'LAMBDA': lambda muon: muon.nMuonHits                              , 'PRETTY':None               },
    'nStations': {'AXES':(15  , 0., 15. ), 'LAMBDA': lambda muon: muon.nDTStations + muon.nCSCStations        , 'PRETTY':None               },
    'pTSig'    : {'AXES':(1000, 0.,  3. ), 'LAMBDA': lambda muon: muon.ptError/muon.pt                        , 'PRETTY':'#sigma_{pT}/p_{T}'},
}

#### CLASS AND FUNCTION DEFINITIONS ####
# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    for KEY in CONFIG:

        # the pretty strings are mostly in the cut dictionary
        # so use it if it's None
        # but use the string given if not
        XTIT = Selections.PrettyTitles[KEY] if CONFIG[KEY]['PRETTY'] is None else CONFIG[KEY]['PRETTY']

        for MUON in ('DSA', 'RSA'):
            self.HistInit(MUON+'_'+KEY           , ';'+XTIT+';Counts', *CONFIG[KEY]['AXES'])
            self.HistInit(MUON+'_'+KEY+'_Matched', ';'+XTIT+';Counts', *CONFIG[KEY]['AXES'])

    for MUON in ('DSA', 'RSA'):
        self.HistInit(MUON+'_nMuon'        , ';Muon Multiplicity;Counts', 15, 0., 15.)
        self.HistInit(MUON+'_nMuon_Matched', ';Muon Multiplicity;Counts', 15, 0., 15.)

# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    Event    = E.getPrimitives('EVENT')
    DSAmuons = E.getPrimitives('DSAMUON')
    RSAmuons = E.getPrimitives('RSAMUON')

    eventWeight = 1.
    try:
        eventWeight = 1. if Event.weight > 0. else -1.
    except:
        pass

    SelectMuons = False
    # require reco muons to pass all selections
    if SelectMuons:
        DSASelections = [Selections.MuonSelection(muon) for muon in DSAmuons]
        RSASelections = [Selections.MuonSelection(muon) for muon in RSAmuons]
        selectedDSAmuons = [mu for idx,mu in enumerate(DSAmuons) if DSASelections[idx]]
        selectedRSAmuons = [mu for idx,mu in enumerate(RSAmuons) if RSASelections[idx]]

    # don't require reco muons to pass all selections
    else:
        selectedDSAmuons = DSAmuons
        selectedRSAmuons = RSAmuons
    
    # fill histograms for every reco muon
    for MUON, recoMuons in (('DSA', selectedDSAmuons), ('RSA', selectedRSAmuons)):
        for muon in recoMuons:
            for KEY in CONFIG:
                self.HISTS[MUON+'_'+KEY].Fill(CONFIG[KEY]['LAMBDA'](muon), eventWeight)
        self.HISTS[MUON+'_nMuon'].Fill(len(recoMuons), eventWeight)

    # get gen particles if this is a signal sample
    if self.SP is not None:
        if '4Mu' in self.NAME:
            mu11, mu12, mu21, mu22, X1, X2, H, P, extramu = E.getPrimitives('GEN', 'HTo2XTo4Mu')
            genMuons = (mu11, mu12, mu21, mu22)
        elif '2Mu2J' in self.NAME:
            mu1, mu2, j1, j2, X, XP, H, P, extramu = E.getPrimitives('GEN', 'HTo2XTo2Mu2J')
            genMuons = (mu1, mu2)

        # fill histograms only for matched reco muons
        for genMuon in genMuons:
            # cut genMuons outside the detector acceptance
            # don't do it for now
            #genMuonSelection = Selections.AcceptanceSelection(genMuon)

            for MUON, recoMuons in (('DSA', selectedDSAmuons), ('RSA', selectedRSAmuons)):
                matches = matchedMuons(genMuon, recoMuons)
                for match in matches:
                    muon = recoMuons[match['idx']]
                    for KEY in CONFIG:
                        self.HISTS[MUON+'_'+KEY+'_Matched'].Fill(CONFIG[KEY]['LAMBDA'](muon), eventWeight)
                self.HISTS[MUON+'_nMuon_Matched'].Fill(len(matches), eventWeight)

#### RUN ANALYSIS ####
if __name__ == '__main__':
    ARGS = Analyzer.PARSER.parse_args()
    Analyzer.setSample(ARGS)
    for METHOD in ('declareHistograms', 'analyze'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])
    analyzer = Analyzer.Analyzer(
        ARGS        = ARGS,
        BRANCHKEYS  = ('EVENT', 'DSAMUON', 'RSAMUON', 'GEN'),
    )
    analyzer.writeHistograms('roots/RecoMuonPlots_{}.root')
