import ROOT as R
from DisplacedDimuons.Common.Constants import SIGNALS
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Analysis.AnalysisTools as AT
import DisplacedDimuons.Analysis.Selector as Selector
import itertools, operator
from PileupTools import PileupWeight

CUTSTRING = '_Combined_NS_NH_FPTE_HLT_REP_PT_TRK_NDT_DCA_PC_LXYE_MASS_CHI2_VTX_COSA_NPP_LXYSIG_OS_DPHI'

#### CLASS AND FUNCTION DEFINITIONS ####
# setup function for Analyzer class
def begin(self, PARAMS=None):
    if self.SP is None:
        print 'This script only runs on signal.'
        exit()

    self.COUNTS = {
            'None' : {'sumWeights':0., 'counts':0.},
            'Nom'  : {'sumWeights':0., 'counts':0.},
            'Low'  : {'sumWeights':0., 'counts':0.},
            'High' : {'sumWeights':0., 'counts':0.},
    }

# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    Event = E.getPrimitives('EVENT')

    for key in self.COUNTS:
        weight = PileupWeight(Event.nTruePV, variation=key)
        self.COUNTS[key]['sumWeights'] += weight

    if self.TRIGGER and self.SP is not None:
        if not Selections.passedTrigger(E): return

    DSAmuons = E.getPrimitives('DSAMUON')
    PATmuons = E.getPrimitives('PATMUON')
    Dimuons3 = E.getPrimitives('DIMUON')

    cutstring = CUTSTRING
    selectedDimuons, selectedDSAmuons, selectedPATmuons = Selector.SelectObjects(E, cutstring, Dimuons3, DSAmuons, PATmuons)
    if selectedDimuons is not None:
        for dim in selectedDimuons:
            if dim.composition != 'DSA': continue
            if dim.LxySig() < 7.: continue

            for key in self.COUNTS:
                weight = PileupWeight(Event.nTruePV, variation=key)
                self.COUNTS[key]['counts'] += weight

# cleanup function for Analyzer class
def end(self, PARAMS=None):
    print '{:4d} {:3d} {:4d} ::: {:11.5f} {:11.5f} ::: {:11.5f} {:11.5f} ::: {:11.5f} {:11.5f} ::: {:11.5f} {:11.5f}'.format(
            self.SP.mH, self.SP.mX, self.SP.cTau,
            *itertools.chain(*[(self.COUNTS[key]['sumWeights'], self.COUNTS[key]['counts']) for key in ('None', 'Nom', 'Low', 'High')])
    )

#### RUN ANALYSIS ####
if __name__ == '__main__':
    # get arguments
    Analyzer.PARSER.add_argument('--idphi', dest='IDPHI', action='store_true')
    ARGS = Analyzer.PARSER.parse_args()

    # set sample object based on arguments
    Analyzer.setSample(ARGS)

    # define Analyzer methods
    for METHOD in ('begin', 'analyze', 'end'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])

    # declare analyzer
    analyzer = Analyzer.Analyzer(
        ARGS        = ARGS,
        BRANCHKEYS  = ('DIMUON', 'PATMUON', 'DSAMUON', 'TRIGGER', 'GEN', 'EVENT', 'FILTER'),
    )
