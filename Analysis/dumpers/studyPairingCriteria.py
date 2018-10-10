import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedMuons, matchedDimuons

#### CLASS AND FUNCTION DEFINITIONS ####
# setup function for Analyzer class
def begin(self, PARAMS=None):
    self.TOTALS   = {
            'total'   : 0,
            'trigger' : 0,
            'nPairs'  : 0,
    }
    self.COUNTERS = {
            'all'   : { 'nPairs' : 0, 'nDimuons' : 0, 'nMatches' : 0, 'nCorrect' : 0},
            'loose' : { 'nPairs' : 0, 'nDimuons' : 0, 'nMatches' : 0, 'nCorrect' : 0},
    }

# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    self.HistInit('goodChi2', ';vtx #chi^{2}/dof;Counts', 100, 0., 20.)
    self.HistInit('badChi2' , ';vtx #chi^{2}/dof;Counts', 100, 0., 20.)

# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    if self.SP is None:
        raise Exception('[ANALYZER ERROR]: This script runs on signal only.')

    self.TOTALS['total'] += 1
    muons   = E.getPrimitives('DSAMUON')

    # apply trigger if --trigger
    # skip events without at least 2 muons with pT > 30
    if self.TRIGGER:
        if not Selections.passedTrigger(E): return

        self.TOTALS['trigger'] += 1

        numPT = 0
        for mu in muons:
            if mu.pt > 30:
                numPT += 1
            if numPT == 2:
                break
        if numPT < 2:
            return

    Event   = E.getPrimitives('EVENT'  )
    dimuons = E.getPrimitives('DIMUON' )

    if '4Mu' in self.NAME:
        mu11, mu12, mu21, mu22, X1, X2, H, P, extramu = E.getPrimitives('GEN')
        genMuons = (mu11, mu12, mu21, mu22)
        genMuonPairs = ((mu11, mu12), (mu21, mu22))
    elif '2Mu2J' in self.NAME:
        mu1, mu2, j1, j2, X, XP, H, P, extramu = E.getPrimitives('GEN')
        genMuons = (mu1, mu2)
        genMuonPairs = ((mu1, mu2),)

    # define a few selections
    muonSelections = {
        'all'   : [True for mu in muons],
        'loose' : [Selections.MuonSelection(mu, cutList='TestMuonCutList') for mu in muons],
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

    # loop over genMuonPairs, find dimuon, and do something based on result
    for genMuonPair in genMuonPairs:
        self.TOTALS['nPairs'] += 1

        for key in muonSelections:
            if len(selectedDimuons[key]) > 0:
                self.COUNTERS[key]['nDimuons'] += 1
                dimuonMatches, muonMatches, exitcode = matchedDimuons(genMuonPair, selectedDimuons[key], selectedMuons[key])
                if len(dimuonMatches) > 0:
                    self.COUNTERS[key]['nMatches'] += 1
                    sortedDimuons = sorted(selectedDimuons[key], key=lambda dim: dim.normChi2)
                    bestDimuon = sortedDimuons[0]
                    dimuon = dimuonMatches[0]['idx']
                    if bestDimuon.idx1 == dimuon.idx1 and bestDimuon.idx2 == dimuon.idx2:
                        self.COUNTERS[key]['nCorrect'] += 1
                        if key == 'loose':
                            self.HISTS['goodChi2'].Fill(bestDimuon.normChi2)
                    else:
                        if key == 'loose':
                            self.HISTS['badChi2'].Fill(bestDimuon.normChi2)

# cleanup function for Analyzer class
def end(self, PARAMS=None):
    print '[DATA] === {:<5s} {:4d} {:3d} {:4d} === Total {:5d} :: Trigger {:5d} ({:7.2%}) :: Pairs {:5d} ({:7.2%})'.format(
            '4Mu' if '4Mu' in self.NAME else '2Mu2J',
            self.SP.mH,
            self.SP.mX,
            self.SP.cTau,
                        self.TOTALS['total'],
                        self.TOTALS['trigger'],
            safePercent(self.TOTALS['trigger'], self.TOTALS['total']),
                        self.TOTALS['nPairs'],
            safePercent(self.TOTALS['nPairs'], self.TOTALS['trigger']),
    )
    for key in ('all', 'loose'):
        print '[DATA]  {:<5s} : {:5d} with dimuons ({:7.2%}); {:5d} matches ({:7.2%}) with {:5d} correct ({:7.2%})'.format(
            key,
                        self.COUNTERS[key]['nDimuons'],
            safePercent(self.COUNTERS[key]['nDimuons'], self.TOTALS['nPairs']),
                        self.COUNTERS[key]['nMatches'],
            safePercent(self.COUNTERS[key]['nMatches'], self.COUNTERS[key]['nDimuons']),
                        self.COUNTERS[key]['nCorrect'],
            safePercent(self.COUNTERS[key]['nCorrect'], self.COUNTERS[key]['nMatches']),
        )

def safePercent(a, b):
    if b != 0:
        return a/float(b)
    else:
        return 0.

#### RUN ANALYSIS ####
if __name__ == '__main__':
    # get arguments
    ARGS = Analyzer.PARSER.parse_args()

    # set sample object based on arguments
    Analyzer.setSample(ARGS)

    # define Analyzer methods
    for METHOD in ('begin', 'analyze', 'end', 'declareHistograms'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])

    # declare analyzer
    analyzer = Analyzer.Analyzer(
        ARGS        = ARGS,
        BRANCHKEYS  = ('DSAMUON', 'EVENT', 'GEN', 'DIMUON', 'TRIGGER'),
    )
    analyzer.writeHistograms('pairingCriteria{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else ''))
