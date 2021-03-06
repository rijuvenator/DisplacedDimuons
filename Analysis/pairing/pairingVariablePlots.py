import ROOT as R
import numpy as np
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedMuons, matchedDimuons, matchedDimuonPairs

PTCUTS = list(range(41))
MULTCUTS = (0, 5, 10, 15)

def quadrature(d1, d2, func):
    return ((func(d1))**2. + (func(d2))**2.)**0.5

SQUANTS = {
    'LxySig'  : {'AXES':(100,  0., 200.), 'LAMBDA': lambda dim: dim.LxySig(), 'PRETTY':'L_{xy}/#sigma_{L_{xy}}'},
    'LxyErr'  : {'AXES':(100,  0., 100.), 'LAMBDA': lambda dim: dim.LxyErr(), 'PRETTY':'#sigma_{L_{xy}} [cm]'  },
    'vtxChi2' : {'AXES':(100,  0., 50. ), 'LAMBDA': lambda dim: dim.normChi2, 'PRETTY':'vtx #chi^{2}/dof'      },
    'deltaR'  : {'AXES':(100,  0., 5.  ), 'LAMBDA': lambda dim: dim.deltaR  , 'PRETTY':'#DeltaR(#mu#mu)'       },
    'cosAlpha': {'AXES':(100, -1., 1.  ), 'LAMBDA': lambda dim: dim.cosAlpha, 'PRETTY':'cos(#alpha)'           },
}
DQUANTS = {
    'deltaM'  : {'AXES':(100, 0., 500.), 'LAMBDA': lambda d1, d2: abs(d1.mass-d2.mass)                           , 'PRETTY':'#DeltaM(#mu#mu)'        },
    'FDM'     : {'AXES':(100, 0., 1.  ), 'LAMBDA': lambda d1, d2: abs(d1.mass-d2.mass)/(d1.mass+d2.mass)         , 'PRETTY':'#DeltaM/#SigmaM(#mu#mu)'},
    'QLxyErr' : {'AXES':(100, 0., 100.), 'LAMBDA': lambda d1, d2: quadrature(d1, d2, SQUANTS['LxyErr']['LAMBDA']), 'PRETTY':'Q(#sigma_{L_{xy}}) [cm]'},
}
#### CLASS AND FUNCTION DEFINITIONS ####
# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    self.HistInit('MvsMSD', ';N(MSD);N(MSD = HPD);Counts', 3, 0., 3., 3, 0., 3.)
    self.HistInit('MvsHPD', ';N(HPD);N(HPD = MSD);Counts', 7, 0., 7., 3, 0., 3.)

    for tag in ('Matched', 'Junk'):
        for squant,params in SQUANTS.iteritems():
            self.HistInit(squant+'_'+tag, ';{};Counts'.format(params['PRETTY']), *params['AXES'])
        for dquant,params in DQUANTS.iteritems():
            self.HistInit(dquant+'_'+tag, ';{};Counts'.format(params['PRETTY']), *params['AXES'])

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

    baseMuons    = [mu for mu in muons if mu.nDTStations+mu.nCSCStations>1 and mu.nCSCHits+mu.nDTHits>12 and mu.ptError/mu.pt<1. and mu.pt > 5.]
    baseOIndices = [mu.idx for mu in baseMuons]
    baseDimuons  = [dim for dim in dimuons if dim.idx1 in baseOIndices and dim.idx2 in baseOIndices]

    # consider the 4+ muon case
    if len(baseMuons) > 3:
        # save a list of the 4 highest pT muons
        selectedMuons    = sorted(baseMuons, key=lambda mu: mu.pt, reverse=True)[:4]
        selectedOIndices = [mu.idx for mu in selectedMuons]
        selectedDimuons  = [dim for dim in baseDimuons if dim.idx1 in selectedOIndices and dim.idx2 in selectedOIndices]
        if ARGS.CUTS == '_OC':
            selectedDimuons = [dim for dim in selectedDimuons if muons[dim.idx1].charge != muons[dim.idx2].charge]
        selectedDimIDs   = {(dim.idx1, dim.idx2):dim for dim in selectedDimuons}

        # find best non-overlapping matches for both pairs
        realMatches, dimuonMatches, muon0Matches, muon1Matches = matchedDimuonPairs(genMuonPairs, baseDimuons)

        # now...
        # realMatches has either 0-2 elements, depending on success of finding matches
        # selectedDim* has 0-6 elements, given 4 choose 2 vs. vertex fit efficiency
        # selectedDim* has 0-4 elements if the opposite charge requirement is in effect
        nMSD = len(realMatches)
        nHPD = len(selectedDimIDs)

        MSDIDs = [(m['dim'].idx1, m['dim'].idx2) for w,m in realMatches.iteritems()]

        # there can be 0-2 MSD == HPD
        nMatched = 0
        for ID in MSDIDs:
            if ID in selectedDimIDs:
                nMatched += 1

        # time to fill all the histograms
        self.HISTS['MvsMSD'].Fill(float(nMSD), float(nMatched))
        self.HISTS['MvsHPD'].Fill(float(nHPD), float(nMatched))

        for ID,HPD in selectedDimIDs.iteritems():
            if ID in MSDIDs:
                tag = 'Matched'
            else:
                tag = 'Junk'

            for squant in SQUANTS:
                F = SQUANTS[squant]['LAMBDA']
                self.HISTS[squant+'_'+tag].Fill(F(HPD))

        def swap(ID):
            return (ID[1], ID[0])

        def checkIfInList(ID1, ID2, L):
            ret1, ret2 = None, None
            if ID1 in L or swap(ID1) in L:
                ret1 = ID1 if ID1 in L else swap(ID1)
            if ID2 in L or swap(ID2) in L:
                ret2 = ID2 if ID2 in L else swap(ID2)
            return ret1, ret2

        if nMatched == 2:
            for pairings in [[(0,1),(2,3)], [(0,2),(1,3)], [(0,3),(1,2)]]:
                firstPair, secondPair = pairings
                firstID, secondID = (selectedMuons[firstPair[0]].idx, selectedMuons[firstPair[1]].idx), (selectedMuons[secondPair[0]].idx, selectedMuons[secondPair[1]].idx)
                ID1, ID2 = checkIfInList(firstID, secondID, selectedDimIDs)
                if ID1 is not None and ID2 is not None:
                    mID1, mID2 = checkIfInList(firstID, secondID, MSDIDs)
                    if mID1 is not None and mID2 is not None:
                        tag = 'Matched'
                    else:
                        tag = 'Junk'

                    for dquant in DQUANTS:
                        F = DQUANTS[dquant]['LAMBDA']
                        self.HISTS[dquant+'_'+tag].Fill(F(selectedDimIDs[ID1], selectedDimIDs[ID2]))

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
    analyzer.writeHistograms('roots/pairingVariablePlots{}{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else '', ARGS.CUTS))
