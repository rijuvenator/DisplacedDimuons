import math
import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedMuons, findDimuon

# CONFIG stores the title and axis tuple so that the histograms can be declared in a loop
HEADERS = ('XTITLE', 'AXES', 'LAMBDA', 'PRETTY', 'ACC_LAMBDA')
VALUES  = (
    ('pT' , 'gen p_{T} [GeV]', (1000,       0.,    500.), lambda muon: muon.pt       , 'p_{T}'  , lambda sel: sel.allExcept('a_pT' )),
    ('eta', 'gen #eta'       , (1000,      -3.,      3.), lambda muon: muon.eta      , '#eta'   , lambda sel: sel.allExcept('a_eta')),
    ('phi', 'gen #phi'       , (1000, -math.pi, math.pi), lambda muon: muon.phi      , '#phi'   , lambda sel: sel                   ),
    ('Lxy', 'gen L_{xy} [cm]', (1000,       0.,    800.), lambda muon: muon.Lxy()    , 'L_{xy}' , lambda sel: sel.allExcept('a_Lxy')),
)
CONFIG = {}
for VAL in VALUES:
    KEY, VALS = VAL[0], VAL[1:]
    CONFIG[KEY] = dict(zip(HEADERS, VALS))

#### CLASS AND FUNCTION DEFINITIONS ####
# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    for KEY in CONFIG:
        TITLE = ';'+CONFIG[KEY]['XTITLE']+'; Vertex Fit Efficiency'
        self.HistInit(KEY+'Eff', TITLE, *CONFIG[KEY]['AXES'])
        self.HistInit(KEY+'Den', ''   , *CONFIG[KEY]['AXES'])

# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    if self.SP is None:
        raise Exception('[ANALYZER ERROR]: This script runs on signal only.')
    if '4Mu' in self.NAME:
        mu11, mu12, mu21, mu22, X1, X2, H, P, extramu = E.getPrimitives('GEN', 'HTo2XTo4Mu')
        genMuons = (mu11, mu12, mu21, mu22)
        genMuonPairs = ((mu11, mu12), (mu21, mu22))
    elif '2Mu2J' in self.NAME:
        mu1, mu2, j1, j2, X, XP, H, P, extramu = E.getPrimitives('GEN', 'HTo2XTo2Mu2J')
        genMuons = (mu1, mu2)
        genMuonPairs = ((mu1, mu2),)
    DSAmuons = E.getPrimitives('DSAMUON')
    Dimuons  = E.getPrimitives('DIMUON' )

    for genMuonPair in genMuonPairs:
        # require genMuonPair to be within acceptance
        genMuonSelection = Selections.AcceptanceSelection(genMuonPair)
        if not genMuonSelection: continue

        dimuon, exitcode, muonMatches = findDimuon(genMuonPair, DSAmuons, Dimuons)

        # both gen muons matched, but no dimuon: fill den only
        if exitcode == 2:
            for KEY in CONFIG:
                F = CONFIG[KEY]['LAMBDA']
                self.HISTS[KEY+'Den'].Fill(F(genMuonPair[0]))
        # both gen muons matched and a dimuon was found
        elif exitcode == 0:
            for KEY in CONFIG:
                F = CONFIG[KEY]['LAMBDA']
                self.HISTS[KEY+'Den'].Fill(F(genMuonPair[0]))
                self.HISTS[KEY+'Eff'].Fill(F(genMuonPair[0]))

#### RUN ANALYSIS ####
if __name__ == '__main__':
    ARGS = Analyzer.PARSER.parse_args()
    Analyzer.setSample(ARGS)
    for METHOD in ('declareHistograms', 'analyze'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])
    analyzer = Analyzer.Analyzer(
        ARGS        = ARGS,
        BRANCHKEYS  = ('GEN', 'DSAMUON', 'DIMUON'),
    )
    analyzer.writeHistograms('roots/SignalVertexFitEffPlots_{}.root')
