import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Selector as Selector
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Analysis.AnalysisTools as AT
import DisplacedDimuons.Common.Utilities as Utilities

CUTLIST = [s for s in Selections.CutLists['DSAQualityCutList']+Selections.CutLists['AllMuonCutList'] if 'd0Sig' not in s]

#### CLASS AND FUNCTION DEFINITIONS ####
# setup function for Analyzer class
def begin(self, PARAMS=None):
    pass

# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    self.HistInit('nGenDSA', ';generated L_{xy} [cm];Reconstruction Efficiency', 800, 0., 800)
    self.HistInit('nGenRSA', ';generated L_{xy} [cm];Reconstruction Efficiency', 800, 0., 800)
    self.HistInit('nRecDSA', ';generated L_{xy} [cm];Reconstruction Efficiency', 800, 0., 800)
    self.HistInit('nRecRSA', ';generated L_{xy} [cm];Reconstruction Efficiency', 800, 0., 800)

    self.HistInit('pTRes-DSA', ';(p_{T}^{reco} #minus p_{T}^{gen})/p_{T}^{gen};Density', 100, -1., 3.)
    self.HistInit('pTRes-RSA', ';(p_{T}^{reco} #minus p_{T}^{gen})/p_{T}^{gen};Density', 100, -1., 3.)

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

    DSAmuons = E.getPrimitives('DSAMUON')
    RSAmuons = E.getPrimitives('RSAMUON')

    selectedMuons = {
        'DSA': DSAmuons,
        'RSA': RSAmuons
    }

    for genMuonPair in genMuonPairs:

        genAcceptances = [Selections.AcceptanceSelection(genMuonPair[0]), Selections.AcceptanceSelection(genMuonPair[1])]

        for MUON in ('DSA', 'RSA'):
            dimuonMatches, muonMatches, exitcode = AT.matchedDimuons(genMuonPair, [], selectedMuons[MUON], vertex='BS', doDimuons=False)
            genMuonMatches = exitcode.getBestGenMuonMatches(muonMatches)

            for which, genMuon in enumerate(genMuonPair):
                if genAcceptances[which].allExcept('a_Lxy'):
                    self.HISTS['nGen'+MUON].Fill(genMuon.Lxy())
                    if genMuonMatches[which] is not None:
                        self.HISTS['nRec'+MUON].Fill(genMuon.Lxy())

                        RM     = genMuonMatches[which]['muon']
                        GM     = genMuon.BS
                        pTRes  = (RM.pt - GM.pt) / GM.pt

                        self.HISTS['pTRes-'+MUON].Fill(pTRes)

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
    analyzer.writeHistograms('roots/mcbg/DSAVSRSAPlots{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else ''))
