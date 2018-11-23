import ROOT as R
import numpy as np
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedMuons, matchedDimuons, matchedDimuonPairs

#### CLASS AND FUNCTION DEFINITIONS ####
# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    for key in ('All', 'Matched', 'NotMatched'):
        self.HistInit('Lxy_'+key, ';gen dimuon L_{xy} [cm];Counts', 800, 0., 800.)

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

    if ARGS.CUTS == '_HPD':
        sortedMuons = sorted(baseMuons, key=lambda mu: mu.pt, reverse=True)
        if len(sortedMuons) > 4:
            highestPTMuons = sortedMuons[:4]
        else:
            highestPTMuons = sortedMuons
        highestIndices = [mu.idx for mu in highestPTMuons]
        selectedDimuons = [dim for dim in baseDimuons if dim.idx1 in highestIndices and dim.idx2 in highestIndices]
    else:
        selectedDimuons = baseDimuons

    if len(selectedDimuons) > 0:

        # sort dimuons by chi^2, get best <=2, and their "IDs"
        sortedDimuons = sorted(selectedDimuons, key=lambda dim: dim.normChi2)
        lowestChi2Dimuons = []
        for dim in sortedDimuons:
            if len(lowestChi2Dimuons) == 0:
                lowestChi2Dimuons.append(dim)
            else:
                alreadyLow = lowestChi2Dimuons[0]
                alreadyID  = (alreadyLow.idx1, alreadyLow.idx2)
                if dim.idx1 in alreadyID or dim.idx2 in alreadyID: continue
                lowestChi2Dimuons.append(dim)
                break
        #bestDimuonIDs_Chi2 = {(d.idx1, d.idx2):d for d in lowestChi2Dimuons}
        bestDimuonIDs_Chi2 = [(d.idx1, d.idx2) for d in lowestChi2Dimuons]

        # find best non-overlapping matches for both pairs
        realMatches, dimuonMatches, muon0Matches, muon1Matches = matchedDimuonPairs(genMuonPairs, selectedDimuons)

        # realMatches has 0-2 elements
        MSDIDs = [(m['dim'].idx1, m['dim'].idx2) for w,m in realMatches.iteritems()]

        for i,ID in enumerate(MSDIDs):
            q = genMuonPairs[i][0].Lxy()
            self.HISTS['Lxy_All'].Fill(q)
            if ID in bestDimuonIDs_Chi2:
                self.HISTS['Lxy_Matched'].Fill(q)
            else:
                self.HISTS['Lxy_NotMatched'].Fill(q)


#### RUN ANALYSIS ####
if __name__ == '__main__':
    # get arguments
    ARGS = Analyzer.PARSER.parse_args()

    # set sample object based on arguments
    Analyzer.setSample(ARGS)

    # define Analyzer methods
    for METHOD in ('analyze', 'declareHistograms'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])

    # declare analyzer
    analyzer = Analyzer.Analyzer(
        ARGS        = ARGS,
        BRANCHKEYS  = ('DSAMUON', 'EVENT', 'GEN', 'DIMUON', 'TRIGGER'),
    )
    analyzer.writeHistograms('roots/LCDPlots{}{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else '', ARGS.CUTS))
