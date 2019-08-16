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
    self.HistInit('LxyDen', ';generated L_{xy} [cm];Efficiency for Common Vertex Fit to Converge', 500, 0., 500.)
    self.HistInit('LxyEff', ';generated L_{xy} [cm];Efficiency for Common Vertex Fit to Converge', 500, 0., 500.)

    self.HistInit('pTRes-Less', ';(p_{T}^{reco} #minus p_{T}^{gen})/p_{T}^{gen};Density', 100, -1., 3.)
    self.HistInit('pTRes-More', ';(p_{T}^{reco} #minus p_{T}^{gen})/p_{T}^{gen};Density', 100, -1., 3.)

    self.HistInit('LxyErr-Less', ';#sigma_{L_{xy}} [cm];Density', 101, 0., 101.)
    self.HistInit('LxyErr-More', ';#sigma_{L_{xy}} [cm];Density', 101, 0., 101.)

# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    if '4Mu' in self.NAME:
        mu11, mu12, mu21, mu22, X1, X2, H, P, extramu = E.getPrimitives('GEN')
        genMuons = (mu11, mu12, mu21, mu22)
        genMuonPairs = ((mu11, mu12), (mu21, mu22))
    elif '2Mu2J' in self.NAME:
        mu1, mu2, j1, j2, X, XP, H, P, extramu = E.getPrimitives('GEN')
        genMuons = (mu1, mu2)
        genMuonPairs = ((mu1, mu2),)

    DSAmuons = E.getPrimitives('DSAMUON')
    PATmuons = E.getPrimitives('PATMUON')
    Dimuons3 = E.getPrimitives('DIMUON')

    #selectedDimuons, selectedDSAmuons, selectedPATmuons = Selector.SelectObjects(E, '_Combined_NS_NH_FPTE_PT_DCA_TRK_NDT_PV', Dimuons3, DSAmuons, PATmuons)
    #if selectedDimuons is None: selectedDimuons = []

    selectedDimuons  = [dim for dim in Dimuons3 if dim.composition == 'DSA']
    selectedDSAmuons = [mu  for mu  in DSAmuons if Selections.MuonSelection(mu, cutList=CUTLIST)]

    for genMuonPair in genMuonPairs:
        genMuonSelection = Selections.AcceptanceSelection(genMuonPair)
        if not genMuonSelection: continue

        dimuonMatches, muonMatches, exitcode = AT.matchedDimuons(genMuonPair, selectedDimuons, selectedDSAmuons, vertex='BS')

        fillDen = exitcode.both and ((not exitcode.same) or (exitcode.same and exitcode.nextBest))
        fillNum = exitcode.matched

        if fillDen:
            KEY = 'Lxy'
            F = lambda genMuon: genMuon.Lxy()
            if True:
                self.HISTS[KEY+'Den'].Fill(F(genMuonPair[0]))
            if fillNum:
                self.HISTS[KEY+'Eff'].Fill(F(genMuonPair[0]))

        if fillDen and fillNum:
            region = 'Less' if genMuonPair[0].Lxy() < 320. else 'More'
            genMuonMatches = exitcode.getBestGenMuonMatches(muonMatches)
            selDim = None
            for dim in selectedDimuons:
                if (genMuonMatches[0]['muon'].idx, genMuonMatches[1]['muon'].idx) == dim.ID:
                    selDim = dim
                    break
                if (genMuonMatches[1]['muon'].idx, genMuonMatches[0]['muon'].idx) == dim.ID:
                    selDim = dim
                    break
            for which, genMuon in enumerate(genMuonPair):
                RM     = genMuonMatches[which]['muon']
                GM     = genMuon.BS
                pTRes  = (RM.pt - GM.pt) / GM.pt
                self.HISTS['pTRes-' +region].Fill(pTRes)
                self.HISTS['LxyErr-'+region].Fill(selDim.LxyErr())

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
        BRANCHKEYS  = ('DIMUON', 'PATMUON', 'DSAMUON', 'TRIGGER', 'GEN', 'EVENT', 'FILTER'),
    )

    # write plots
    analyzer.writeHistograms('roots/mcbg/VertexFitPlots{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else ''))
