import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Selector as Selector
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
import DisplacedDimuons.Analysis.AnalysisTools as AT

#### CLASS AND FUNCTION DEFINITIONS ####
# setup function for Analyzer class
def begin(self, PARAMS=None):
    pass

# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    self.WEIGHTS = {1:0., 2:0., 5:0., 10:0.}

    for factor in self.WEIGHTS:
        self.HistInit('genLxy_{}' .format(factor), ';gen L_{xy} [cm];Counts', 200, 0., 1000.)
        self.HistInit('genTime_{}'.format(factor), ';gen time   [cm];Counts', 200, 0., 1000.)
        for comp in ('PAT', 'HYB', 'DSA'):
            self.HistInit('Lxy_{}_{}'.format(comp, factor), ';L_{xy} [cm];Counts', 100, 0., 500.)

# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    if '2Mu2J' in self.NAME:
        mu1, mu2, j1, j2, X, XP, H, P, extramu = E.getPrimitives('GEN')
        genMuons = (mu1, mu2)
        genMuonPairs = ((mu1, mu2),)

    for factor in self.WEIGHTS:
        weight = AT.SignalWeight(self.SP.cTau, self.SP.cTau/float(factor), mu1, X)
        self.WEIGHTS[factor] += weight
        self.HISTS['genLxy_{}' .format(factor)].Fill(mu1.Lxy(), weight)
        self.HISTS['genTime_{}'.format(factor)].Fill(mu1.Lxy()*X.mass/X.pt, weight)

    if self.TRIGGER and self.SP is not None:
        if not Selections.passedTrigger(E): return

    Event = E.getPrimitives('EVENT')

    DSAmuons = E.getPrimitives('DSAMUON')
    PATmuons = E.getPrimitives('PATMUON')
    Dimuons3 = E.getPrimitives('DIMUON')

    selectedDimuons, selectedDSAmuons, selectedPATmuons = Selector.SelectObjects(E, '_Combined_NS_NH_FPTE_HLT_REP_PT_DCA_PC_LXYE_MASS_CHI2_VTX_COSA_NPP_LXYSIG_TRK_OS_NDT_DPHI', Dimuons3, DSAmuons, PATmuons)
    if selectedDimuons is None: return

    for factor in self.WEIGHTS:
        weight = AT.SignalWeight(self.SP.cTau, self.SP.cTau/float(factor), mu1, X)
        for dim in selectedDimuons:
            self.HISTS['Lxy_{}_{}'.format(dim.composition[:3], factor)].Fill(dim.Lxy(), weight)


# cleanup function for Analyzer class
def end(self, PARAMS=None):
    for factor in self.WEIGHTS:
        print '{:4d} {:3d} {:4d} ::: {:2d} {:9.2f}'.format(*(self.SP.SP + (factor, self.WEIGHTS[factor])))

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
    analyzer.writeHistograms('test{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else ''))

