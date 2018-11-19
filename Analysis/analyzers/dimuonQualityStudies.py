import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedDimuons

CONFIG = {
    'LxyErr'  : {'AXES':(1000,      0., 100.   ), 'LAMBDA': lambda dim: dim.LxyErr()                      , 'PRETTY':'#sigma_{L_{xy}} [cm]'  },
    'deltaR'  : {'AXES':(1000,      0., 5.     ), 'LAMBDA': lambda dim: dim.deltaR                        , 'PRETTY':'#DeltaR(#mu#mu)'       },
}

#### CLASS AND FUNCTION DEFINITIONS ####
# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    for Q in CONFIG:
        for CAT in ('Matched', 'Junk'):
            self.HistInit(Q+'_'+CAT, ';'+CONFIG[Q]['PRETTY']+';Counts', *CONFIG[Q]['AXES'])

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
    DSAmuons = E.getPrimitives('DSAMUON')
    Dimuons = E.getPrimitives('DIMUON')

    selectedDSAmuons = [mu for mu in DSAmuons if mu.nDTStations+mu.nCSCStations>1 and mu.nCSCHits+mu.nDTHits>12 and mu.ptError/mu.pt<1.] 
    selectedOIndices = [mu.idx for mu in selectedDSAmuons]
    selectedDimuons  = [dim for dim in Dimuons if dim.idx1 in selectedOIndices and dim.idx2 in selectedOIndices]

    for genMuonPair in genMuonPairs:
        dimuonMatches, muonMatches, exitcode = matchedDimuons(genMuonPair, selectedDimuons)

        matchedIndices = [m['idx'] for m in dimuonMatches]

        for idx,dimuon in enumerate(selectedDimuons):
            CAT = 'Matched' if idx in matchedIndices else 'Junk'
            for Q in CONFIG:
                self.HISTS[Q+'_'+CAT].Fill(CONFIG[Q]['LAMBDA'](dimuon))

#### RUN ANALYSIS ####
if __name__ == '__main__':
    ARGS = Analyzer.PARSER.parse_args()
    Analyzer.setSample(ARGS)

    for METHOD in ('declareHistograms', 'analyze'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])

    analyzer = Analyzer.Analyzer(
        ARGS        = ARGS,
        BRANCHKEYS  = ('DIMUON', 'DSAMUON', 'GEN', 'TRIGGER'),
    )

    analyzer.writeHistograms('roots/DimuonQualityStudies{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else ''))
