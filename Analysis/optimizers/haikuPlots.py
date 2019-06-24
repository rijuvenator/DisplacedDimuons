import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import numberOfParallelPairs
import DisplacedDimuons.Analysis.Selector as Selector
import operator, itertools

# I named this script HaikuPlots because there are 5 cuts for vtxChi2, 7 for LxySig, and 5 for trkChi2

PI = R.TMath.Pi()

ALL = '_Combined_NS_NH_FPTE_HLT_REP_PT_NDT_DCA_PC_LXYE_MASS_VTX_COSA_NPP_OS_DPHI'

CONFIG = {
        'vtxChi2' : ((100,  0.,   50.), 'vtx #chi^{2}'          , 'DIM', lambda dim     : dim.normChi2                   , (50, 20, 10, 5, 1)       , operator.lt),
        'LxySig'  : ((100,  0.,   50.), 'L_{xy}/#sigma_{L_{xy}}', 'DIM', lambda dim     : dim.LxySig()                   , (3, 5, 6, 10, 15, 20, 25), operator.gt),
        'trkChi2' : (( 50,  0.,   10.), 'trk #chi^{2}/dof'      , 'DSA', lambda mu1, mu2: max(mu1.normChi2, mu2.normChi2), (10, 4, 3, 2, 1)         , operator.lt),
        'd0Sig'   : ((100,  0.,   20.), 'd_{0}/#sigma_{d_{0}}'  , 'DSA', lambda mu1, mu2: min(mu1.d0Sig(), mu2.d0Sig())  , (0, 1, 2, 5, 10)         , operator.gt),
}
for key in CONFIG:
    CONFIG[key] = dict(zip(('AXES', 'PRETTY', 'TYPE', 'LAMBDA', 'VALS', 'OP'), CONFIG[key]))

KEYS = CONFIG.keys()

def others(key):
    return [k for k in KEYS if k != key]

#### CLASS AND FUNCTION DEFINITIONS ####
# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    # itertools.product is a cartesian product, i.e. a nested for loop, so you want the lists of values, given as vals
    # then you need to build a format string, i.e. '{}_' + '{}-{}' as many keys separated by '_'
    # then you need fstring.format(key, key0, val0, key1, val1, ...) so [item for sublist in list for item in sublist] will make a flat list that can be unpacked
    for key in CONFIG:
        keys = others(key)
        for vals in itertools.product(*[CONFIG[k]['VALS'] for k in keys]):
            fstring = '{}_'
            fstring += '_'.join(['{}-{}'] * len(keys))
            self.HistInit(fstring.format(key, *[item for keyvalpair in zip(keys, vals) for item in keyvalpair]), ';{};Counts'.format(CONFIG[key]['PRETTY']), *CONFIG[key]['AXES'])

# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    if self.TRIGGER and self.SP is not None:
        if not Selections.passedTrigger(E): return

    Event = E.getPrimitives('EVENT')

    # take 10% of data: event numbers ending in 7
    if 'DoubleMuon' in self.NAME and not self.ARGS.IDPHI:
        if Event.event % 10 != 7: return

    DSAmuons = E.getPrimitives('DSAMUON')
    PATmuons = E.getPrimitives('PATMUON')
    Dimuons3 = E.getPrimitives('DIMUON')

    eventWeight = 1.
    try:
        eventWeight = 1. if Event.weight > 0. else -1.
    except:
        pass

    def getOriginalMuons(dim):
        if dim.composition == 'PAT':
            return PATmuons[dim.idx1], PATmuons[dim.idx2]
        elif dim.composition == 'DSA':
            return DSAmuons[dim.idx1], DSAmuons[dim.idx2]
        else:
            return DSAmuons[dim.idx1], PATmuons[dim.idx2]

    cutString = ALL[:]
    if ('DoubleMuon' in self.NAME or ('DoubleMuon' not in self.NAME and self.SP is None)) and self.ARGS.IDPHI:
        cutString = cutString.replace('DPHI', 'IDPHI')
    selectedDimuons, selectedDSAmuons, selectedPATmuons = Selector.SelectObjects(E, cutString, Dimuons3, DSAmuons, PATmuons)
    if selectedDimuons is None: return

    for key in CONFIG:
        f = CONFIG[key]['LAMBDA']
        for dim in selectedDimuons:
            if dim.composition != 'DSA': continue
            mus = getOriginalMuons(dim)

            if CONFIG[key]['TYPE'] == 'DSA':
                fills = [f(*mus)]
            else:
                fills = [f(dim)]

            # as above; this is fully general for N dimensions
            # funcs are the others' lambdas; ops are the others' ops; args are dim if it's a dim cut else mus; passedKeys are if they passed the cut
            # if they all passed, construct the hkey as above and fill
            keys = others(key)
            for vals in itertools.product(*[CONFIG[k]['VALS'] for k in keys]):
                keyvals    = {k:float(val) for k, val in zip(keys, vals)}
                funcs      = {k:CONFIG[k]['LAMBDA']                          for k in keys}
                ops        = {k:CONFIG[k]['OP']                              for k in keys}
                args       = {k:[dim] if CONFIG[k]['TYPE'] == 'DIM' else mus for k in keys}
                passedKeys = {k:ops[k](funcs[k](*args[k]), keyvals[k]) for k in keys}

                if all(passedKeys.values()):

                    fstring = '{}_'
                    fstring += '_'.join(['{}-{}'] * len(keys))
                    hkey = fstring.format(key, *[item for keyvalpair in zip(keys, vals) for item in keyvalpair])

                    for fill in fills:
                        self.HISTS[hkey].Fill(fill, eventWeight)

#### RUN ANALYSIS ####
if __name__ == '__main__':
    # get arguments
    Analyzer.PARSER.add_argument('--idphi', dest='IDPHI', action='store_true')
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
    analyzer.writeHistograms('roots/mcbg/HaikuPlots{}{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else '', '' if not ARGS.IDPHI else '_IDPHI'))
