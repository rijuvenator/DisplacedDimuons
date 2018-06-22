import math
import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedMuons

#### CLASS AND FUNCTION DEFINITIONS ####
# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    if self.SP is None:
        raise Exception('[ANALYZER ERROR]: This script runs on signal only.')
    if '4Mu' in self.NAME:
        mu11, mu12, mu21, mu22, X1, X2, H, P = E.getPrimitives('GEN', 'HTo2XTo4Mu')
        genMuons = (mu11, mu12, mu21, mu22)
        genMuonPairs = ((mu11, mu12), (mu21, mu22))
    elif '2Mu2J' in self.NAME:
        mu1, mu2, j1, j2, X, XP, H, P = E.getPrimitives('GEN', 'HTo2XTo2Mu2J')
        genMuons = (mu1, mu2)
        genMuonPairs = ((mu1, mu2),)
    DSAmuons = E.getPrimitives('DSAMUON')

    SelectMuons   = False
    # require muons to pass all selections
    if SelectMuons:
        DSASelections    = [Selections.MuonSelection  (muon)   for muon   in DSAmuons]

        selectedDSAmuons = [mu  for idx,mu  in enumerate(DSAmuons) if DSASelections   [idx]]

    # don't require muons to pass all selections
    else:
        selectedDSAmuons = DSAmuons

    # loop over genMuons and print if pTRes is poor
    for genMuon in genMuons:

        matches = matchedMuons(genMuon, selectedDSAmuons)
        if len(matches) != 0:
            closestRecoMuon = selectedDSAmuons[matches[0]['idx']]

            if (closestRecoMuon.pt-genMuon.pt)/genMuon.pt < -0.8:
                dumpInfo(genMuon, selectedDSAmuons, len(matches))

# dump info
def dumpInfo(genMuon, DSAmuons, nMatches):
    print 'Gen Muon:    {:10.4f} {:7.4f} {:7.4f} {:9.4f} {:2d}'.format(
            genMuon.pt,
            genMuon.eta,
            genMuon.phi,
            genMuon.Lxy(),
            nMatches
    )
    for muon in DSAmuons:
        fstring = '  Reco Muon: {:10.4f} {:7.4f} {:7.4f} {:9s} {:2s} {:7.4f}'.format(
            muon.pt,
            muon.eta,
            muon.phi,
            '',
            '',
            muon.p4.DeltaR(genMuon.p4)
        )
        if muon.p4.DeltaR(genMuon.p4) < 0.3:
            fstring = '\033[31m' + fstring + '\033[m'
        print fstring
    print ''

#### RUN ANALYSIS ####
if __name__ == '__main__':
    ARGS = Analyzer.PARSER.parse_args()
    Analyzer.setFNAME(ARGS)
    for METHOD in ('analyze',):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])
    analyzer = Analyzer.Analyzer(
        NAME        = ARGS.NAME,
        SIGNALPOINT = Utilities.SignalPoint(ARGS.SIGNALPOINT),
        BRANCHKEYS  = ('GEN', 'DSAMUON'),
        TEST        = ARGS.TEST,
        SPLITTING   = ARGS.SPLITTING,
        FILE        = ARGS.FNAME
    )
