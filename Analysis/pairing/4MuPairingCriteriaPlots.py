import ROOT as R
import numpy as np
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedMuons, matchedDimuons, matchedDimuonPairs

PTCUTS = list(range(41))
MULTCUTS = (0, 5, 10, 15)

#### CLASS AND FUNCTION DEFINITIONS ####
# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    corrects = ('Chi2', 'HPD', 'HPD-OC', 'HPD-LCD', 'HPD-AMD', 'HPD-FMD', 'HPD-C2S')
    for key in ['nMatch', 'nMatch4'] + ['nCorrect'+c for c in corrects]:
        self.HistInit(key, ';p_{T} Cut [GeV];Counts', len(PTCUTS), 0., float(len(PTCUTS)))

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

    for pTCut in PTCUTS:
        selectedMuons    = [mu for mu in baseMuons if mu.pt > pTCut]
        selectedOIndices = [mu.idx for mu in selectedMuons]
        selectedDimuons  = [dim for dim in baseDimuons if dim.idx1 in selectedOIndices and dim.idx2 in selectedOIndices]

        if len(selectedDimuons) > 0:
            bestDimuonIDs = {}
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
            bestDimuonIDs['Chi2'] = [(d.idx1, d.idx2) for d in lowestChi2Dimuons]

            # sort muons by pT, get best <=4, their dimuons, and their "IDs"
            sortedMuons = sorted(selectedMuons, key=lambda mu: mu.pt, reverse=True)
            if len(sortedMuons) > 4:
                highestPTMuons = sortedMuons[:4]
            else:
                highestPTMuons = sortedMuons
            highestIndices = [mu.idx for mu in highestPTMuons]
            bestDimuonIDs['HPD'] = [(d.idx1, d.idx2) for d in selectedDimuons if d.idx1 in highestIndices and d.idx2 in highestIndices]
            HPDs = [dim for dim in selectedDimuons if (dim.idx1, dim.idx2) in bestDimuonIDs['HPD']]

            # HPDs with opposite charge
            bestDimuonIDs['HPD-OC'] = [(d.idx1, d.idx2) for d in HPDs if muons[d.idx1].charge != muons[d.idx2].charge]

            # sort HPDs by chi^2 and get best <=2
            sortedHPDs = sorted(HPDs, key=lambda dim: dim.normChi2)
            HPD_LCDs = []
            for dim in sortedHPDs:
                if len(HPD_LCDs) == 0:
                    HPD_LCDs.append(dim)
                else:
                    alreadyLow = HPD_LCDs[0]
                    alreadyID  = (alreadyLow.idx1, alreadyLow.idx2)
                    if dim.idx1 in alreadyID or dim.idx2 in alreadyID: continue
                    HPD_LCDs.append(dim)
                    break
            bestDimuonIDs['HPD-LCD'] = [(d.idx1, d.idx2) for d in HPD_LCDs]

            # pair HPDs uniquely and non-overlapping-ly and sort the PAIRINGs by AMD and C2S
            pairings = []
            for i in range(len(HPDs)):
                for j in range(i+1, len(HPDs)):
                    muonIDs = set((HPDs[i].idx1, HPDs[i].idx2, HPDs[j].idx1, HPDs[j].idx2))
                    if len(muonIDs) == 4:
                        pairings.append((i, j))

            if len(pairings) > 0:

                def AMD(pairing): return abs(HPDs[pairing[0]].mass-HPDs[pairing[1]].mass)
                def FMD(pairing): return abs(HPDs[pairing[0]].mass-HPDs[pairing[1]].mass)/(HPDs[pairing[0]].mass+HPDs[pairing[1]].mass)
                def C2S(pairing): return HPDs[pairing[0]].normChi2+HPDs[pairing[1]].normChi2

                functions = {'AMD':AMD, 'FMD':FMD, 'C2S':C2S}

                sortedPairings = {}
                for key in functions:
                    sortedPairings[key] = sorted(pairings, key=functions[key])
                    bestDimuonIDs['HPD-'+key] = []
                    if len(sortedPairings[key]) > 0:
                        didx1, didx2 = sortedPairings[key][0]
                        for idx in sortedPairings[key][0]:
                            bestDimuonIDs['HPD-'+key].append((HPDs[idx].idx1, HPDs[idx].idx2))

            else:
                for key in ('AMD', 'FMD', 'C2S'): bestDimuonIDs['HPD-'+key] = []


            # find best non-overlapping matches for both pairs
            realMatches, dimuonMatches, muon0Matches, muon1Matches = matchedDimuonPairs(genMuonPairs, selectedDimuons)

            # loop over gen muon pairs
            for pairIndex in realMatches:
                self.HISTS['nMatch'].Fill(pTCut)
                if len(realMatches) == 2: self.HISTS['nMatch4'].Fill(pTCut)

                # best matched dimuon
                matchedDimuon = realMatches[pairIndex]['dim']

                # fill a pTCut histogram with number of matches that are also found in one of various lists
                for key in ('Chi2', 'HPD', 'HPD-OC', 'HPD-LCD', 'HPD-AMD', 'HPD-FMD', 'HPD-C2S'):
                    if key in ('HPD-AMD', 'HPD-FMD', 'HPD-C2S') and len(realMatches) != 2: continue
                    if (matchedDimuon.idx1, matchedDimuon.idx2) in bestDimuonIDs[key]:
                        self.HISTS['nCorrect'+key].Fill(pTCut)

            # note that nMatch4 is only filled when we have 2 matches and HPD-AMD,FMD,C2S are only filled as a subset of them

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
    analyzer.writeHistograms('roots/pairingCriteriaPlots{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else ''))
