import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Analysis.AnalysisTools as AT
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import numberOfParallelPairs
import DisplacedDimuons.Analysis.Selector as Selector
import operator, itertools

# A simplified version of HaikuPlots, only one variable, but different signal reweights

PI = R.TMath.Pi()

ALL = '_Combined_NS_NH_FPTE_HLT_REP_PT_TRK_NDT_DCA_PC_LXYE_MASS_CHI2_VTX_COSA_NPP_OS_DPHI'

CONFIG = {
        'LxySig'  : ((100, 0., 50.), 'L_{xy}/#sigma_{L_{xy}}', 'DIM', lambda dim: dim.LxySig()),
}
for key in CONFIG:
    CONFIG[key] = dict(zip(('AXES', 'PRETTY', 'TYPE', 'LAMBDA'), CONFIG[key]))

#### CLASS AND FUNCTION DEFINITIONS ####
# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    self.FACTORS = (1,)
    if self.SP is not None:
        self.FACTORS = (1, 2, 5, 10)
        self.WEIGHTS = {factor:0. for factor in self.FACTORS}

    for key in CONFIG:
        for factor in self.FACTORS:
            self.HistInit('{}_{}'.format(key, factor), ';{};Counts'.format(CONFIG[key]['PRETTY']), *CONFIG[key]['AXES'])

# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    # so, a bit of a weird ordering here compared to my usual preferences
    # Event weight goes first because it doesn't depend on anything else
    # Gens come next because signal weights need gens to compute
    # Then the weight sum is computed, because it should not depend on trigger
    # THEN the trigger is applied, the other primitives are extracted, etc.

    Event = E.getPrimitives('EVENT')

    # take 10% of data: event numbers ending in 7
    if 'DoubleMuon' in self.NAME and not self.ARGS.IDPHI:
        if Event.event % 10 != 7: return

    eventWeight = 1.
    try:
        eventWeight = 1. if Event.weight > 0. else -1.
    except:
        pass

    if self.SP is not None:
        if '2Mu2J' in self.NAME:
            mu1, mu2, j1, j2, X, XP, H, P, extramu = E.getPrimitives('GEN')
            genMuons = (mu1, mu2)
            genMuonPairs = ((mu1, mu2),)

            for factor in self.FACTORS:
                signalWeight = AT.SignalWeight(self.SP.cTau, self.SP.cTau/float(factor), mu1, X)
                self.WEIGHTS[factor] += signalWeight*eventWeight

    if self.TRIGGER and self.SP is not None:
        if not Selections.passedTrigger(E): return

    DSAmuons = E.getPrimitives('DSAMUON')
    PATmuons = E.getPrimitives('PATMUON')
    Dimuons3 = E.getPrimitives('DIMUON')

    cutString = ALL[:]
    if ('DoubleMuon' in self.NAME or ('DoubleMuon' not in self.NAME and self.SP is None)) and self.ARGS.IDPHI:
        cutString = cutString.replace('DPHI', 'IDPHI')
    selectedDimuons, selectedDSAmuons, selectedPATmuons = Selector.SelectObjects(E, cutString, Dimuons3, DSAmuons, PATmuons)
    if selectedDimuons is None: return

    def getOriginalMuons(dim):
        if dim.composition == 'PAT':
            return PATmuons[dim.idx1], PATmuons[dim.idx2]
        elif dim.composition == 'DSA':
            return DSAmuons[dim.idx1], DSAmuons[dim.idx2]
        else:
            return DSAmuons[dim.idx1], PATmuons[dim.idx2]

    for factor in self.FACTORS:
        signalWeight = 1.
        if self.SP is not None:
            signalWeight = AT.SignalWeight(self.SP.cTau, self.SP.cTau/float(factor), mu1, X)
        for key in CONFIG:
            f = CONFIG[key]['LAMBDA']
            for dim in selectedDimuons:
                if dim.composition != 'DSA': continue

                mus = getOriginalMuons(dim)

                if CONFIG[key]['TYPE'] == 'DSA':
                    fills = [f(*mus)]
                else:
                    fills = [f(dim)]

                for fill in fills:
                    self.HISTS['{}_{}'.format(key, factor)].Fill(fill, eventWeight*signalWeight)

# cleanup function for Analyzer class
def end(self, PARAMS=None):
    if self.SP is not None:
        for factor in self.FACTORS:
            print '{:4d} {:3d} {:4d} ::: {:2d} {:11.5f}'.format(*(self.SP.SP + (factor, self.WEIGHTS[factor])))

#### RUN ANALYSIS ####
if __name__ == '__main__':
    # get arguments
    Analyzer.PARSER.add_argument('--idphi', dest='IDPHI', action='store_true')
    ARGS = Analyzer.PARSER.parse_args()

    # set sample object based on arguments
    Analyzer.setSample(ARGS)

    # define Analyzer methods
    for METHOD in ('declareHistograms', 'analyze', 'end'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])

    # declare analyzer
    analyzer = Analyzer.Analyzer(
        ARGS        = ARGS,
        BRANCHKEYS  = ('DIMUON', 'PATMUON', 'DSAMUON', 'TRIGGER', 'GEN', 'EVENT', 'FILTER'),
    )

    # write plots
    analyzer.writeHistograms('roots/mcbg/ReweightedPlots{}{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else '', '' if not ARGS.IDPHI else '_IDPHI'))
