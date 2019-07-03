import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedDimuons
import DisplacedDimuons.Analysis.Selector as Selector
import DisplacedDimuons.Analysis.PrimitivesPrinter as Printer

Printer.COLORON = True

#### CLASS AND FUNCTION DEFINITIONS ####
# setup function for Analyzer class
def begin(self, PARAMS=None):
    self.COUNTS = {float('inf'):0, 10.:0, 4.:0, 3.:0, 2.5:0, 2.:0}
    self.MATCH  = {float('inf'):0, 10.:0, 4.:0, 3.:0, 2.5:0, 2.:0}

# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    pass

# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    if self.TRIGGER and self.SP is not None:
        if not Selections.passedTrigger(E): return

    Event = E.getPrimitives('EVENT')

    # take 10% of data: event numbers ending in 7
    if 'DoubleMuon' in self.NAME:
        if Event.event % 10 != 7: return

    DSAmuons = E.getPrimitives('DSAMUON')
    PATmuons = E.getPrimitives('PATMUON')
    Dimuons3 = E.getPrimitives('DIMUON')

    eventWeight = 1.
    try:
        eventWeight = 1. if Event.weight > 0. else -1.
    except:
        pass

    selectedDimuons, selectedDSAmuons, selectedPATmuons = Selector.SelectObjects(E, self.CUTS, Dimuons3, DSAmuons, PATmuons)
    if selectedDimuons is None: return
    selectedDimuons = [dim for dim in selectedDimuons if dim.composition == 'DSA']

    def getOriginalMuons(dim):
        if dim.composition == 'PAT':
            return PATmuons[dim.idx1], PATmuons[dim.idx2]
        elif dim.composition == 'DSA':
            return DSAmuons[dim.idx1], DSAmuons[dim.idx2]
        else:
            return DSAmuons[dim.idx1], PATmuons[dim.idx2]

    for dim in selectedDimuons:
        mu1, mu2 = getOriginalMuons(dim)
        for val in self.COUNTS:
            if max(mu1.normChi2, mu2.normChi2) < val:
                self.COUNTS[val] += 1

    if len(selectedDimuons) == 0: return

    if '4Mu' in self.NAME:
        mu11, mu12, mu21, mu22, X1, X2, H, P, extramu = E.getPrimitives('GEN')
        genMuons = (mu11, mu12, mu21, mu22)
        genMuonPairs = ((mu11, mu12), (mu21, mu22))
    elif '2Mu2J' in self.NAME:
        mu1, mu2, j1, j2, X, XP, H, P, extramu = E.getPrimitives('GEN')
        genMuons = (mu1, mu2)
        genMuonPairs = ((mu1, mu2),)

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

    for pairIndex in realMatches:
        genMuon = genMuonPairs[pairIndex][0]
        dim = realMatches[pairIndex]['dim']

        for val in self.COUNTS:
            mu1, mu2 = getOriginalMuons(dim)
            if max(mu1.normChi2, mu2.normChi2) < val:
                self.MATCH[val] += 1

# cleanup function for Analyzer class
def end(self, PARAMS=None):
    data = []
    for dic in ('COUNTS', 'MATCH'):
        d = getattr(self, dic)
        for val in (float('inf'), 10., 4., 3., 2.5, 2.):
            data.append(d[val])
    print '{:4d} {:3d} {:4d} ::: {:5d} {:5d} {:5d} {:5d} {:5d} {:5d} ::: {:5d} {:5d} {:5d} {:5d} {:5d} {:5d}'.format(self.SP.mH, self.SP.mX, self.SP.cTau, *data)

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
        BRANCHKEYS  = ('DIMUON', 'PATMUON', 'DSAMUON', 'TRIGGER', 'GEN', 'EVENT', 'FILTER'),
    )
