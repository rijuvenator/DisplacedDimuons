import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import numberOfParallelPairs
import DisplacedDimuons.Analysis.Selector as Selector
import operator

OP = {'<':max, '>':min}

PI = R.TMath.Pi()

ALL = '_Combined_NS_NH_FPTE_HLT_REP_PT_TRK_NDT_DCA_PC_LXYE_MASS_CHI2_VTX_COSA_NPP_LXYSIG_DPHI_OS_TIME'

def getTime(dim, DSAMuons):
    mu1, mu2 = DSAMuons[dim.idx1], DSAMuons[dim.idx2]

    t1, t2 = abs(mu1.timeAtIP_InOut), abs(mu2.timeAtIP_InOut)
    d1, d2 = mu1.deltaR_SA, mu2.deltaR_SA

    times = []
    for t, d in zip((t1, d1), (t2, d2)):
        if d < 0.3:
            times.append(t)

    times = [t for t in times if t < 998.]
    if len(times) == 0:
        return 999.
    else:
        return max(times)

CONFIG = {
        'nHits'   : (( 50,  0.,   50.), 'N(CSC+DT Hits)'        , '_NS_NH'   , lambda  mu:  mu.nCSCHits+mu.nDTHits, '>' ),
        'FPTE'    : ((100,  0.,    2.), '#sigma_{p_{T}}/p_{T}'  , '_FPTE'    , lambda  mu:  mu.ptError/mu.pt      , '<' ),
        'pT'      : ((100,  0., 1000.), 'p_{T} [GeV]'           , '_PT'      , lambda  mu:  mu.pt                 , '>' ),
        'DCA'     : ((100,  0., 1000.), 'D.C.A. [cm]'           , '_DCA'     , lambda dim: dim.DCA                , None),
        'LxyErr'  : ((100,  0.,  100.), '#sigma_{L_{xy}} [cm]'  , '_LXYE'    , lambda dim: dim.LxyErr()           , None),
        'mass'    : ((800,  0.,  400.), 'M(#mu#mu) [GeV]'       , '_MASS'    , lambda dim: dim.mass               , None),
        'vtxChi2' : ((100,  0.,   50.), 'vtx #chi^{2}'          , '_CHI2'    , lambda dim: dim.normChi2           , None),
        'cosAlpha': (( 50, -1.,    1.), 'cos(#alpha)'           , '_COSA_NPP', lambda dim: dim.cosAlphaOriginal   , None),
        'Npp'     : (( 20,  0.,   20.), 'N(parallel pairs)'     , '_COSA_NPP', numberOfParallelPairs              , None),
        'LxySig'  : ((100,  0.,   50.), 'L_{xy}/#sigma_{L_{xy}}', '_LXYSIG'  , lambda dim: dim.LxySig()           , None),
        'trkChi2' : (( 50,  0.,   10.), 'trk #chi^{2}'          , '_TRK'     , lambda  mu:  mu.normChi2           , '<' ),
        'nDTHits' : (( 50,  0.,   50.), 'N(DT Hits)'            , '_NDT'     , lambda  mu:  mu.nDTHits            , '>' ),
        'deltaPhi': ((100,  0.,    PI), '|#Delta#Phi|'          , '_DPHI'    , lambda dim: dim.deltaPhi           , None),
        'time'    : (( 50,  0.,   50.), '|t_{in-out}| [ns]'     , '_TIME'    , getTime                            , None),
}
for key in CONFIG:
    CONFIG[key] = dict(zip(('AXES', 'PRETTY', 'OMIT', 'LAMBDA', 'CASTTYPE'), CONFIG[key]))

#### CLASS AND FUNCTION DEFINITIONS ####
# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    for key in CONFIG:
        self.HistInit(key, ';{};Counts'.format(CONFIG[key]['PRETTY']), *CONFIG[key]['AXES'])

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

    for key in CONFIG:
        cutString = ALL.replace(CONFIG[key]['OMIT'], '')
        if key == 'deltaPhi':
            if ('DoubleMuon' in self.NAME or ('DoubleMuon' not in self.NAME and self.SP is None)) and self.ARGS.IDPHI:
                cutString += '_IDPHI'
        else:
            if ('DoubleMuon' in self.NAME or ('DoubleMuon' not in self.NAME and self.SP is None)) and self.ARGS.IDPHI:
                cutString = cutString.replace('DPHI', 'IDPHI')
        selectedDimuons, selectedDSAmuons, selectedPATmuons = Selector.SelectObjects(E, cutString, Dimuons3, DSAmuons, PATmuons)
        if selectedDimuons is None: continue

        f = CONFIG[key]['LAMBDA']
        if key == 'Npp':
            if [dim.composition for dim in selectedDimuons].count('DSA') > 0:
                val = sum(f(DSAmuons))
                self.HISTS[key].Fill(val, eventWeight)
        else:
            for dim in selectedDimuons:
                if dim.composition != 'DSA': continue
                if CONFIG[key]['CASTTYPE'] is not None:
                    mus = getOriginalMuons(dim)
                    if key != 'nDTHits':
                        val = OP[CONFIG[key]['CASTTYPE']]([f(mu) for mu in mus])
                    else:
                        vals = [f(mu) for mu in mus if mu.nCSCHits == 0]
                        if len(vals) != 0:
                            val = min(vals)
                        else:
                            val = None
                else:
                    if key == 'time':
                        val = f(dim, DSAmuons)
                    else:
                        val = f(dim)

                if val is not None:
                    self.HISTS[key].Fill(val, eventWeight)

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
    analyzer.writeHistograms('roots/mcbg/NM1Distributions{}{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else '', '' if not ARGS.IDPHI else '_IDPHI'))
