import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedMuons, matchedDimuons

CONFIG = {
    'pT': ('p_{T}', (100,  -1.,  5.), lambda rmu: rmu.pt   , lambda gmu, extrap: gmu.pt if extrap == 'LIN' else gmu.BS.pt , lambda rq, gq: (rq-gq)/gq),
    'd0': ('d_{0}', (100, -50., 50.), lambda rmu: rmu.d0() , lambda gmu, extrap: gmu.d0(extrap=extrap)                    , lambda rq, gq:  rq-gq    ),
}

#### CLASS AND FUNCTION DEFINITIONS ####
# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    for QUANTITY in ('pT', 'd0'):
        PRETTY, AXES, RFUNC, GFUNC, RESFUNC = CONFIG[QUANTITY]
        self.HistInit(QUANTITY+'ResRG', ';'+PRETTY+' Res;Counts', *AXES)
        self.HistInit(QUANTITY+'ResBS', ';'+PRETTY+' Res;Counts', *AXES)
    self.HistInit('deltaRRG', ';#DeltaR(#mu#mu);Counts', 50, 0., .2)
    self.HistInit('deltaRBS', ';#DeltaR(#mu#mu);Counts', 50, 0., .2)

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
    Dimuons  = E.getPrimitives('DIMUON' )

    for genMuon in genMuons:
        #print '{:9.4f} {:7.4f} {:7.4f} : {:9.4f} {:7.4f} {:7.4f}'.format(genMuon.pt, genMuon.eta, genMuon.phi, genMuon.BS.pt, genMuon.BS.eta, genMuon.BS.phi)
        matchesRG = matchedMuons(genMuon, DSAmuons, vertex=None)
        matchesBS = matchedMuons(genMuon, DSAmuons             )
        if len(matchesRG) > 0:
            recoMuon = DSAmuons[matchesRG[0]['idx']]
            for QUANTITY in ('pT', 'd0'):
                PRETTY, AXES, RFUNC, GFUNC, RESFUNC = CONFIG[QUANTITY]
                self.HISTS[QUANTITY+'ResRG'].Fill(RESFUNC(RFUNC(recoMuon), GFUNC(genMuon, 'LIN')))
            self.HISTS['deltaRRG'].Fill(matchesRG[0]['deltaR'])
        if len(matchesBS) > 0:
            recoMuon = DSAmuons[matchesBS[0]['idx']]
            for QUANTITY in ('pT', 'd0'):
                PRETTY, AXES, RFUNC, GFUNC, RESFUNC = CONFIG[QUANTITY]
                self.HISTS[QUANTITY+'ResBS'].Fill(RESFUNC(RFUNC(recoMuon), GFUNC(genMuon, 'FULL')))
            self.HISTS['deltaRBS'].Fill(matchesBS[0]['deltaR'])

#### RUN ANALYSIS ####
if __name__ == '__main__':
    # get arguments
    ARGS = Analyzer.PARSER.parse_args()

    # set sample object based on arguments
    Analyzer.setSample(ARGS)

    # define Analyzer methods
    for METHOD in ('declareHistograms', 'analyze',):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])

    # declare analyzer
    analyzer = Analyzer.Analyzer(
        ARGS        = ARGS,
        BRANCHKEYS  = ('DSAMUON', 'GEN', 'DIMUON')
    )

    # write plots
    analyzer.writeHistograms('roots/ResTest{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else ''))
