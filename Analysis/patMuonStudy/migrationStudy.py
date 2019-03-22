import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedDimuons
import DisplacedDimuons.Analysis.Selector as Selector

#### CLASS AND FUNCTION DEFINITIONS ####
# setup function for Analyzer class
def begin(self, PARAMS=None):
    pass

# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    pass

# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    if self.TRIGGER and self.SP is not None:
        if not Selections.passedTrigger(E): return
    DSAmuons = E.getPrimitives('DSAMUON')
    PATmuons = E.getPrimitives('PATMUON')
    Dimuons3 = E.getPrimitives('DIMUON')
    Event    = E.getPrimitives('EVENT')

    eventWeight = 1.
    try:
        eventWeight = 1. if Event.weight > 0. else -1.
    except:
        pass

    CutStrings = {
        ''   : '_Combined_NS_NH_FPTE_HLT_REP_PT_PC_LXYE_MASS',
        'G'  : '_Combined_NS_NH_FPTE_HLT_GLB_REP_PT_PC_LXYE_MASS',
        'GN' : '_Combined_NS_NH_FPTE_HLT_GLB_NTL_REP_PT_PC_LXYE_MASS',
        'M'  : '_Combined_NS_NH_FPTE_HLT_MED_REP_PT_PC_LXYE_MASS',
        'MN' : '_Combined_NS_NH_FPTE_HLT_MED_NTL_REP_PT_PC_LXYE_MASS',
    }
    CutStringKeys = ('', 'G', 'GN', 'M', 'MN')
    selectedDimuons, selectedDSAmuons, selectedPATmuons = {}, {}, {}

    for key in CutStringKeys:
        selectedDimuons[key], selectedDSAmuons[key], selectedPATmuons[key] = Selector.SelectObjects(E, CutStrings[key], Dimuons3, DSAmuons, PATmuons)

    selectedIDs = {key:set() for key in CutStringKeys}
    for key in CutStringKeys:
        if selectedDimuons[key] is None: continue
        for dim in selectedDimuons[key]:
            selectedIDs[key].add((dim.composition[:3], dim.idx1, dim.idx2))

    maxLen = max([len(selectedIDs[key]) for key in selectedIDs])

    if not selectedIDs[''] == selectedIDs['G'] == selectedIDs['M'] == selectedIDs['GN'] == selectedIDs['MN']:
        print '::: {:13s} {:d} {:7d} {:10d} :::'.format(self.NAME, Event.run, Event.lumi, Event.event)
        for key in CutStringKeys:
            strings = []
            if selectedDimuons[key] is not None:
                for dim in selectedDimuons[key]:
                    strings.append('{:3s} {:2d} {:2d} ::: {:9.4f} {:8.4f} {:10.2f} {:6.2f}'.format(
                        dim.composition[:3], dim.idx1, dim.idx2,
                        dim.LxySig(), dim.Lxy(), dim.normChi2, min(dim.mu1.d0Sig(),dim.mu2.d0Sig()))
                    )
            while len(strings) < maxLen:
                strings.append('-')

            for s in strings:
                print '  {:2s} ::: {:s}'.format(key if key != '' else 'X', s)

# cleanup function for Analyzer class
def end(self, PARAMS=None):
    pass
    #if self.SP is not None:
    #    print '{:5s} {:4d} {:3d} {:4d}'.format('4Mu' if '4Mu' in self.NAME else '2Mu2J', self.SP.mH, self.SP.mX, self.SP.cTau),
    #else:
    #    print '{:s}'.format(self.NAME),

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
        BRANCHKEYS  = ('DIMUON', 'PATMUON', 'DSAMUON', 'TRIGGER', 'GEN', 'EVENT'),
    )
