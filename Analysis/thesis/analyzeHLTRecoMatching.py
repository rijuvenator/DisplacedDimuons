import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Selector as Selector
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Analysis.AnalysisTools as AT
import DisplacedDimuons.Common.Utilities as Utilities

CUTLIST = Selections.CutLists['DSAQualityCutList']

#### CLASS AND FUNCTION DEFINITIONS ####
# setup function for Analyzer class
def begin(self, PARAMS=None):
    pass

# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    self.HistInit('subPT-Den-Nom', ';generated subleading muon p_{T} [GeV];HLT-RECO Matching Efficiency', 1000, 0., 1000.)
    self.HistInit('subPT-Eff-Nom', ';generated subleading muon p_{T} [GeV];HLT-RECO Matching Efficiency', 1000, 0., 1000.)
    self.HistInit('subPT-Den-Acc', ';generated subleading muon p_{T} [GeV];HLT-RECO Matching Efficiency', 1000, 0., 1000.)
    self.HistInit('subPT-Eff-Acc', ';generated subleading muon p_{T} [GeV];HLT-RECO Matching Efficiency', 1000, 0., 1000.)

    self.HistInit('Lxy-Den-Nom', ';generated L_{xy} [cm];HLT-RECO Matching Efficiency', 500, 0., 500.)
    self.HistInit('Lxy-Eff-Nom', ';generated L_{xy} [cm];HLT-RECO Matching Efficiency', 500, 0., 500.)
    self.HistInit('Lxy-Den-Acc', ';generated L_{xy} [cm];HLT-RECO Matching Efficiency', 500, 0., 500.)
    self.HistInit('Lxy-Eff-Acc', ';generated L_{xy} [cm];HLT-RECO Matching Efficiency', 500, 0., 500.)


# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    if self.TRIGGER and self.SP is not None:
        if not Selections.passedTrigger(E): return

    if '4Mu' in self.NAME:
        mu11, mu12, mu21, mu22, X1, X2, H, P, extramu = E.getPrimitives('GEN')
        genMuons = (mu11, mu12, mu21, mu22)
        genMuonPairs = ((mu11, mu12), (mu21, mu22))
    elif '2Mu2J' in self.NAME:
        mu1, mu2, j1, j2, X, XP, H, P, extramu = E.getPrimitives('GEN')
        genMuons = (mu1, mu2)
        genMuonPairs = ((mu1, mu2),)

    ACCEPT = False
    for genMuonPair in genMuonPairs:
        genAcceptance  =  Selections.AcceptanceSelection(genMuonPair)
        #genAcceptances = [Selections.AcceptanceSelection(genMuonPair[0]), Selections.AcceptanceSelection(genMuonPair[1])]

        if genAcceptance:
            ACCEPT = True

    # I ran this 4 times:
    # - selectedMuons = DSAmuons
    # - selectedMuons = DSAmuons passing Q.C.
    # - selectedMuons = DSAmuons passing Q.C. + pT > 10
    # - selectedMuons = DSAmuons passing Q.C. + pT > 10 + eta < 2
    DSAmuons = E.getPrimitives('DSAMUON')
    selectedMuons = {
        'DSA' : [mu for mu in DSAmuons if Selections.MuonSelection(mu, cutList=CUTLIST) and mu.pt > 10. and abs(mu.eta) < 2.]
    }

    if len(selectedMuons['DSA']) < 2: return

    HLTRECO = True
    HLTPaths, HLTMuons, L1TMuons = E.getPrimitives('TRIGGER')
    HLTMuonMatches = AT.matchedTrigger(HLTMuons, selectedMuons['DSA'])
    if not any([HLTMuonMatches[ij]['matchFound'] for ij in HLTMuonMatches]): HLTRECO = False

    vals = {
        'subPT': min([mu.pt for mu in genMuons]),
        'Lxy'  : genMuons[0].Lxy()
    }

    for val in vals:
        if True:
            if True:
                self.HISTS['{}-Den-Nom'.format(val)].Fill(vals[val])
            if HLTRECO:
                self.HISTS['{}-Eff-Nom'.format(val)].Fill(vals[val])
        if ACCEPT:
            if True:
                self.HISTS['{}-Den-Acc'.format(val)].Fill(vals[val])
            if HLTRECO:
                self.HISTS['{}-Eff-Acc'.format(val)].Fill(vals[val])

# cleanup function for Analyzer class
def end(self, PARAMS=None):
    pass

#### RUN ANALYSIS ####
if __name__ == '__main__':
    # get arguments
    ARGS = Analyzer.PARSER.parse_args()

    # set sample object based on arguments
    Analyzer.setSample(ARGS)

    # define Analyzer methods
    for METHOD in ('begin', 'declareHistograms', 'analyze', 'end'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])

    # declare analyzer
    analyzer = Analyzer.Analyzer(
        ARGS        = ARGS,
        BRANCHKEYS  = ('RSAMUON', 'DSAMUON', 'TRIGGER', 'GEN', 'EVENT', 'FILTER'),
    )

    # write plots
    analyzer.writeHistograms('roots/mcbg/HLTRECOPlots{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else ''))
