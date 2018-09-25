import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedMuons, findDimuon

#### CLASS AND FUNCTION DEFINITIONS ####
def begin(self, PARAMS=None):
    self.DATA = {'signal' : [0, 0, 0], 'background' : [0, 0, 0]}

# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    if self.SP is None:
        raise Exception('[ANALYZER ERROR]: This script runs on signal only.')

    muons   = E.getPrimitives('DSAMUON')

    # apply trigger if --trigger
    # skip events without at least 2 muons with pT > 30
    if self.TRIGGER:
        if not Selections.passedTrigger(E): return

        numPT = 0
        for mu in muons:
            if mu.pt > 30:
                numPT += 1
            if numPT == 2:
                break
        if numPT < 2:
            return

    Event   = E.getPrimitives('EVENT'  )
    dimuons = E.getPrimitives('DIMUON' )

    if '4Mu' in self.NAME:
        mu11, mu12, mu21, mu22, X1, X2, H, P, extramu = E.getPrimitives('GEN')
        genMuons = (mu11, mu12, mu21, mu22)
        genMuonPairs = ((mu11, mu12), (mu21, mu22))
    elif '2Mu2J' in self.NAME:
        mu1, mu2, j1, j2, X, XP, H, P, extramu = E.getPrimitives('GEN')
        genMuons = (mu1, mu2)
        genMuonPairs = ((mu1, mu2),)

    # loop over genMuonPairs, find dimuon, and do something based on result
    for genMuonPair in genMuonPairs:
        if len(dimuons) > 0:
            savedDimuon, exitcode, muonMatches, oMuonMatches = findDimuon(genMuonPair, muons, dimuons)
            if savedDimuon is not None:
                for dimuon in dimuons:
                    if dimuon.idx1 == savedDimuon.idx1 and dimuon.idx2 == savedDimuon.idx2:
                        print '1,'+','.join(['{:.4f}'.format(i) for i in (dimuon.deltaR, dimuon.normChi2, dimuon.Lxy()/dimuon.LxySig())])
                    else:
                        print '0,'+','.join(['{:.4f}'.format(i) for i in (dimuon.deltaR, dimuon.normChi2, dimuon.Lxy()/dimuon.LxySig())])
            else:
                for dimuon in dimuons:
                    print '0,'+','.join(['{:.4f}'.format(i) for i in (dimuon.deltaR, dimuon.normChi2, dimuon.Lxy()/dimuon.LxySig())])

    #for genMuonPair in genMuonPairs:
    #    if len(dimuons) > 0:
    #        savedDimuon, exitcode, muonMatches, oMuonMatches = findDimuon(genMuonPair, muons, dimuons)
    #        if savedDimuon is not None:
    #            for dimuon in dimuons:
    #                dR, chi2, sigLxy = dimuon.deltaR, dimuon.normChi2, dimuon.Lxy()/dimuon.LxySig()
    #                cat = 1 if (dimuon.idx1 == savedDimuon.idx1 and dimuon.idx2 == savedDimuon.idx2) else 0
    #                if cat == 0:
    #                    self.DATA['background'][0] += 1
    #                else:
    #                    self.DATA['signal'    ][0] += 1
    #                if dR < .4638 and dR > .1463 and sigLxy < 19.6:
    #                    if cat == 1:
    #                        self.DATA['signal'    ][1] += 1
    #                    else:
    #                        self.DATA['signal'    ][2] += 1
    #                else:
    #                    if cat == 0:
    #                        self.DATA['background'][1] += 1
    #                    else:
    #                        self.DATA['background'][2] += 1

def end(self, PARAMS=None):
    print self.DATA

#### RUN ANALYSIS ####
if __name__ == '__main__':
    # get arguments
    ARGS = Analyzer.PARSER.parse_args()

    # set sample object based on arguments
    Analyzer.setSample(ARGS)

    # define Analyzer methods
    #for METHOD in ('analyze','begin','end'):
    for METHOD in ('analyze',):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])

    # declare analyzer
    analyzer = Analyzer.Analyzer(
        ARGS        = ARGS,
        BRANCHKEYS  = ('DSAMUON', 'EVENT', 'GEN', 'DIMUON', 'TRIGGER'),
    )
