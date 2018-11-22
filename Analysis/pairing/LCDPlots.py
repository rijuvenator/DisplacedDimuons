import ROOT as R
import numpy as np
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedMuons, matchedDimuons

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

        # find matches for both pairs
        dmatches = []
        m0matches = []
        m1matches = []
        for i,genMuonPair in enumerate(genMuonPairs):
            dimuonMatches, muonMatches, exitcode = matchedDimuons(genMuonPair, selectedDimuons)
            if len(dimuonMatches) > 0:
                for match in dimuonMatches:
                    match['which'] = i
                for match in muonMatches[0]:
                    match['which'] = i
                for match in muonMatches[1]:
                    match['which'] = i
                dmatches.extend(dimuonMatches)
                m0matches.extend(muonMatches[0])
                m1matches.extend(muonMatches[1])

        # sort EVERYTHING by deltaR^2
        # remember: matches is [matches_pair0 ... matches_pair1], and matches_pair0, e.g. is a list of dimuonMatches
        # so a "column" of the table is matches_pair0 + matches_pair1. When they get sorted, the best ones
        # will float to the top, and the "which" will help remember which pair they came from
        if len(dmatches) > 0: # zip doesn't behave for zero length
            sortTable = zip(dmatches, m0matches, m1matches)
            sortTable.sort(key=lambda row:row[1]['deltaR']**2.+row[2]['deltaR'])
            dimuonMatches, muonMatches0, muonMatches1 = zip(*sortTable)
        else:
            sortTable = []
            dimuonMatches, muonMatches0, muonMatches1 = [], [], []

        # find the best two dimuon matches with non-overlapping muons
        realMatches = {}
        for dimuonMatch, muonMatch0, muonMatch1 in sortTable:
            # remember which pair
            which = dimuonMatch['which']
            # if there's nothing in realMatches, take this match
            if len(realMatches) == 0:
                realMatches[which] = dimuonMatch
            # there's already something in realMatches
            # if it's the same pair, keep going
            # okay, it's the other pair. Great. But make sure the other pair
            # has no muons in common with the pair that exists already (alreadyFound, alreadyIndices)
            # if it does, keep going
            # otherwise, bingo! we've found the other match. fill it and break.
            else:
                if which in realMatches: continue
                alreadyFound = realMatches[realMatches.keys()[0]]
                alreadyIndices = [alreadyFound['dim'].idx1, alreadyFound['dim'].idx2]
                if dimuonMatch['dim'].idx1 in alreadyIndices or dimuonMatch['dim'].idx2 in alreadyIndices: continue
                realMatches[which] = dimuonMatch
                break

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
    analyzer.writeHistograms('roots/LCDPlots{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else ''))
