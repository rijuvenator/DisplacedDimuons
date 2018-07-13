import math
import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import findDimuon

# CONFIG stores the axis and function information so that histograms can be filled and declared in a loop
CONFIG = {
    'pT'      : {'AXES':( 0., 500.   ), 'LAMBDA': lambda dimuon: dimuon.pt      , 'PRETTY':'p_{T} [GeV]'    },
    'eta'     : {'AXES':(-3., 3.     ), 'LAMBDA': lambda dimuon: dimuon.eta     , 'PRETTY':None             },
    'Lxy'     : {'AXES':( 0., 800.   ), 'LAMBDA': lambda dimuon: dimuon.Lxy()   , 'PRETTY':'L_{xy} [cm]'    },
    'LxySig'  : {'AXES':( 0., 20.    ), 'LAMBDA': lambda dimuon: dimuon.LxySig(), 'PRETTY':None             },
    'vtxChi2' : {'AXES':( 0., 5.     ), 'LAMBDA': lambda dimuon: dimuon.normChi2, 'PRETTY':None             },
    'deltaR'  : {'AXES':( 0., 5.     ), 'LAMBDA': lambda dimuon: dimuon.deltaR  , 'PRETTY':'#DeltaR(#mu#mu)'},
    'mass'    : {'AXES':( 0., 500.   ), 'LAMBDA': lambda dimuon: dimuon.mass    , 'PRETTY':'M(#mu#mu) [GeV]'},
    'deltaPhi': {'AXES':( 0., math.pi), 'LAMBDA': lambda dimuon: dimuon.deltaPhi, 'PRETTY':None             },
    'cosAlpha': {'AXES':(-1., 1.     ), 'LAMBDA': lambda dimuon: dimuon.cosAlpha, 'PRETTY':None             },
}

#### CLASS AND FUNCTION DEFINITIONS ####
# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    for KEY in CONFIG:

        # the pretty strings are mostly in the cut dictionary
        # so use it if it's None
        # but use the string given if not
        XTIT = Selections.PrettyTitles[KEY] if CONFIG[KEY]['PRETTY'] is None else CONFIG[KEY]['PRETTY']

        if True:
            self.HistInit('Dim_'+KEY           , ';'+XTIT+';Counts', 1000, *CONFIG[KEY]['AXES'])

        if self.SP is not None:
            self.HistInit('Dim_'+KEY+'_Matched', ';'+XTIT+';Counts', 1000, *CONFIG[KEY]['AXES'])

    # make LxySig vs Lxy
    TITLE = ';' + CONFIG['Lxy']['PRETTY'] + ';' + Selections.PrettyTitles['LxySig'] + ';Counts'
    AXES  = (1000,) + CONFIG['Lxy']['AXES'] + (1000,) + (CONFIG['LxySig']['AXES'])
    if True:
        self.HistInit('Dim_LxySigVSLxy'        , TITLE, *AXES)

    if self.SP is not None:
        self.HistInit('Dim_LxySigVSLxy_Matched', TITLE, *AXES)

# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    Event    = E.getPrimitives('EVENT'  )
    DSAmuons = E.getPrimitives('DSAMUON')
    Dimuons  = E.getPrimitives('DIMUON' )

    eventWeight = 1.
    try:
        eventWeight = 1. if Event.weight > 0. else -1.
    except:
        pass

    # modify this to determine what type of selections to apply, if any
    SelectDimuons = False
    SelectMuons   = False

    # require dimuons to pass all selections and the DSA muons to pass all selections
    if SelectDimuons and SelectMuons:
        DSASelections    = [Selections.MuonSelection(muon) for muon in DSAmuons]
        DimuonSelections = [Selections.DimuonSelection(dimuon) for dimuon in Dimuons ]
        selectedDimuons  = [dim for idx,dim in enumerate(Dimuons) if DimuonSelections[idx] and DSASelections[dim.idx1] and DSASelections[dim.idx2]]

    # don't require dimuons to pass all selections, but require DSA muons to pass all selections
    elif not SelectDimuons and SelectMuons:
        DSASelections   = [Selections.MuonSelection(muon) for muon in DSAmuons]
        selectedDimuons = [dim for idx,dim in enumerate(Dimuons) if DSASelections[dim.idx1] and DSASelections[dim.idx2]]

    # don't require dimuons to pass all selections, and don't require DSA muons to pass all selections, either
    elif not SelectDimuons and not SelectMuons:
        selectedDimuons = Dimuons

    # fill histograms for every dimuon
    for dimuon in selectedDimuons:
        for KEY in CONFIG:
            self.HISTS['Dim_'+KEY].Fill(CONFIG[KEY]['LAMBDA'](dimuon), eventWeight)

        self.HISTS['Dim_LxySigVSLxy'].Fill(CONFIG['Lxy']['LAMBDA'](dimuon), CONFIG['LxySig']['LAMBDA'](dimuon), eventWeight)

    # get gen particles if this is a signal sample
    if self.SP is not None:
        if '4Mu' in self.NAME:
            mu11, mu12, mu21, mu22, X1, X2, H, P, extramu = E.getPrimitives('GEN')
            genMuons = (mu11, mu12, mu21, mu22)
            genMuonPairs = ((mu11, mu12), (mu21, mu22))
        elif '2Mu2J' in self.NAME:
            mu1, mu2, j1, j2, X, XP, H, P, extramu = E.getPrimitives('GEN')
            genMuons = (mu1, mu2)
            genMuonPairs = ((mu1, mu2),)

        # fill histograms only for matched reco muons
        for genMuonPair in genMuonPairs:
            # require genMuonPair to be within acceptance
            # don't do it for now
            #genMuonSelection = Selections.AcceptanceSelection(genMuonPair)

            # find the matching dimuon, if any, and fill
            dimuon, exitcode, muonMatches = findDimuon(genMuonPair, DSAmuons, Dimuons)

            if dimuon is not None:
                for KEY in CONFIG:
                    self.HISTS['Dim_'+KEY+'_Matched'].Fill(CONFIG[KEY]['LAMBDA'](dimuon), eventWeight)
                self.HISTS['Dim_LxySigVSLxy_Matched'].Fill(CONFIG['Lxy']['LAMBDA'](dimuon), CONFIG['LxySig']['LAMBDA'](dimuon), eventWeight)

#### RUN ANALYSIS ####
if __name__ == '__main__':
    ARGS = Analyzer.PARSER.parse_args()
    Analyzer.setSample(ARGS)
    for METHOD in ('declareHistograms', 'analyze'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])
    analyzer = Analyzer.Analyzer(
        ARGS        = ARGS,
        BRANCHKEYS  = ('EVENT', 'GEN', 'DSAMUON', 'DIMUON'),
    )
    analyzer.writeHistograms('roots/DimuonPlots_{}.root')
