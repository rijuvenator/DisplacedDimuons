import math
import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities

# CONFIG stores the axis and function information so that histograms can be filled and declared in a loop
CONFIG = {
    'pt'      : {'AXES':( 0., 100.   ), 'LAMBDA': lambda dimuon: dimuon.pt      },
    'eta'     : {'AXES':(-5., 5.     ), 'LAMBDA': lambda dimuon: dimuon.eta     },
    'Lxy'     : {'AXES':( 0., 600.   ), 'LAMBDA': lambda dimuon: dimuon.Lxy()   },
    'LxySig'  : {'AXES':( 0., 20.    ), 'LAMBDA': lambda dimuon: dimuon.LxySig()},
    'vtxChi2' : {'AXES':( 0., 5.     ), 'LAMBDA': lambda dimuon: dimuon.normChi2},
    'deltaR'  : {'AXES':( 0., 5.     ), 'LAMBDA': lambda dimuon: dimuon.deltaR  },
    'mass'    : {'AXES':( 0., 20.    ), 'LAMBDA': lambda dimuon: dimuon.mass    },
    'deltaPhi': {'AXES':( 0., math.pi), 'LAMBDA': lambda dimuon: dimuon.deltaPhi},
    'cosAlpha': {'AXES':(-1., 1.     ), 'LAMBDA': lambda dimuon: dimuon.cosAlpha},
}

#### CLASS AND FUNCTION DEFINITIONS ####
# declare histograms for Analyzer class
def declareHistograms(self):
    for KEY in CONFIG:

        # the pretty strings are mostly in the cut dictionary
        # but change this if new quantities are added, with a PRETTY key in CONFIG
        # so use the Pretty version and tack on units for pT and Lxy
        XTIT = Selections.PrettyTitles[KEY]
        if KEY == 'pt' : XTIT += ' [GeV]'
        if KEY == 'Lxy': XTIT += ' [cm]'

        self.HistInit('Dim_'+KEY, ';'+XTIT+';Counts', 1000, *CONFIG[KEY]['AXES'])

# internal loop function for Analyzer class
def analyze(self, E):
    DSAmuons = E.getPrimitives('DSAMUON')
    Dimuons  = E.getPrimitives('DIMUON' )

    # require dimuons to pass all selections and the DSA muons to pass all selections
    #DSASelections    = [Selections.MuonSelection(muon) for muon in DSAmuons]
    #DimuonSelections = [Selections.DimuonSelection(dimuon) for dimuon in Dimuons ]
    #selectedDimuons  = [dim for idx,dim in enumerate(Dimuons) if DimuonSelections[idx] and DSASelections[dim.idx1] and DSASelections[dim.idx2]]

    # don't require dimuons to pass all selections, but require DSA muons to pass all selections
    #DSASelections   = [Selections.MuonSelection(muon) for muon in DSAmuons]
    #selectedDimuons = [dim for idx,dim in enumerate(Dimuons) if DSASelections[dim.idx1] and DSASelections[dim.idx2]]

    # don't require dimuons to pass all selections, and don't require DSA muons to pass all selections, either
    selectedDimuons = Dimuons

    for dimuon in selectedDimuons:
        for KEY in CONFIG:
            self.HISTS['Dim_'+KEY].Fill(CONFIG[KEY]['LAMBDA'](dimuon))

#### RUN ANALYSIS ####
if __name__ == '__main__':
    ARGS = Analyzer.PARSER.parse_args()
    Analyzer.setFNAME(ARGS)
    for METHOD in ('declareHistograms', 'analyze'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])
    analyzer = Analyzer.Analyzer(
        NAME        = ARGS.NAME,
        SIGNALPOINT = Utilities.SignalPoint(ARGS.SIGNALPOINT),
        BRANCHKEYS  = ('DSAMUON', 'DIMUON'),
        TEST        = ARGS.TEST,
        SPLITTING   = ARGS.SPLITTING,
        FILE        = ARGS.FNAME
    )
    analyzer.writeHistograms('roots/DimuonPlots_{}.root')
