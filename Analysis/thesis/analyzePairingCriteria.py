import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Analysis.AnalysisTools as AT
import DisplacedDimuons.Analysis.Selector as Selector


#### CLASS AND FUNCTION DEFINITIONS ####
# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    self.HistInit('Lxy-Den', ';generated L_{xy} [cm];Efficiency' , 170, 0., 340.)
    self.HistInit('Lxy-Num', ';generated L_{xy} [cm];Efficiency' , 170, 0., 340.)

# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    if self.TRIGGER and self.SP is not None:
        if not Selections.passedTrigger(E): return

    Event = E.getPrimitives('EVENT')

    # take 10% of data: event numbers ending in 7
    if 'DoubleMuon' in self.NAME and '_IDPHI' not in self.CUTS:
        if Event.event % 10 != 7: return

    DSAmuons = E.getPrimitives('DSAMUON')
    PATmuons = E.getPrimitives('PATMUON')
    Dimuons3 = E.getPrimitives('DIMUON')

    if '4Mu' in self.NAME:
        mu11, mu12, mu21, mu22, X1, X2, H, P, extramu = E.getPrimitives('GEN')
        genMuons = (mu11, mu12, mu21, mu22)
        genMuonPairs = ((mu11, mu12), (mu21, mu22))
    elif '2Mu2J' in self.NAME:
        mu1, mu2, j1, j2, X, XP, H, P, extramu = E.getPrimitives('GEN')
        genMuons = (mu1, mu2)
        genMuonPairs = ((mu1, mu2),)

    prePCDimuons   , prePCDSAmuons   , prePCPATmuons    = Selector.SelectObjects(E, '_Combined_NS_NH_FPTE_HLT_REP_PT_TRK_NDT_DCA'   , Dimuons3, DSAmuons, PATmuons)
    selectedDimuons, selectedDSAmuons, selectedPATmuons = Selector.SelectObjects(E, '_Combined_NS_NH_FPTE_HLT_REP_PT_TRK_NDT_DCA_PC', Dimuons3, DSAmuons, PATmuons)

    if prePCDimuons is not None:

        if len(genMuonPairs) == 1:
            genMuonPair = genMuonPairs[0]
            dimuonMatches, muonMatches, exitcode = AT.matchedDimuons(genMuonPair, [dim for dim in prePCDimuons if dim.composition == 'DSA'])
            if len(dimuonMatches) > 0:
                realMatches = {0:dimuonMatches[0]}
            else:
                realMatches = {}
        else:
            realMatches, dimuonMatches, muon0Matches, muon1Matches = AT.matchedDimuonPairs(genMuonPairs, [dim for dim in prePCDimuons if dim.composition == 'DSA'])

        selectedIDs = [dim.ID for dim in selectedDimuons if dim.composition == 'DSA'] if selectedDimuons is not None else []

        for pairIndex in realMatches:
            self.HISTS['Lxy-Den'].Fill(genMuonPairs[pairIndex][0].Lxy())

            if realMatches[pairIndex]['dim'].ID in selectedIDs:
                self.HISTS['Lxy-Num'].Fill(genMuonPairs[pairIndex][0].Lxy())

#### RUN ANALYSIS ####
if __name__ == '__main__':
    # get arguments
    ARGS = Analyzer.PARSER.parse_args()

    # set sample object based on arguments
    Analyzer.setSample(ARGS)

    # define Analyzer methods
    for METHOD in ('declareHistograms', 'analyze'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])

    # declare analyzer
    analyzer = Analyzer.Analyzer(
        ARGS        = ARGS,
        BRANCHKEYS  = ('DIMUON', 'PATMUON', 'DSAMUON', 'TRIGGER', 'GEN', 'EVENT', 'FILTER'),
    )

    # write plots
    analyzer.writeHistograms('roots/mcbg/PairingCriteriaPlots{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else ''))
