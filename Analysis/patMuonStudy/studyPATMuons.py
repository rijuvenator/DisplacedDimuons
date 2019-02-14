import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedDimuons, matchedTrigger, applyPairingCriteria, replaceDSADimuons

QUANTITIES = {
    'Lxy'     : {'AXES':(1000,      0., 800.   ), 'LAMBDA': lambda dim: dim.Lxy()                         , 'PRETTY':'L_{xy} [cm]'           },
    'LxySig'  : {'AXES':(8000,      0., 2000.  ), 'LAMBDA': lambda dim: dim.LxySig()                      , 'PRETTY':'L_{xy}/#sigma_{L_{xy}}'},
    'LxyErr'  : {'AXES':(1000,      0., 100.   ), 'LAMBDA': lambda dim: dim.LxyErr()                      , 'PRETTY':'#sigma_{L_{xy}} [cm]'  },
    'vtxChi2' : {'AXES':(1000,      0., 50.    ), 'LAMBDA': lambda dim: dim.normChi2                      , 'PRETTY':'vtx #chi^{2}/dof'      },
}

CONFIG = {
    'DSA-LxySig'  : {'QKEY':'LxySig' },
    'DSA-LxyErr'  : {'QKEY':'LxyErr' },
    'DSA-vtxChi2' : {'QKEY':'vtxChi2'},
    'PAT-LxySig'  : {'QKEY':'LxySig' },
    'PAT-LxyErr'  : {'QKEY':'LxyErr' },
    'PAT-vtxChi2' : {'QKEY':'vtxChi2'},
}

#### CLASS AND FUNCTION DEFINITIONS ####
# setup function for Analyzer class
def begin(self, PARAMS=None):
    self.COUNTS = {'selected':0, 'replaced':0}

# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    for KEY in CONFIG:
        XTIT = QUANTITIES[CONFIG[KEY]['QKEY']]['PRETTY']
        self.HistInit(KEY, ';'+XTIT+';Counts', *QUANTITIES[CONFIG[KEY]['QKEY']]['AXES'])

# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    if self.TRIGGER and self.SP is not None:
        if not Selections.passedTrigger(E): return
    DSAmuons = E.getPrimitives('DSAMUON')
    PATmuons = E.getPrimitives('PATMUON')
    Dimuons3 = E.getPrimitives('DIMUON')
    Event    = E.getPrimitives('EVENT')

    Dimuons = [dim for dim in Dimuons3 if sum(dim.ID) < 999]

    if self.SP is not None:
        if '4Mu' in self.NAME:
            mu11, mu12, mu21, mu22, X1, X2, H, P, extramu = E.getPrimitives('GEN')
            genMuons = (mu11, mu12, mu21, mu22)
            genMuonPairs = ((mu11, mu12), (mu21, mu22))
        elif '2Mu2J' in self.NAME:
            mu1, mu2, j1, j2, X, XP, H, P, extramu = E.getPrimitives('GEN')
            genMuons = (mu1, mu2)
            genMuonPairs = ((mu1, mu2),)

    eventWeight = 1.
    try:
        eventWeight = 1. if Event.weight > 0. else -1.
    except:
        pass

    # decide what set of cuts to apply based on self.CUTS cut string
    ALL       = 'All'       in self.CUTS
    PROMPT    = '_Prompt'   in self.CUTS
    NOPROMPT  = '_NoPrompt' in self.CUTS
    NSTATIONS = '_NS'       in self.CUTS
    NMUONHITS = '_NH'       in self.CUTS
    FPTERR    = '_FPTE'     in self.CUTS
    PT        = '_PT'       in self.CUTS
    HLT       = '_HLT'      in self.CUTS
    PC        = '_PC'       in self.CUTS
    LXYERR    = '_LXYE'     in self.CUTS
    MASS      = '_M'        in self.CUTS

    def boolsToMuonCutList(NSTATIONS, NMUONHITS, FPTERR, PT):
        cutList = []
        if NSTATIONS:
            cutList.append('b_nStations')
        if NMUONHITS:
            cutList.append('b_nMuonHits')
        if FPTERR:
            cutList.append('b_FPTE')
        if PT:
            cutList.append('b_pT')
        return cutList

    def boolsToDimuonCutList(LXYERR, MASS):
        cutList = []
        if LXYERR:
            cutList.append('b_LxyErr')
        if MASS:
            cutList.append('b_mass')
        return cutList

    # require DSA muons to pass all selections, and require dimuons to pass all selections except LxySig and deltaPhi
    if ALL:
        DSASelections    = [Selections.MuonSelection(muon) for muon in DSAmuons]
        DimuonSelections = [Selections.DimuonSelection(dimuon) for dimuon in Dimuons ]
        selectedDSAmuons = [mu for idx,mu in enumerate(DSAmuons) if DSASelections[idx]]
        selectedDimuons  = [dim for idx,dim in enumerate(Dimuons) if DimuonSelections[idx].allExcept('LxySig', 'deltaPhi') and DSASelections[dim.idx1] and DSASelections[dim.idx2]]

    # no cuts
    else:
        selectedDSAmuons = DSAmuons
        selectedDimuons  = Dimuons

    # for PROMPT and NOPROMPT event selections
    if PROMPT or NOPROMPT:
        highLxySigExists = False
        for dimuon in Dimuons:
            if dimuon.LxySig() > 3.:
                highLxySigExists = True
                break

        # return if there are LxySig > 3
        if PROMPT:
            if highLxySigExists:
                return
        # return if there are NO LxySig > 3 -- that's category 1
        elif NOPROMPT:
            if not highLxySigExists:
                return

    if PROMPT or NOPROMPT:
        # compute all the baseline selection booleans
        DSASelections = [Selections.MuonSelection(muon, cutList='BaselineMuonCutList') for muon in DSAmuons]

        # figure out which cuts we actually care about
        cutList = boolsToMuonCutList(NSTATIONS, NMUONHITS, FPTERR, PT)

        # no selection
        if len(cutList) == 0:
            selectedDSAmuons = DSAmuons
            selectedDimuons  = Dimuons
        # cutList is some nonzero list, meaning keep only the muons that pass the cut keys in cutList
        else:
            selectedDSAmuons = [mu for i,mu in enumerate(DSAmuons) if DSASelections[i].allOf(*cutList)]
            selectedOIndices = [mu.idx for mu in selectedDSAmuons]
            selectedDimuons  = [dim for dim in Dimuons if dim.idx1 in selectedOIndices and dim.idx2 in selectedOIndices]

    # apply HLT RECO matching
    if HLT:
        HLTPaths, HLTMuons, L1TMuons = E.getPrimitives('TRIGGER')
        DSAMuonsForHLTMatch = [mu for mu in selectedDSAmuons if abs(mu.eta) < 2.]
        HLTMuonMatches = matchedTrigger(HLTMuons, DSAMuonsForHLTMatch)
        if not any([HLTMuonMatches[ij]['matchFound'] for ij in HLTMuonMatches]): return

    # apply pairing criteria and transform selectedDimuons
    if PC:
        selectedDimuons = applyPairingCriteria(selectedDSAmuons, selectedDimuons)

    if PROMPT or NOPROMPT:
        # compute all the baseline selection booleans
        DimuonSelections = {dim.ID:Selections.DimuonSelection(dim, cutList='BaselineDimuonCutList') for dim in selectedDimuons}

        # figure out which cuts we actually care about
        cutList = boolsToDimuonCutList(LXYERR, MASS)

        # cutList is some nonzero list, meaning keep only the muons that pass the cut keys in cutList
        if len(cutList) > 0:
            selectedDimuons = [dim for dim in selectedDimuons if DimuonSelections[dim.ID].allOf(*cutList)]

    # for the MC/Data events, skip events with no dimuons, but not for "no selection"
    if (PROMPT or NOPROMPT) and NSTATIONS:
        if len(selectedDimuons) == 0: return

    # also filter selectedDSAmuons to only be of those indices that are in the final dimuons
    if PROMPT or NOPROMPT:
        selectedOIndices = []
        for dim in selectedDimuons:
            selectedOIndices.append(dim.idx1)
            selectedOIndices.append(dim.idx2)
        selectedOIndices = list(set(selectedOIndices))
        selectedDSAmuons = [mu for mu in selectedDSAmuons if mu.idx in selectedOIndices]

    selectedIDs = [dim.ID for dim in selectedDimuons]
    replacedDimuons, wasReplaced = replaceDSADimuons(Dimuons3, DSAmuons, mode='PAT')
    replacedIDs = [dim.ID for dim,isReplaced in zip(Dimuons,wasReplaced) if isReplaced]

    for KEY in CONFIG:
        QKEY = KEY[4:]
        if 'DSA' in KEY:
            for dim in selectedDimuons:
                self.HISTS[KEY].Fill(QUANTITIES[QKEY]['LAMBDA'](dim))
        else:
            for dim, rdim, wasrep in zip(Dimuons, replacedDimuons, wasReplaced):
                if dim.ID in selectedIDs and wasrep:
                    self.HISTS[KEY].Fill(QUANTITIES[QKEY]['LAMBDA'](rdim))

    self.COUNTS['selected'] += len(selectedIDs)
    self.COUNTS['replaced'] += len([ID for ID in selectedIDs if ID in replacedIDs])


# cleanup function for Analyzer class
def end(self, PARAMS=None):
    print '{:5s} {:4d} {:3d} {:4d} {:5d} {:5d} {:7.4f}'.format('4Mu' if '4Mu' in self.NAME else '2Mu2J', self.SP.mH, self.SP.mX, self.SP.cTau, self.COUNTS['selected'], self.COUNTS['replaced'], self.COUNTS['replaced']/float(self.COUNTS['selected'])*100.)

#### RUN ANALYSIS ####
if __name__ == '__main__':
    # get arguments
    ARGS = Analyzer.PARSER.parse_args()

    # set sample object based on arguments
    Analyzer.setSample(ARGS)

    # define Analyzer methods
    for METHOD in ('begin', 'declareHistograms', 'analyze', 'end'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])

    # declare analyzer
    analyzer = Analyzer.Analyzer(
        ARGS        = ARGS,
        BRANCHKEYS  = ('DIMUON', 'PATMUON', 'DSAMUON', 'TRIGGER', 'GEN', 'EVENT'),
    )

    # write plots
    analyzer.writeHistograms('roots/PATMuonStudyPlots{}{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else '', ARGS.CUTS))
