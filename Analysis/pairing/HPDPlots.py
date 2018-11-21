import ROOT as R
import numpy as np
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedMuons, matchedDimuons

#### CLASS AND FUNCTION DEFINITIONS ####
# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    for key in ('All', 'Matched', 'Wrong', 'Right', 'Hopeless', 'Lost'):
        self.HistInit('pT_'+key, ';Refitted Muon p_{T} [GeV];Counts', 1500, 0., 1500.)

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

    Event   = E.getPrimitives('EVENT'  )
    dimuons = E.getPrimitives('DIMUON' )
    muons   = E.getPrimitives('DSAMUON')

    baseMuons    = [mu for mu in muons if mu.nDTStations+mu.nCSCStations>1 and mu.nCSCHits+mu.nDTHits>12 and mu.ptError/mu.pt<1.]
    baseOIndices = [mu.idx for mu in baseMuons]
    baseDimuons  = [dim for dim in dimuons if dim.idx1 in baseOIndices and dim.idx2 in baseOIndices]

    if len(baseDimuons) > 0:
        sortedMuons = sorted(baseMuons, key=lambda mu: mu.pt, reverse=True)
        bestTwo = (sortedMuons[0].idx, sortedMuons[1].idx)
        bestDimuon = None
        for dim in baseDimuons:
            if dim.idx1 in bestTwo and dim.idx2 in bestTwo:
                bestDimuon = dim
                break
        # Highest pT Dimuon (HPD) found
        if bestDimuon is not None:
            self.fillBoth('All', bestDimuon)

            # split HPD found into 3 pieces and 4 histograms:
            # - no matches (Hopeless)
            # - matches, and one of the matches is the HPD (Matched)
            # - matches, and none of the matches is the HPD (Wrong = HPD pT, Right = all matches' pT)
            dimuonMatches, muonMatches, exitcode = matchedDimuons(genMuonPairs[0], baseDimuons)
            if len(dimuonMatches) > 0:
                for match in dimuonMatches:
                    matchedDimuon = match['dim']
                    if matchedDimuon.idx1 == bestDimuon.idx1 and matchedDimuon.idx2 == bestDimuon.idx2:
                        self.fillBoth('Matched', bestDimuon)
                        break
                else:
                    self.fillBoth('Wrong', bestDimuon)
                    for match in dimuonMatches:
                        matchedDimuon = match['dim']
                        self.fillBoth('Right', matchedDimuon)
            else:
                self.fillBoth('Hopeless', bestDimuon)

        # HPD not found
        else:
            dimuonMatches, muonMatches, exitcode = matchedDimuons(genMuonPairs[0], baseDimuons)
            if len(dimuonMatches) > 0:
                for match in dimuonMatches:
                    matchedDimuon = match['dim']
                    self.fillBoth('Lost', matchedDimuon)

def fillBoth(self, tag, dim):
    self.HISTS['pT_'+tag].Fill(dim.mu1.pt)
    self.HISTS['pT_'+tag].Fill(dim.mu2.pt)

#### RUN ANALYSIS ####
if __name__ == '__main__':
    # get arguments
    ARGS = Analyzer.PARSER.parse_args()

    # set sample object based on arguments
    Analyzer.setSample(ARGS)

    # define Analyzer methods
    for METHOD in ('analyze', 'declareHistograms', 'fillBoth'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])

    # declare analyzer
    analyzer = Analyzer.Analyzer(
        ARGS        = ARGS,
        BRANCHKEYS  = ('DSAMUON', 'EVENT', 'GEN', 'DIMUON', 'TRIGGER'),
    )
    analyzer.writeHistograms('roots/HPDPlots{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else ''))
