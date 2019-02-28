import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedDimuons, matchedTrigger, applyPairingCriteria, replaceDSADimuons
import DisplacedDimuons.Analysis.Selector as Selector

#### CLASS AND FUNCTION DEFINITIONS ####
# setup function for Analyzer class
def begin(self, PARAMS=None):
    self.COUNTS = {'huzzah':0, 'hybfound':0, 'hybnot':0, 'nomatch':0, 'bothmatch':0, 'failedDim':0, 'failedPT':0, 'failedLxyE':0, 'failedM':0, 'failedMatch':0, 'recovered':0}

# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    pass

# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    if self.TRIGGER and self.SP is not None:
        if not Selections.passedTrigger(E): return
    DSAmuons = E.getPrimitives('DSAMUON')
    PATmuons = E.getPrimitives('PATMUON')
    Dimuons3 = E.getPrimitives('DIMUON')
    Event    = E.getPrimitives('EVENT')

    eventWeight = 1.
    try:
        eventWeight = 1. if Event.weight > 0. else -1.
    except:
        pass

    selectedDimuonsOld, selectedDSAmuonsOld = Selector.SelectObjects(E, self.CUTS, [dim for dim in Dimuons3 if dim.composition == 'DSA'], DSAmuons)
    if selectedDimuonsOld is None: return

    selectedDimuons, selectedDSAmuons, selectedPATmuons = Selector.SelectObjectsReordered(E, self.CUTS, Dimuons3, DSAmuons, PATmuons)

    selectedDimuonsHyb, selectedDSAmuonsHyb, selectedPATmuonsHyb = Selector.SelectObjectsReordered(E, self.CUTS, Dimuons3, DSAmuons, PATmuons, keepHybrids=True, option=ARGS.PCOPTION)

    if self.SP is not None:
        if '4Mu' in self.NAME:
            mu11, mu12, mu21, mu22, X1, X2, H, P, extramu = E.getPrimitives('GEN')
            genMuons = (mu11, mu12, mu21, mu22)
            genMuonPairs = ((mu11, mu12), (mu21, mu22))
        elif '2Mu2J' in self.NAME:
            mu1, mu2, j1, j2, X, XP, H, P, extramu = E.getPrimitives('GEN')
            genMuons = (mu1, mu2)
            genMuonPairs = ((mu1, mu2),)

        realMatches = {}
        if selectedDimuons is not None:
            # do the signal matching
            if len(genMuonPairs) == 1:
                genMuonPair = genMuonPairs[0]
                dimuonMatches, muonMatches, exitcode = matchedDimuons(genMuonPair, selectedDimuons)
                if len(dimuonMatches) > 0:
                    realMatches = {0:dimuonMatches[0]}
                else:
                    realMatches = {}
            else:
                realMatches, dimuonMatches, muon0Matches, muon1Matches = matchedDimuonPairs(genMuonPairs, selectedDimuons)

        if len(realMatches) == 0:
            if len(genMuonPairs) == 1:
                genMuonPair = genMuonPairs[0]
                dimuonMatches, muonMatches, exitcode = matchedDimuons(genMuonPair, selectedDimuonsOld)
                if len(dimuonMatches) > 0:
                    realMatchesOld = {0:dimuonMatches[0]}
                else:
                    realMatchesOld = {}
            else:
                realMatchesOld, dimuonMatches, muon0Matches, muon1Matches = matchedDimuonPairs(genMuonPairs, selectedDimuonsOld)

            if len(realMatchesOld) > 0:
                # huzzah!
                self.COUNTS['huzzah'] += 1
                HybridDimuons = [dim for dim in Dimuons3 if dim.composition == 'HYBRID']
                HybridIDs = [dim.ID for dim in HybridDimuons]

                # defines a SegMatch, returns a pair of indices (called candidate)
                def lookForSegMatch(DSAmuon):
                    candidate = None
                    if DSAmuon.idx_SegMatch is None:
                        pass
                    elif len(DSAmuon.idx_SegMatch) > 1:
                        if DSAmuon.idx_ProxMatch in DSAmuon.idx_SegMatch:
                            candidate = DSAmuon.idx_ProxMatch
                        else:
                            # take first entry
                            # which is the smallest index = largest pT
                            candidate = DSAmuon.idx_SegMatch[0]
                    else:
                        candidate = DSAmuon.idx_SegMatch[0]
                    return candidate

                # check whether the DSA dimuons have hybrid replacements
                for dim in selectedDimuonsOld:
                    candidates = map(lookForSegMatch, (DSAmuons[dim.idx1], DSAmuons[dim.idx2]))

                    if candidates.count(None) == 1:
                        PATIndex = candidates[0] if candidates[0] is not None else candidates[1]
                        DSAIndex = dim.idx2      if candidates[1] is     None else dim.idx1
                        testID = (DSAIndex, PATIndex)
                        if testID in HybridIDs:
                            self.COUNTS['hybfound'] += 1
                        else:
                            self.COUNTS['hybnot'] += 1
                    elif candidates.count(None) == 2:
                        self.COUNTS['nomatch'] += 1
                    elif candidates.count(None) == 0:
                        self.COUNTS['bothmatch'] += 1
                        PATDim = None
                        for pd in Dimuons3:
                            if pd.composition == 'PAT' and set(candidates).issubset(pd.ID):
                                PATDim = pd
                                break
                        if PATDim is None:
                            self.COUNTS['failedDim'] += 1
                            continue
                        elif PATmuons[PATDim.idx1].pt < 10. or PATmuons[PATDim.idx2].pt < 10.:
                            self.COUNTS['failedPT'] += 1
                            continue
                        elif PATDim.LxyErr() > 99.:
                            self.COUNTS['failedLxyE'] += 1
                            continue
                        elif PATDim.mass < 5.:
                            self.COUNTS['failedM'] += 1
                            continue
                        else:
                            self.COUNTS['failedMatch'] += 1
                    else:
                        print 'What?'

                # see if gen muons matched with hybrid selection
                if selectedDimuonsHyb is not None:
                    if len(genMuonPairs) == 1:
                        genMuonPair = genMuonPairs[0]
                        dimuonMatches, muonMatches, exitcode = matchedDimuons(genMuonPair, selectedDimuonsHyb)
                        if len(dimuonMatches) > 0:
                            realMatchesHyb = {0:dimuonMatches[0]}
                        else:
                            realMatchesHyb = {}
                    else:
                        realMatchesHyb, dimuonMatches, muon0Matches, muon1Matches = matchedDimuonPairs(genMuonPairs, selectedDimuonsHyb)

                    if len(realMatchesHyb) > 0:
                        self.COUNTS['recovered'] += 1

# cleanup function for Analyzer class
def end(self, PARAMS=None):
    if self.SP is not None:
        print '{:5s} {:4d} {:3d} {:4d}'.format('4Mu' if '4Mu' in self.NAME else '2Mu2J', self.SP.mH, self.SP.mX, self.SP.cTau),
    else:
        print '{:s}'.format(self.NAME),
    print '{huzzah:5d} {hybfound:5d} {hybnot:5d} {nomatch:5d} {bothmatch:5d} {failedDim:5d} {failedPT:5d} {failedLxyE:5d} {failedM:5d} {failedMatch:5d} {recovered:5d}'.format(**self.COUNTS)

#### RUN ANALYSIS ####
if __name__ == '__main__':
    Analyzer.PARSER.add_argument('--pcoption', dest='PCOPTION', type=int, default=1)
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
