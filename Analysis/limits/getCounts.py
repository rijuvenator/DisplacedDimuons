import ROOT as R
from DisplacedDimuons.Common.Constants import SIGNALS
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Analysis.AnalysisTools as AT
import DisplacedDimuons.Analysis.Selector as Selector
import itertools, operator

OP = {'div':operator.div, 'mul':operator.mul}

CUTSTRING = '_Combined_NS_NH_FPTE_HLT_REP_PT_TRK_NDT_DCA_PC_LXYE_MASS_CHI2_VTX_COSA_NPP_OS_DPHI'

#### CLASS AND FUNCTION DEFINITIONS ####
# setup function for Analyzer class
def begin(self, PARAMS=None):
    self.COUNTS = {}
    if self.SP is not None:
        self.COUNTS['div'] = {i:{'sumWeights':0., 'counts':0.} for i in xrange(1,11)}
        self.COUNTS['mul'] = {i:{'sumWeights':0., 'counts':0.} for i in xrange(2, 6)}

# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    Event = E.getPrimitives('EVENT')

    if self.SP is not None:
        if '2Mu2J' in self.NAME:
            mu1, mu2, j1, j2, X, XP, H, P, extramu = E.getPrimitives('GEN')
            genMuons = (mu1, mu2)
            genMuonPairs = ((mu1, mu2),)

            for op in self.COUNTS:
                for factor in self.COUNTS[op]:
                    signalWeight = AT.SignalWeight(self.SP.cTau, OP[op](self.SP.cTau, float(factor)), mu1, X)
                    self.COUNTS[op][factor]['sumWeights'] += signalWeight

    if self.TRIGGER and self.SP is not None:
        if not Selections.passedTrigger(E): return

    # take 10% of data: event numbers ending in 7
    if 'DoubleMuon' in self.NAME and not self.ARGS.IDPHI:
        if Event.event % 10 != 7: return

    DSAmuons = E.getPrimitives('DSAMUON')
    PATmuons = E.getPrimitives('PATMUON')
    Dimuons3 = E.getPrimitives('DIMUON')

    cutstring = CUTSTRING
    if ('DoubleMuon' in self.NAME or ('DoubleMuon' not in self.NAME and self.SP is None)) and self.ARGS.IDPHI:
        cutstring = CUTSTRING.replace('DPHI', 'IDPHI')
    selectedDimuons, selectedDSAmuons, selectedPATmuons = Selector.SelectObjects(E, cutstring, Dimuons3, DSAmuons, PATmuons)
    if selectedDimuons is not None:
        for dim in selectedDimuons:
            if dim.composition != 'DSA': continue
            if self.SP is not None:
                for op in self.COUNTS:
                    for factor in self.COUNTS[op]:
                        signalWeight = AT.SignalWeight(self.SP.cTau, OP[op](self.SP.cTau, float(factor)), mu1, X)
                        self.COUNTS[op][factor]['counts'] += signalWeight

# cleanup function for Analyzer class
def end(self, PARAMS=None):
    if self.SP is not None:
        for op in self.COUNTS:
            for factor in self.COUNTS[op]:
                print '{:4d} {:3d} {:4d} ::: {:3s} {:2d} ::: {:11.5f} {:11.5f}'.format(
                        self.SP.mH, self.SP.mX, self.SP.cTau, op, factor,
                        self.COUNTS[op][factor]['sumWeights'],
                        self.COUNTS[op][factor]['counts'],
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
