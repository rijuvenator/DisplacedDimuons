import ROOT as R
import numpy as np
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedMuons, matchedDimuons, matchedDimuonPairs

#### CLASS AND FUNCTION DEFINITIONS ####
# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    for key in ('All', 'All4', 'Chi2', 'HPD', 'HPD-OC', 'HPD-LCD', 'HPD-AMD', 'HPD-FMD', 'HPD-C2S'):
        matchtaglist = ('',) if 'All' in key else ('_Matched', '_NotMatched')
        for matchtag in matchtaglist:
            self.HistInit('Lxy_' +key+matchtag, ';gen dimuon L_{xy} [cm];Counts' , 800 , 0., 800. )
            self.HistInit('pT1_' +key+matchtag, ';gen leading p_{T} [GeV];Counts', 120 , 0., 1200.)
            self.HistInit('mass_'+key+matchtag, ';gen dimuon mass [GeV];Counts'  , 400 , 0., 400. )

            self.HistInit('RLxy_' +key+matchtag, ';reco dimuon L_{xy} [cm];Counts' , 800 , 0., 800. )
            self.HistInit('RpT1_' +key+matchtag, ';reco leading p_{T} [GeV];Counts', 120 , 0., 1200.)
            self.HistInit('Rmass_'+key+matchtag, ';reco dimuon mass [GeV];Counts'  , 400 , 0., 400. )

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

        bestDimuonIDs = {}
        # sort dimuons by chi^2, get best <=2, and their "IDs"
        sortedDimuons = sorted(baseDimuons, key=lambda dim: dim.normChi2)
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
        sortedMuons = sorted(baseMuons, key=lambda mu: mu.pt, reverse=True)
        if len(sortedMuons) > 4:
            highestPTMuons = sortedMuons[:4]
        else:
            highestPTMuons = sortedMuons
        highestIndices = [mu.idx for mu in highestPTMuons]
        bestDimuonIDs['HPD'] = [(d.idx1, d.idx2) for d in baseDimuons if d.idx1 in highestIndices and d.idx2 in highestIndices]
        HPDs = [dim for dim in baseDimuons if (dim.idx1, dim.idx2) in bestDimuonIDs['HPD']]

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
        realMatches, dimuonMatches, muon0Matches, muon1Matches = matchedDimuonPairs(genMuonPairs, baseDimuons)

        # realMatches has 0-2 elements
        MSDIDs = {w:(m['dim'].idx1, m['dim'].idx2) for w,m in realMatches.iteritems()}

        funcs = {
            'Lxy'   : lambda gmpair: gmpair[0].Lxy(),
            'pT1'   : lambda gmpair: max(gmpair[0].pt, gmpair[1].pt),
            'mass'  : lambda gmpair: (gmpair[0].p4+gmpair[1].p4).M(),
            'RLxy'  : lambda dim   : dim.Lxy(),
            'RpT1'  : lambda dim   : max(dim.mu1.pt, dim.mu2.pt),
            'Rmass' : lambda dim   : dim.mass,
        }

        for tag in funcs:
            for i,ID in MSDIDs.iteritems():
                if tag[0] == 'R':
                    q = funcs[tag](realMatches[i]['dim'])
                else:
                    q = funcs[tag](genMuonPairs[i])
                self.HISTS[tag+'_All'].Fill(q)
                if len(MSDIDs) == 2:
                    self.HISTS[tag+'_All4'].Fill(q)
                for pckey in ('Chi2', 'HPD', 'HPD-OC', 'HPD-LCD', 'HPD-AMD', 'HPD-FMD', 'HPD-C2S'):
                    if len(MSDIDs) != 2 and pckey in ('HPD-AMD', 'HPD-FMD', 'HPD-C2S'): continue
                    if ID in bestDimuonIDs[pckey]:
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
