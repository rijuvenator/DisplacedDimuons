import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedMuons, findDimuon

#### CLASS AND FUNCTION DEFINITIONS ####
# setup function for Analyzer class
def begin(self, PARAMS=None):
    self.COUNTERS = {
        'all'   : { 'nDimuon' : 0, 'nSuccess' : 0 , 'nFail' : 0, 'nFalse' : 0},
        'pT'    : { 'nDimuon' : 0, 'nSuccess' : 0 , 'nFail' : 0, 'nFalse' : 0},
#       'pT_MS' : { 'nDimuon' : 0, 'nSuccess' : 0 , 'nFail' : 0, 'nFalse' : 0},
    }

# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    if self.SP is None:
        raise Exception('[ANALYZER ERROR]: This script runs on signal only.')

    Event   = E.getPrimitives('EVENT'  )
    muons   = E.getPrimitives('DSAMUON')
    dimuons = E.getPrimitives('DIMUON' )
    if '4Mu' in self.NAME:
        mu11, mu12, mu21, mu22, X1, X2, H, P, extramu = E.getPrimitives('GEN')
        genMuons = (mu11, mu12, mu21, mu22)
        genMuonPairs = ((mu11, mu12), (mu21, mu22))
    elif '2Mu2J' in self.NAME:
        mu1, mu2, j1, j2, X, XP, H, P, extramu = E.getPrimitives('GEN')
        genMuons = (mu1, mu2)
        genMuonPairs = ((mu1, mu2),)

    muonSelections = {
        'all'   : [True for mu in muons],
        'pT'    : [Selections.MuonSelection(mu, cutList=('pT',)) for mu in muons],
#       'pT_MS' : [Selections.MuonSelection(mu, cutList=('pT','nStations')) for mu in muons]
    }

    selectedMuons = {}
    selectedDimuons = {}
    for key in muonSelections:
        if key == 'all':
            selectedMuons['all'] = muons
            selectedDimuons['all'] = dimuons
        else:
            selectedMuons[key] = [mu for idx,mu in enumerate(muons) if muonSelections[key][idx]]
            selectedDimuons[key] = [dim for idx,dim in enumerate(dimuons) if muonSelections[key][dim.idx1] and muonSelections[key][dim.idx2]]

    for genMuonPair in genMuonPairs:

        for key in muonSelections:
            dimuon, exitcode, muonMatches, oMuonMatches = findDimuon(genMuonPair, selectedMuons[key], selectedDimuons[key])
            if dimuon is not None:
                self.COUNTERS[key]['nDimuon'] += 1
                sortedDimuons = sorted(selectedDimuons[key], key=lambda dim: dim.normChi2)
                bestDimuon = sortedDimuons[0]
                if bestDimuon.idx1 == dimuon.idx1 and bestDimuon.idx2 == dimuon.idx2:
                    self.COUNTERS[key]['nSuccess'] += 1
            else:
                self.COUNTERS[key]['nFail'] += 1
                if len(selectedDimuons[key]) > 0:
                    self.COUNTERS[key]['nFalse'] += 1

# cleanup function for Analyzer class
def end(self, PARAMS=None):
    print '[DATA] === {:<5s} {:4d} {:3d} {:4d} ==='.format('4Mu' if '4Mu' in self.NAME else '2Mu2J', *self.SP.SP)
#   for key in ('all', 'pT', 'pT_MS'):
    for key in ('all', 'pT'):
        print '[DATA]  {:<5s} : {:5d} correct of {:5d} ({:5.2%}), {:5d} fails with {:5d} false'.format(
            key,
            self.COUNTERS[key]['nSuccess'],
            self.COUNTERS[key]['nDimuon'],
            self.COUNTERS[key]['nSuccess']/float(self.COUNTERS[key]['nDimuon']),
            self.COUNTERS[key]['nFail'],
            self.COUNTERS[key]['nFalse'],
    )

#### RUN ANALYSIS ####
if __name__ == '__main__':
    # get arguments
    ARGS = Analyzer.PARSER.parse_args()

    # set sample object based on arguments
    Analyzer.setSample(ARGS)

    # define Analyzer methods
    for METHOD in ('begin', 'analyze', 'end'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])

    # declare analyzer
    analyzer = Analyzer.Analyzer(
        ARGS        = ARGS,
        BRANCHKEYS  = ('DSAMUON', 'EVENT', 'GEN', 'DIMUON'),
    )
