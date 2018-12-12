import ROOT as R
import numpy as np
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedMuons, matchedDimuons, matchedDimuonPairs

KEYS = []
for fillWhen in ('', '-4'):
    KEYS.append('All'+fillWhen)
    for oppCharge in ('', '-OC'):
        KEYS.append('Chi2'+oppCharge+fillWhen)
        for criteria in ('-LCD', '-C2S', '-AMD'):
            fullName = 'HPD'+oppCharge+criteria+fillWhen
            if fillWhen == '-4' or (fillWhen == '' and criteria != '-AMD'):
                KEYS.append(fullName)

#### CLASS AND FUNCTION DEFINITIONS ####
# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    for key in KEYS:
        matchtaglist = ('',) if 'All' in key else ('_Matched', '_NotMatched')
        for matchtag in matchtaglist:
            self.HistInit('GLxy_' +key+matchtag, ';gen dimuon L_{xy} [cm];Counts' , 800 , 0., 800. )
            #self.HistInit('GpT1_' +key+matchtag, ';gen leading p_{T} [GeV];Counts', 120 , 0., 1200.)
            #self.HistInit('Gmass_'+key+matchtag, ';gen dimuon mass [GeV];Counts'  , 400 , 0., 400. )

            self.HistInit('RLxy_' +key+matchtag, ';reco dimuon L_{xy} [cm];Counts' , 800 , 0., 800. )
            #self.HistInit('RpT1_' +key+matchtag, ';reco leading p_{T} [GeV];Counts', 120 , 0., 1200.)
            #self.HistInit('Rmass_'+key+matchtag, ';reco dimuon mass [GeV];Counts'  , 400 , 0., 400. )

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

    if '_5GeV' in ARGS.CUTS:
        selectedMuons = [mu for mu in baseMuons if mu.pt > 5.]
    else:
        selectedMuons = baseMuons

    if '_4Reco' in ARGS.CUTS and len(selectedMuons) < 4: return

    selectedOIndices = [mu.idx for mu in selectedMuons]
    selectedDimuons  = [dim for dim in dimuons if dim.idx1 in selectedOIndices and dim.idx2 in selectedOIndices]

    if len(selectedDimuons) > 0:

        bestDimuons = {}

        # sort muons by pT, get best <=4, and their dimuons
        sortedMuons = sorted(selectedMuons, key=lambda mu: mu.pt, reverse=True)
        highestPTMuons = sortedMuons[:4]
        highestIndices = [mu.idx for mu in highestPTMuons]
        bestDimuons['HPD'] = {d.ID:d for d in selectedDimuons if d.idx1 in highestIndices and d.idx2 in highestIndices}

        # HPDs with opposite charge
        bestDimuons['HPD-OC'] = {d.ID:d for d in bestDimuons['HPD'].values() if d.isOC(muons)}

        # abstraction for getting 2 best non-overlapping dimuons satisfying some criteria
        def getBest2(dimuonList, applyOC=False):
            finalList = []
            for dim in dimuonList:
                if len(finalList) == 0:
                    if (not applyOC) or (applyOC and dim.isOC(muons)):
                        finalList.append(dim)
                else:
                    alreadyID = finalList[0].ID
                    if dim.idx1 in alreadyID or dim.idx2 in alreadyID: continue
                    if applyOC and not dim.isOC(muons): continue
                    finalList.append(dim)
                    break
            return {d.ID:d for d in finalList}

        # sort dimuons by chi^2, get best <=2, with or without applying opposite charge
        sortedDimuons = sorted(selectedDimuons, key=lambda dim: dim.normChi2)
        bestDimuons['Chi2'] = getBest2(sortedDimuons)
        bestDimuons['Chi2-4'] = bestDimuons['Chi2']
        bestDimuons['Chi2-OC'] = getBest2(sortedDimuons, applyOC=True)
        bestDimuons['Chi2-OC-4'] = bestDimuons['Chi2-OC']

        # sort HPDs by chi^2 and get best <=2, with or without applying opposite charge
        sortedHPDs = sorted(bestDimuons['HPD'].values(), key=lambda dim: dim.normChi2)
        bestDimuons['HPD-LCD'] = getBest2(sortedHPDs)
        bestDimuons['HPD-LCD-4'] = bestDimuons['HPD-LCD']
        bestDimuons['HPD-OC-LCD'] = getBest2(sortedHPDs, applyOC=True)
        bestDimuons['HPD-OC-LCD-4'] = bestDimuons['HPD-OC-LCD']

        # pair HPDs (or HPD-OCs) uniquely and non-overlapping-ly and sort the PAIRINGs by AMD, FMD, C2S
        pairings = {}
        for tag in ('HPD', 'HPD-OC'):
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

        functions = {'AMD':AMD, 'FMD':FMD, 'C2S':C2S}

        # if there are pairings, use sortedPairings[0]
        for tag in ('HPD', 'HPD-OC'):
            if len(pairings[tag]) > 0:

                for fkey in functions:
                    sortedPairings = sorted(pairings[tag], key=functions[fkey])
                    bestDimuons[tag+'-'+fkey     ] = []
                    bestDimuons[tag+'-'+fkey+'-4'] = []
                    if len(sortedPairings) > 0:
                        for dim in sortedPairings[0]:
                            bestDimuons[tag+'-'+fkey     ].append(dim.ID)
                            bestDimuons[tag+'-'+fkey+'-4'].append(dim.ID)

            else:
                for fkey in functions:
                    bestDimuons[tag+'-'+fkey     ] = []
                    bestDimuons[tag+'-'+fkey+'-4'] = []

        # find best non-overlapping matches for both pairs
        realMatches, dimuonMatches, muon0Matches, muon1Matches = matchedDimuonPairs(genMuonPairs, selectedDimuons)

        # realMatches has 0-2 elements
        MSDIDs = {w:m['dim'].ID for w,m in realMatches.iteritems()}

        funcs = {
            'GLxy'  : lambda gmpair: gmpair[0].Lxy(),
#           'GpT1'  : lambda gmpair: max(gmpair[0].pt, gmpair[1].pt),
#           'Gmass' : lambda gmpair: (gmpair[0].p4+gmpair[1].p4).M(),
            'RLxy'  : lambda dim   : dim.Lxy(),
#           'RpT1'  : lambda dim   : max(dim.mu1.pt, dim.mu2.pt),
#           'Rmass' : lambda dim   : dim.mass,
        }

        for tag in funcs:
            for i,ID in MSDIDs.iteritems():
                if tag[0] == 'R':
                    q = funcs[tag](realMatches[i]['dim'])
                else:
                    q = funcs[tag](genMuonPairs[i])

                self.HISTS[tag+'_All'].Fill(q)
                if len(MSDIDs) == 2:
                    self.HISTS[tag+'_All-4'].Fill(q)

                for pckey in KEYS:
                    if 'All' in pckey: continue
                    if '-4' in pckey and len(MSDIDs) != 2: continue
                    if ID in bestDimuons[pckey]:
                        self.HISTS[tag+'_'+pckey+'_Matched'].Fill(q)
                    else:
                        self.HISTS[tag+'_'+pckey+'_NotMatched'].Fill(q)


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
