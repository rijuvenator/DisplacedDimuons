import math
import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedMuons

#### CLASS AND FUNCTION DEFINITIONS ####
def begin(self, PARAMS=None):
    self.COUNTERS = {
        'nGenMuons' : 0,
        'nGenAcc'   : 0,
        'nMatches'  : 0,
        'nMultiple' : 0,
        'multiDict' : {},
    }

# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    if self.SP is None:
        raise Exception('[ANALYZER ERROR]: This script runs on signal only.')
    if '4Mu' in self.NAME:
        mu11, mu12, mu21, mu22, X1, X2, H, P = E.getPrimitives('GEN', 'HTo2XTo4Mu')
        genMuons = (mu11, mu12, mu21, mu22)
        genMuonPairs = ((mu11, mu12), (mu21, mu22))
    elif '2Mu2J' in self.NAME:
        mu1, mu2, j1, j2, X, XP, H, P = E.getPrimitives('GEN', 'HTo2XTo2Mu2J')
        genMuons = (mu1, mu2)
        genMuonPairs = ((mu1, mu2),)
    DSAmuons = E.getPrimitives('DSAMUON')

    SelectMuons   = False
    # require muons to pass all selections
    if SelectMuons:
        DSASelections    = [Selections.MuonSelection  (muon)   for muon   in DSAmuons]

        selectedDSAmuons = [mu  for idx,mu  in enumerate(DSAmuons) if DSASelections   [idx]]

    # don't require muons to pass all selections
    else:
        selectedDSAmuons = DSAmuons

    # loop over genMuons and count various matching criteria
    for genMuon in genMuons:

        self.COUNTERS['nGenMuons'] += 1

        if Selections.AcceptanceSelection(genMuon):
            self.COUNTERS['nGenAcc'] += 1

        matches = matchedMuons(genMuon, selectedDSAmuons)
        if len(matches) != 0:
            self.COUNTERS['nMatches'] += 1

            if len(matches) > 1:
                self.COUNTERS['nMultiple'] += 1
                if len(matches) not in self.COUNTERS['multiDict']:
                    self.COUNTERS['multiDict'][len(matches)] = 0
                self.COUNTERS['multiDict'][len(matches)] += 1

# dump info
def end(self, PARAMS=None):
    fstring = 'DATA: {:4d} {:3d} {:4d} {:5s} {:6d} {:6d} {:6d} {:6d} '
    multiDictCounts = []
    for i in xrange(max(self.COUNTERS['multiDict'].keys())-1):
        fstring += '{:6d} '
        try:
            multiDictCounts.append(self.COUNTERS['multiDict'][i+2])
        except:
            multiDictCounts.append(0)

    print fstring.format(
        self.SP.mH,
        self.SP.mX,
        self.SP.cTau,
        '4Mu' if '4Mu' in self.NAME else '2Mu2J',
        self.COUNTERS['nGenMuons'],
        self.COUNTERS['nGenAcc'  ],
        self.COUNTERS['nMatches' ],
        self.COUNTERS['nMultiple'],
        *multiDictCounts
    )

#### RUN ANALYSIS ####
if __name__ == '__main__':
    ARGS = Analyzer.PARSER.parse_args()
    Analyzer.setFNAME(ARGS)
    for METHOD in ('begin', 'analyze', 'end'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])
    analyzer = Analyzer.Analyzer(
        NAME        = ARGS.NAME,
        SIGNALPOINT = Utilities.SignalPoint(ARGS.SIGNALPOINT),
        BRANCHKEYS  = ('GEN', 'DSAMUON'),
        TEST        = ARGS.TEST,
        SPLITTING   = ARGS.SPLITTING,
        FILE        = ARGS.FNAME
    )
