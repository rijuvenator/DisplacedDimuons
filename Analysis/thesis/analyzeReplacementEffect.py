import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Analysis.AnalysisTools as AT
import DisplacedDimuons.Analysis.Selector as Selector


#### CLASS AND FUNCTION DEFINITIONS ####
# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    self.HistInit('Lxy-before'   , ';L_{xy} [cm];Counts'           , 170, 0., 340.)
    self.HistInit('Lxy-after'    , ';L_{xy} [cm];Counts'           , 170, 0., 340.)
    self.HistInit('LxySig-before', ';L_{xy}/#sigma_{L_{xy}};Counts', 170, 0., 340.)
    self.HistInit('LxySig-after' , ';L_{xy}/#sigma_{L_{xy}};Counts', 170, 0., 340.)


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

    eventWeight = 1.
    try:
        eventWeight = 1. if Event.weight > 0. else -1.
    except:
        pass

    selectedDimuons, selectedDSAmuons, selectedPATmuons = Selector.SelectObjects(E, '_Combined_NS_NH_FPTE_HLT_PT', Dimuons3, DSAmuons, PATmuons)
    if selectedDimuons is not None:
        for dim in selectedDimuons:
            if dim.composition != 'DSA': continue
            self.HISTS['Lxy-before'   ].Fill(dim.Lxy()   , eventWeight)
            self.HISTS['LxySig-before'].Fill(dim.LxySig(), eventWeight)

    selectedDimuons, selectedDSAmuons, selectedPATmuons = Selector.SelectObjects(E, '_Combined_NS_NH_FPTE_HLT_REP_PT', Dimuons3, DSAmuons, PATmuons)
    if selectedDimuons is not None:
        for dim in selectedDimuons:
            if dim.composition != 'DSA': continue
            self.HISTS['Lxy-after'    ].Fill(dim.Lxy()   , eventWeight)
            self.HISTS['LxySig-after' ].Fill(dim.LxySig(), eventWeight)

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
    analyzer.writeHistograms('roots/mcbg/RepEffectPlots{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else ''))
