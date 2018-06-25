import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedMuons

PATSIGNALPOINTS = ((125, 20, 13), (1000, 150, 1000))

#### CLASS AND FUNCTION DEFINITIONS ####
# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    if self.SP.SP == (125, 20, 13):
        AXES = (100, 0., 50.)
    elif self.SP.SP == (1000, 150, 1000):
        AXES = (100, 0., 500.)
    self.HistInit('LxyDen'+PARAMS, ''                                          , *AXES)
    self.HistInit('LxyEff'+PARAMS, ';gen L_{xy} [cm];Reconstruction Efficiency', *AXES)

# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    if not '2Mu2J' in self.NAME or self.SP.SP not in PATSIGNALPOINTS:
        raise Exception('[ANALYZER ERROR]: This script runs on two specific HTo2XTo2Mu2J signal points only.')

    mu1, mu2, j1, j2, X, XP, H, P = E.getPrimitives('GEN', 'HTo2XTo2Mu2J')
    genMuonPairs = ((mu1, mu2),)
    DSAmuons = E.getPrimitives('DSAMUON')
    Dimuons  = E.getPrimitives('DIMUON' )

    for genMuonPair in genMuonPairs:
        # require genMuonPair to be within acceptance
        genMuonSelection = Selections.AcceptanceSelection(genMuonPair)
        if not genMuonSelection: continue

        # check if any DSA muons match a genMuon
        muonMatches = [None, None]
        for i, genMuon in enumerate(genMuonPair):
            matches = matchedMuons(genMuon, DSAmuons)
            if len(matches) > 0:
                muonMatches[i] = matches[0]['idx']

        # if both genMuons matched, check if there is a dimuon with exactly those recoMuons
        if muonMatches[0] is not None and muonMatches[1] is not None:
            # fill the denominator histogram
            self.HISTS['LxyDen'+PARAMS].Fill(genMuonPair[0].Lxy())

            for dimuon in Dimuons:
                if dimuon.idx1 in muonMatches and dimuon.idx2 in muonMatches:
                    self.HISTS['LxyEff'+PARAMS].Fill(genMuonPair[0].Lxy())

#### RUN ANALYSIS ####
if __name__ == '__main__':
    Analyzer.PARSER.add_argument('--type', dest='TYPE')
    ARGS = Analyzer.PARSER.parse_args()
    Analyzer.setSample(ARGS)
    FileTemplate = '/eos/cms/store/user/adasgupt/DisplacedDimuons/NTuples/{}ntuple_HTo2XTo2Mu2J_{}{}.root'
    for METHOD in ('declareHistograms', 'analyze'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])
    if ARGS.TYPE == 'OLD':
        PREFIX = 'Special/'
        SUFFIX = '_NoTrackerTweak'
    else:
        PREFIX = ''
        SUFFIX = ''
    analyzer = Analyzer.Analyzer(
        ARGS        = ARGS,
        BRANCHKEYS  = ('GEN', 'DSAMUON', 'DIMUON'),
        FILES       = FileTemplate.format(PREFIX, Utilities.SPStr(ARGS.SIGNALPOINT), SUFFIX),
        PARAMS      = ARGS.TYPE
    )
    analyzer.writeHistograms('roots/LxyEffTest_'+ARGS.TYPE+'_{}.root')
    print 'Done', ARGS.SIGNALPOINT, ARGS.TYPE

# To run all 4 files and hadd them together into the necessary file, run this command:
#   for TYPE in OLD NEW; do for SP in "125 20 13" "1000 150 1000"; do python compareTrackerTweak.py --type $TYPE --signalpoint $SP & done; done;
# Then when all 4 processes have finished, do
#   hadd LxyEffTest.root LxyEffTest_{OLD,NEW}_HTo2XTo2Mu2J_{125_20_13,1000_150_1000}.root
