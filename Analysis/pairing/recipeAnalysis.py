import ROOT as R
import numpy as np
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedMuons, matchedDimuons, matchedDimuonPairs

PTCUTS = list(range(41))

def nToStr(n):
    if   n >= 4: return '4'
    elif n == 3: return '3'
    elif n == 2: return '2'
    else       : return None

#### CLASS AND FUNCTION DEFINITIONS ####
# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    for nMuons in ('All', '2', '3', '4'):
        for quantity in ('Triggers', 'Events', 'Matches', 'Correct'):
            key = 'n'+quantity+'_'+nMuons
            self.HistInit(key, ';p_{T} Cut [GeV];Counts', len(PTCUTS), 0., float(len(PTCUTS)))

            if quantity not in ('Matches', 'Correct'): continue
            self.HistInit('Lxy_'+key, ';L_{xy} [cm];Counts', 800, 0., 800.)

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

    baseMuons = [mu for mu in muons if mu.nDTStations+mu.nCSCStations>1 and mu.nCSCHits+mu.nDTHits>12 and mu.ptError/mu.pt<1.]

    for pTCut in PTCUTS:
        for nMuons in ('All', '2', '3', '4'):
            self.fillHist(nMuons, 'Triggers', pTCut)

        selectedMuons    = [mu for mu in baseMuons if mu.pt > pTCut]
        selectedOIndices = [mu.idx for mu in selectedMuons]
        selectedDimuons  = [dim for dim in dimuons if dim.idx1 in selectedOIndices and dim.idx2 in selectedOIndices]

        if len(selectedMuons) > 0:
            nMuons = nToStr(len(selectedMuons))
            self.fillHist(nMuons, 'Events', pTCut)

            if len(selectedDimuons) > 0:
                # follow the recipe to find the best 1 or 2 dimuons
                if len(selectedMuons) >= 3:
                    sortedDimuons = sorted(selectedDimuons, key=lambda dim: dim.normChi2)

                if len(selectedMuons) >= 4:
                    sortedMuons = sorted(selectedMuons, key=lambda mu: mu.pt, reverse=True)
                    highestPTMuons = sortedMuons[:4]
                    highestIndices = [mu.idx for mu in highestPTMuons]
                    HPDs = {d.ID:d for d in selectedDimuons if d.idx1 in highestIndices and d.idx2 in highestIndices}

                    # find all unique non-overlapping pairs of dimuons
                    pairings = []
                    dimuonList = HPDs.values()
                    for dim1 in dimuonList:
                        for dim2 in dimuonList:
                            if dim1.ID == dim2.ID: continue
                            muonIDs = set(dim1.ID+dim2.ID)
                            if len(muonIDs) == 4:
                                pairings.append((dim1, dim2))

                    def C2S(pairing): return pairing[0].normChi2+pairing[1].normChi2
                    def AMD(pairing): return abs(pairing[0].mass-pairing[1].mass)

                    funcs = {'C2S':C2S, 'AMD':AMD}

                    # sort the pairings by a pairing criteria
                    if len(pairings) > 0:
                        candidateBestDimuons = {fkey:{} for fkey in funcs}
                        sortedPairings = {}
                        for fkey in funcs:
                            sortedPairings[fkey] = sorted(pairings, key=funcs[fkey])
                            for d in sortedPairings[fkey][0]:
                                candidateBestDimuons[fkey][d.ID] = d

                        # try to use AMD for low Lxy
                        if ARGS.CUTS == '_AMD':
                            dims = candidateBestDimuons['AMD'].values()
                            if dims[0].Lxy() < 30. and dims[1].Lxy() < 30.:
                                bestDimuons = candidateBestDimuons['AMD']
                            else:
                                bestDimuons = candidateBestDimuons['C2S']
                        else:
                            bestDimuons = candidateBestDimuons['C2S']

                    # if there were NO pairings, there had to have been <=3 dimuons
                    # because any 4 dimuons can always make at least 1 pair
                    # this means 1 of the 4 muons formed no dimuons at all
                    # so treat this case like the 3 mu case
                    else:
                        sortedDimuons = sorted(selectedDimuons, key=lambda dim: dim.normChi2)
                        bestDimuons = {sortedDimuons[0].ID:sortedDimuons[0]}

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

                # loop over matches and fill if correct by some criteria
                for genPairIndex, dimuonMatches in realMatches.iteritems():
                    if len(dimuonMatches) > 0:
                        self.fillHist(nMuons, 'Matches', pTCut)
                        self.fillLxyHist(nMuons, 'Matches', pTCut, genMuonPairs[genPairIndex][0].Lxy())

                        # best matched dimuon
                        matchedDimuon = dimuonMatches['dim']

                        # if we have 2 muons, take the dimuon made from them
                        if len(selectedMuons) == 2:
                            # strictly speaking this if is not necessary because
                            # if there was a match, then with 2 muons it will be the only dimuon in the list
                            bestDimuon = selectedDimuons[0]
                            if matchedDimuon.ID == bestDimuon.ID:
                                self.fillHist(nMuons, 'Correct', pTCut)
                                self.fillLxyHist(nMuons, 'Correct', pTCut, genMuonPairs[genPairIndex][0].Lxy())

                        # if we have 3 muons, take the dimuon with the lowest chi^2/dof
                        elif len(selectedMuons) == 3:
                            bestDimuon = sortedDimuons[0]
                            if matchedDimuon.ID == bestDimuon.ID:
                                self.fillHist(nMuons, 'Correct', pTCut)
                                self.fillLxyHist(nMuons, 'Correct', pTCut, genMuonPairs[genPairIndex][0].Lxy())

                        # if we have 4+ muons, take the pair of dimuons with the lowest sum of chi^2/dof
                        elif len(selectedMuons) >= 4:
                            if matchedDimuon.ID in bestDimuons:
                                self.fillHist(nMuons, 'Correct', pTCut)
                                self.fillLxyHist(nMuons, 'Correct', pTCut, genMuonPairs[genPairIndex][0].Lxy())

def fillHist(self, nMuons, quantity, pTCut):
    if nMuons is None: return
    # if it's not triggers, fill All at the same time
    if quantity is not 'Triggers':
        self.HISTS['n'+quantity+'_All'    ].Fill(pTCut)
        self.HISTS['n'+quantity+'_'+nMuons].Fill(pTCut)
    # if it's triggers, require All to be called specially
    else:
        self.HISTS['n'+quantity+'_'+nMuons].Fill(pTCut)

def fillLxyHist(self, nMuons, quantity, pTCut, Lxy):
    if nMuons is None: return
    if pTCut != 0: return
    self.HISTS['Lxy_n'+quantity+'_All'    ].Fill(Lxy)
    self.HISTS['Lxy_n'+quantity+'_'+nMuons].Fill(Lxy)


#### RUN ANALYSIS ####
if __name__ == '__main__':
    # get arguments
    ARGS = Analyzer.PARSER.parse_args()

    # set sample object based on arguments
    Analyzer.setSample(ARGS)

    # define Analyzer methods
    for METHOD in ('analyze', 'declareHistograms', 'fillHist', 'fillLxyHist'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])

    # declare analyzer
    analyzer = Analyzer.Analyzer(
        ARGS        = ARGS,
        BRANCHKEYS  = ('DSAMUON', 'EVENT', 'GEN', 'DIMUON', 'TRIGGER'),
    )
    analyzer.writeHistograms('roots/RecipeAnalysisPlots{}{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else '', ARGS.CUTS))

