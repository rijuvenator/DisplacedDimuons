import math
import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities

# CONFIG stores the axis and function information so that histograms can be filled and declared in a loop
CONFIG = {
    'pT'       : {'AXES':(1000, 0., 100.), 'LAMBDA': lambda muon: muon.pt                                     },
    'eta'      : {'AXES':(1000,-5., 5.  ), 'LAMBDA': lambda muon: muon.eta                                    },
    'd0'       : {'AXES':(1000, 0., 20. ), 'LAMBDA': lambda muon: muon.d0()                                   },
    'd0Sig'    : {'AXES':(1000, 0., 20. ), 'LAMBDA': lambda muon: muon.d0Sig()                                },
    'normChi2' : {'AXES':(1000, 0., 5.  ), 'LAMBDA': lambda muon: muon.chi2/muon.ndof if muon.ndof != 0 else 0},
    'nMuonHits': {'AXES':(50  , 0., 50. ), 'LAMBDA': lambda muon: muon.nMuonHits                              },
    'nStations': {'AXES':(15  , 0., 15. ), 'LAMBDA': lambda muon: muon.nDTStations + muon.nCSCStations        },
}

#### CLASS AND FUNCTION DEFINITIONS ####
# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    for KEY in CONFIG:

        # the pretty strings are mostly in the cut dictionary
        # but change this if new quantities are added, with a PRETTY key in CONFIG
        # so use the Pretty version and tack on units for pT and d0
        XTIT = Selections.PrettyTitles[KEY]
        if KEY == 'pT': XTIT += ' [GeV]'
        if KEY == 'd0': XTIT += ' [cm]'

        for MUON in ('DSA', 'RSA'):
            self.HistInit(MUON+'_'+KEY, ';'+XTIT+';Counts', *CONFIG[KEY]['AXES'])

# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    DSAmuons = E.getPrimitives('DSAMUON')
    RSAmuons = E.getPrimitives('RSAMUON')

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

    for MUON, recoMuons in (('DSA', selectedDSAmuons), ('RSA', selectedRSAmuons)):
        for muon in recoMuons:
            for KEY in CONFIG:
                self.HISTS[MUON+'_'+KEY].Fill(CONFIG[KEY]['LAMBDA'](muon))

#### RUN ANALYSIS ####
if __name__ == '__main__':
    ARGS = Analyzer.PARSER.parse_args()
    Analyzer.setFNAME(ARGS)
    for METHOD in ('declareHistograms', 'analyze'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])
    analyzer = Analyzer.Analyzer(
        NAME        = ARGS.NAME,
        SIGNALPOINT = Utilities.SignalPoint(ARGS.SIGNALPOINT),
        BRANCHKEYS  = ('DSAMUON', 'RSAMUON'),
        TEST        = ARGS.TEST,
        SPLITTING   = ARGS.SPLITTING,
        FILE        = ARGS.FNAME
    )
    analyzer.writeHistograms('roots/RecoMuonPlots_{}.root')
