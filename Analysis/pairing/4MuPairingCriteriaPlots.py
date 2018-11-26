import ROOT as R
import numpy as np
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedMuons, matchedDimuons

PTCUTS = list(range(41))
MULTCUTS = (0, 5, 10, 15)

#### CLASS AND FUNCTION DEFINITIONS ####
# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    for key in ('nMatch', 'nCorrectChi2', 'nCorrectPT', 'nCorrectPTOC', 'nCorrectPTChi2',):# 'nCorrectPTFDM'):
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
            bestDimuonIDs_Chi2 = [(d.idx1, d.idx2) for d in lowestChi2Dimuons]

            # sort muons by pT, get best <=4, their dimuons, and their "IDs"
            sortedMuons = sorted(selectedMuons, key=lambda mu: mu.pt, reverse=True)
            if len(sortedMuons) > 4:
                highestPTMuons = sortedMuons[:4]
            else:
                highestPTMuons = sortedMuons
            highestIndices = [mu.idx for mu in highestPTMuons]
            bestDimuonIDs_pT = [(d.idx1, d.idx2) for d in selectedDimuons if d.idx1 in highestIndices and d.idx2 in highestIndices]

            # sort HPDs by chi^2 and get best <=2
            sortedHPDs = sorted([dim for dim in selectedDimuons if (dim.idx1, dim.idx2) in bestDimuonIDs_pT], key=lambda dim: dim.normChi2)
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
            bestDimuonIDs_HPD_LCD = [(d.idx1, d.idx2) for d in HPD_LCDs]

            # loop over gen muon pairs
            for genMuonPair in genMuonPairs:
                dimuonMatches, muonMatches, exitcode = matchedDimuons(genMuonPair, selectedDimuons)
                if len(dimuonMatches) > 0:
                    self.HISTS['nMatch'].Fill(pTCut)

                    # best matched dimuon
                    matchedDimuon = dimuonMatches[0]['dim']

                    # fill nCorrectChi2 : chi^2/dof criterion, i.e. dimuon with lowest vertex chi2/dof
                    if (matchedDimuon.idx1, matchedDimuon.idx2) in bestDimuonIDs_Chi2:
                        self.HISTS['nCorrectChi2'].Fill(pTCut)

                    # fill nCorrectPT : pT criterion, i.e. dimuon made of highest 2 pT
                    if (matchedDimuon.idx1, matchedDimuon.idx2) in bestDimuonIDs_pT:
                        self.HISTS['nCorrectPT'].Fill(pTCut)
                        # fill nCorrectPTOC : pT criterion + opposite charge
                        if muons[matchedDimuon.idx1].charge != muons[matchedDimuon.idx2].charge:
                            self.HISTS['nCorrectPTOC'].Fill(pTCut)

                    # fill nCorrectPTChi2 : pT criterion + lowest chi^2
                    if (matchedDimuon.idx1, matchedDimuon.idx2) in bestDimuonIDs_HPD_LCD:
                        self.HISTS['nCorrectPTChi2'].Fill(pTCut)

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
