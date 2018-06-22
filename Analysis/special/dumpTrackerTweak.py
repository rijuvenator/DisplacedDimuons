import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedMuons

PATSIGNALPOINTS = ((125, 20, 13), (1000, 150, 1000))

#### CLASS AND FUNCTION DEFINITIONS ####
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

        if PARAMS == 'NEW':
            # if both genMuons matched, check if there is a dimuon with exactly those recoMuons
            if muonMatches[0] is not None and muonMatches[1] is not None:
                for dimuon in Dimuons:
                    if dimuon.idx1 in muonMatches and dimuon.idx2 in muonMatches:
                        break
                else:
                    if genMuonPair[0].Lxy() > 340.:
                        dumpInfo(genMuonPair, muonMatches, DSAmuons, Dimuons)
        elif PARAMS == 'OLD':
            # if there were dimuon matches... why?
            if muonMatches[0] is not None and muonMatches[1] is not None:
                for dimuon in Dimuons:
                    if dimuon.idx1 in muonMatches and dimuon.idx2 in muonMatches:
                        if genMuonPair[0].Lxy() > 340.:
                            dumpInfo(genMuonPair, muonMatches, DSAmuons, Dimuons)
                        break

# dump info
def dumpInfo(genMuonPair, muonMatches, DSAmuons, Dimuons):
    for genMuon in genMuonPair:
        print 'Gen Muon Pair: {:7s} {:10.4f} {:7.4f} {:7.4f} {:9.4f}'.format(
                '',
                genMuon.pt,
                genMuon.eta,
                genMuon.phi,
                genMuon.Lxy(),
        )
    for i, muon in enumerate(DSAmuons):
        fstring = '  Reco Muon:   {:7d} {:10.4f} {:7.4f} {:7.4f} {:9s} {:7.4f} {:7.4f}'.format(
            i,
            muon.pt,
            muon.eta,
            muon.phi,
            '',
            muon.p4.DeltaR(genMuonPair[0].p4),
            muon.p4.DeltaR(genMuonPair[1].p4),
        )
        if i in muonMatches:
            fstring = '\033[31m' + fstring + '\033[m'
        print fstring
    for dimuon in Dimuons:
        fstring = '  Dimuon:      {:2d} * {:2d} {:10s} {:7s} {:7s} {:9.4f}'.format(
            dimuon.idx1,
            dimuon.idx2,
            '',
            '',
            '',
            dimuon.Lxy()
        )
        print fstring
    print ''

#### RUN ANALYSIS ####
if __name__ == '__main__':
    Analyzer.PARSER.add_argument('--type', dest='TYPE')
    ARGS = Analyzer.PARSER.parse_args()
    FileTemplate = '/eos/cms/store/user/adasgupt/DisplacedDimuons/NTuples/{}ntuple_HTo2XTo2Mu2J_{}{}.root'
    for METHOD in ('analyze',):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])
    if ARGS.TYPE == 'OLD':
        PREFIX = 'Special/'
        SUFFIX = '_NoTrackerTweak'
    else:
        PREFIX = ''
        SUFFIX = ''
    analyzer = Analyzer.Analyzer(
        NAME        = 'HTo2XTo2Mu2J',
        SIGNALPOINT = Utilities.SignalPoint(ARGS.SIGNALPOINT),
        BRANCHKEYS  = ('GEN', 'DSAMUON', 'DIMUON'),
        TEST        = ARGS.TEST,
        SPLITTING   = ARGS.SPLITTING,
        FILE        = FileTemplate.format(PREFIX, Utilities.SPStr(ARGS.SIGNALPOINT), SUFFIX),
        PARAMS      = ARGS.TYPE
    )

# To run all 4 files and hadd them together into the necessary file, run this command:
#   for TYPE in OLD NEW; do for SP in "125 20 13" "1000 150 1000"; do python compareTrackerTweak.py --type $TYPE --signalpoint $SP & done; done;
# Then when all 4 processes have finished, do
#   hadd LxyEffTest.root LxyEffTest_{OLD,NEW}_HTo2XTo2Mu2J_{125_20_13,1000_150_1000}.root
