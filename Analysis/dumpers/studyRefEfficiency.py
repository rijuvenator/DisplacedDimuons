import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedDimuons

#### CLASS AND FUNCTION DEFINITIONS ####
# setup function for Analyzer class
def begin(self, PARAMS=None):
    self.COUNTS = {'Den' : 0, 'None' : 0, 'One' : 0, 'Both' : 0, 'DSATotal' : 0, 'REFTotal' : 0}

# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    pass

# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    if self.SP is None:
        raise Exception('[ANALYZER ERROR]: This script runs on signal only.')
    if self.TRIGGER:
        if not Selections.passedTrigger(E): return
    if '4Mu' in self.NAME:
        mu11, mu12, mu21, mu22, X1, X2, H, P, extramu = E.getPrimitives('GEN')
        genMuons = (mu11, mu12, mu21, mu22)
        genMuonPairs = ((mu11, mu12), (mu21, mu22))
    elif '2Mu2J' in self.NAME:
        mu1, mu2, j1, j2, X, XP, H, P, extramu = E.getPrimitives('GEN')
        genMuons = (mu1, mu2)
        genMuonPairs = ((mu1, mu2),)
    DSAmuons = E.getPrimitives('DSAMUON')
    Dimuons  = E.getPrimitives('DIMUON')

    for genMuonPair in genMuonPairs:
        genMuonPairSelection = Selections.AcceptanceSelection(genMuonPair)
        if not genMuonPairSelection: continue
        if genMuonPair[0].Lxy() < 100.:
            self.COUNTS['Den'] += 1
            DSAdimuonMatches, DSAmuonMatches, DSAexitcode = matchedDimuons(genMuonPair, ('DUMMY',), DSAmuons, vertex='BS')
            REFdimuonMatches, REFmuonMatches, REFexitcode = matchedDimuons(genMuonPair, Dimuons)

            if DSAexitcode in (1, 2, 3):
                self.COUNTS['DSATotal'] += 2
            elif DSAexitcode in (4, 5, 6, 7):
                self.COUNTS['DSATotal'] += 1

            if len(REFdimuonMatches) > 0:
                self.COUNTS['REFTotal'] += 2

            if len(REFdimuonMatches) == 0:
                if DSAexitcode == 8:
                    self.COUNTS['None'] += 1
                elif DSAexitcode in (4, 5, 6, 7):
                    self.COUNTS['One'] += 1
                elif DSAexitcode in (1, 2, 3):
                    self.COUNTS['Both'] += 1

# cleanup function for Analyzer class
def end(self, PARAMS=None):
    print 'DATA', self.COUNTS

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
        BRANCHKEYS  = ('DIMUON', 'GEN', 'DSAMUON'),
    )
