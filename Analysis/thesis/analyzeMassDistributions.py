import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import numberOfParallelPairs
import DisplacedDimuons.Analysis.Selector as Selector
import operator

# no mass
CUTSTRING = '_Combined_NS_NH_FPTE_HLT_REP_PT_TRK_NDT_DCA_PC_LXYE_CHI2_VTX_COSA_NPP_LXYSIG_DPHI_OS'

#### CLASS AND FUNCTION DEFINITIONS ####
# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    self.HistInit('mass', ';m_{#mu#mu} [GeV];Counts', 2000, 0., 1000.)

# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    if self.TRIGGER and self.SP is not None:
        if not Selections.passedTrigger(E): return

    Event = E.getPrimitives('EVENT')

    DSAmuons = E.getPrimitives('DSAMUON')
    PATmuons = E.getPrimitives('PATMUON')
    Dimuons3 = E.getPrimitives('DIMUON')

    selectedDimuons, selectedDSAmuons, selectedPATmuons = Selector.SelectObjects(E, CUTSTRING, Dimuons3, DSAmuons, PATmuons)
    if selectedDimuons is None: return

    for dim in selectedDimuons:
        if dim.composition != 'DSA': continue
        self.HISTS['mass'].Fill(dim.mass)

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
    analyzer.writeHistograms('roots/mcbg/MassDistributions{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else ''))
