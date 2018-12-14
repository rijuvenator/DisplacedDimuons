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
    for pTCut in map(str, MULTCUTS):
        for split in ('', '_Matched', '_NotMatched'):
            self.HistInit('nMuon'  +split+'_'+pTCut, ';Muon Multiplicity;Counts'  , 15, 0., 15.)
            self.HistInit('nDimuon'+split+'_'+pTCut, ';Dimuon Multiplicity;Counts', 22, 0., 22.)

    #for key in ('nMuon', 'nDimuon', 'nPair', 'nMatch', 'nCorrectChi2', 'nCorrectPT'):
    for key in ('nMatch', 'nCorrectChi2', 'nCorrectHPD'):
        self.HistInit(key, ';p_{T} Cut [GeV];Counts', len(PTCUTS), 0., float(len(PTCUTS)))

    for key in ('nMatch4', 'nCorrectChi24', 'nCorrectHPD4', 'nCorrectLCD4', 'nCorrectC2S4', 'nCorrectAMD4',
                'nMatch3', 'nCorrectChi23', 'nCorrectHPD3',):
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

        # for a few special pT cut values, fill multiplicity histograms: all, and split by matched or not matched
        if pTCut in MULTCUTS:
            sPTCut = str(pTCut)
            self.HISTS['nMuon_'  +sPTCut].Fill(len(selectedMuons  ))
            self.HISTS['nDimuon_'+sPTCut].Fill(len(selectedDimuons))

            # fill split muon histograms; len(0) goes directly to not matched
            matches = []
            if len(selectedMuons) > 0:
                for genMuonPair in genMuonPairs:
                    for genMuon in genMuonPair:
                        matches.extend(matchedMuons(genMuon, selectedMuons, vertex='BS'))
                matches = list(set([m['oidx'] for m in matches]))
                self.HISTS['nMuon_Matched_'   +sPTCut].Fill(len(matches)                   )
                self.HISTS['nMuon_NotMatched_'+sPTCut].Fill(len(selectedMuons)-len(matches))
            else:
                self.HISTS['nMuon_Matched_'   +sPTCut].Fill(0                              )
                self.HISTS['nMuon_NotMatched_'+sPTCut].Fill(0                              )

            # fill split dimuon histograms; len(0) goes directly to not matched
            matches = []
            if len(selectedDimuons) > 0:
                for genMuonPair in genMuonPairs:
                    dimuonMatches, muonMatches, exitcode = matchedDimuons(genMuonPair, selectedDimuons)
                    for m in dimuonMatches:
                        matches.append(m['idx'])
                matches = list(set(matches))
                self.HISTS['nDimuon_Matched_'   +sPTCut].Fill(len(matches)                     )
                self.HISTS['nDimuon_NotMatched_'+sPTCut].Fill(len(selectedDimuons)-len(matches))
            else:
                self.HISTS['nDimuon_Matched_'   +sPTCut].Fill(0                                )
                self.HISTS['nDimuon_NotMatched_'+sPTCut].Fill(0                                )

        #for i in range(len(selectedMuons  )): self.HISTS['nMuon'  ].Fill(pTCut)
        #for i in range(len(selectedDimuons)): self.HISTS['nDimuon'].Fill(pTCut)
        #for i in range(len(genMuonPairs   )): self.HISTS['nPair'  ].Fill(pTCut)

        if len(selectedDimuons) > 0:
            for genMuonPair in genMuonPairs:
                dimuonMatches, muonMatches, exitcode = matchedDimuons(genMuonPair, selectedDimuons)
                if len(dimuonMatches) > 0:
                    self.HISTS['nMatch'].Fill(pTCut)

                    # best matched dimuon
                    matchedDimuon = dimuonMatches[0]['dim']

                    # fill nCorrectChi2 : chi^2/dof criterion, i.e. dimuon with lowest vertex chi2/dof
                    sortedDimuons = sorted(selectedDimuons, key=lambda dim: dim.normChi2)
                    bestDimuon = sortedDimuons[0]
                    if bestDimuon.idx1 == matchedDimuon.idx1 and bestDimuon.idx2 == matchedDimuon.idx2:
                        self.HISTS['nCorrectChi2'].Fill(pTCut)

                    # fill nCorrectHPD : pT criterion, i.e. dimuon made of highest 2 pT
                    sortedMuons = sorted(selectedMuons, key=lambda mu: mu.pt, reverse=True)
                    bestTwo = (sortedMuons[0].idx, sortedMuons[1].idx)
                    bestDimuon = None
                    for dim in selectedDimuons:
                        if dim.idx1 in bestTwo and dim.idx2 in bestTwo:
                            bestDimuon = dim
                            break
                    if bestDimuon is not None:
                        if bestDimuon.idx1 == matchedDimuon.idx1 and bestDimuon.idx2 == matchedDimuon.idx2:
                            self.HISTS['nCorrectHPD'].Fill(pTCut)

                    # test the 3mu and 4mu criteria on 2mu samples
                    bestDimuons = {}
                    if len(sortedMuons) == 3:
                        self.HISTS['nMatch3'].Fill(pTCut)

                        # I have not overwritten bestDimuon yet. It's still the HPD.
                        if bestDimuon is not None:
                            bestDimuons['HPD3'] = (bestDimuon.ID,)
                        else:
                            bestDimuons['HPD3'] = []
                        # Chi2 among all dimuons
                        bestDimuons['Chi23'] = (sortedDimuons[0].ID,)

                        for tag in ('Chi2', 'HPD'):
                            if matchedDimuon.ID in bestDimuons[tag+'3']:
                                self.HISTS['nCorrect'+tag+'3'].Fill(pTCut)

                    elif len(sortedMuons) >= 4:
                        self.HISTS['nMatch4'].Fill(pTCut)

                        highestPTMuons = sortedMuons[:4]
                        highestIndices = [mu.idx for mu in highestPTMuons]
                        bestDimuons['HPD'] = {d.ID:d for d in selectedDimuons if d.idx1 in highestIndices and d.idx2 in highestIndices}

                        pairings = {}
                        for tag in ('HPD',):
                            pairings[tag] = []
                            dimuonList = bestDimuons[tag].values()
                            for dim1 in dimuonList:
                                for dim2 in dimuonList:
                                    if dim1.ID == dim2.ID: continue
                                    muonIDs = set(dim1.ID+dim2.ID)
                                    if len(muonIDs) == 4:
                                        pairings[tag].append((dim1, dim2))

                        def AMD(pairing): return abs(pairing[0].mass-pairing[1].mass)
                        def FMD(pairing): return abs(pairing[0].mass-pairing[1].mass)/(pairing[0].mass+pairing[1].mass)
                        def C2S(pairing): return pairing[0].normChi2+pairing[1].normChi2

                        functions = {'AMD4':AMD, 'C2S4':C2S}

                        # if there are pairings, use sortedPairings[0]
                        for tag in ('HPD',):
                            if len(pairings[tag]) > 0:

                                for fkey in functions:
                                    sortedPairings = sorted(pairings[tag], key=functions[fkey])
                                    bestDimuons[fkey] = []
                                    if len(sortedPairings) > 0:
                                        for dim in sortedPairings[0]:
                                            bestDimuons[fkey].append(dim.ID)

                            else:
                                for fkey in functions:
                                    bestDimuons[fkey] = []

                        # I have not overwritten bestDimuon yet. It's still the HPD.
                        if bestDimuon is not None:
                            bestDimuons['HPD4'] = (bestDimuon.ID,)
                        else:
                            bestDimuons['HPD4'] = []
                        # Chi2 among all dimuons
                        bestDimuons['Chi24'] = (sortedDimuons[0].ID,)
                        # Chi2 among HPDs only
                        if len(bestDimuons['HPD']) > 0:
                            bestDimuons['LCD4'] = (sorted(bestDimuons['HPD'].values(), key=lambda dim: dim.normChi2)[0].ID,)
                        else:
                            bestDimuons['LCD4'] = []

                        for tag in ('Chi2', 'HPD', 'LCD', 'AMD', 'C2S'):
                            if matchedDimuon.ID in bestDimuons[tag+'4']:
                                self.HISTS['nCorrect'+tag+'4'].Fill(pTCut)


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
