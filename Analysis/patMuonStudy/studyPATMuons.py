import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedDimuons, matchedTrigger, applyPairingCriteria

#### CLASS AND FUNCTION DEFINITIONS ####
# setup function for Analyzer class
def begin(self, PARAMS=None):
    pass

# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    pass

# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    # get dimuons
    DSAmuons = E.getPrimitives('DSAMUON')
    PATmuons = E.getPrimitives('PATMUON')
    Dimuons  = E.getPrimitives('DIMUON')
    Event    = E.getPrimitives('EVENT')

    if self.SP is not None:
        if '4Mu' in self.NAME:
            mu11, mu12, mu21, mu22, X1, X2, H, P, extramu = E.getPrimitives('GEN')
            genMuons = (mu11, mu12, mu21, mu22)
            genMuonPairs = ((mu11, mu12), (mu21, mu22))
        elif '2Mu2J' in self.NAME:
            mu1, mu2, j1, j2, X, XP, H, P, extramu = E.getPrimitives('GEN')
            genMuons = (mu1, mu2)
            genMuonPairs = ((mu1, mu2),)


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
        for dimuon in [d for d in Dimuons if sum(d.ID) < 999]:
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
            selectedDimuons  = [dim for dim in Dimuons if dim.idx1 in selectedOIndices and dim.idx2 in selectedOIndices and sum(dim.ID) < 999]

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

    #print '==== EVENT ===='
    #for dim in Dimuons:
    #    print '  ', dim.ID
    #print '==============='

    # loop over dimuons and fill if they pass their selection
    for dimuon in selectedDimuons:
        idx_PM = {1:None, 2:None}
        idx_SM = {1:None, 2:None}
        for num in (1, 2):
            if DSAmuons[getattr(dimuon, 'mu'+str(num)).idx].idx_ProxMatch is not None:
                idx_PM[num] = DSAmuons[getattr(dimuon, 'mu'+str(num)).idx].idx_ProxMatch
            if DSAmuons[getattr(dimuon, 'mu'+str(num)).idx].idx_SegMatch is not None:
                idx_SM[num] = DSAmuons[getattr(dimuon, 'mu'+str(num)).idx].idx_SegMatch

        #print 'Dimuon ({}, {}) prox matched ({}, {}) and seg matched ({}, {})'.format(
        #        dimuon.idx1,
        #        dimuon.idx2,
        #        idx_PM[1],
        #        idx_PM[2],
        #        idx_SM[1],
        #        idx_SM[2],
        #)
        if dimuon.idx1 == 3 and dimuon.idx2 == 4 and idx_PM[1] == 2 and idx_PM[2] == 0 and idx_SM[1] == 2 and idx_SM[2] == 0:
            print Event
            print 'Dimuon ({}, {}) prox matched ({}, {}) and seg matched ({}, {})'.format(
                    dimuon.idx1,
                    dimuon.idx2,
                    idx_PM[1],
                    idx_PM[2],
                    idx_SM[1],
                    idx_SM[2],
            )
            print genMuons[0]
            print genMuons[1]
            print dimuon
            print DSAmuons[3]
            print DSAmuons[4]
            print PATmuons[2]
            print PATmuons[0]
            for d in Dimuons:
                if 1002 in d.ID and 1000 in d.ID:
                    print d
            return


# cleanup function for Analyzer class
def end(self, PARAMS=None):
    pass

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
#   analyzer.writeHistograms('roots/test{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else ''))
