import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedDimuons, matchedTrigger, applyPairingCriteria, replaceDSADimuons
import DisplacedDimuons.Analysis.Selector as Selector

#### CLASS AND FUNCTION DEFINITIONS ####
# setup function for Analyzer class
def begin(self, PARAMS=None):
    self.COUNTS = {'selected':0, 'replaced':0, 'results':{None:0, True:0, False:0}}

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

    Dimuons = [dim for dim in Dimuons3 if sum(dim.ID) < 999]

    selectedDimuons, selectedDSAmuons = Selector.SelectObjects(E, self.CUTS, Dimuons, DSAmuons)
    if selectedDimuons is None: return

    selectedIDs = [dim.ID for dim in selectedDimuons]
    replacedDimuons, wasReplaced, exitcodes = replaceDSADimuons(Dimuons3, DSAmuons, mode='PAT')
    replacedIDs = {dim.ID:{'rdim':rdim, 'exitcode':exitcode} for dim, rdim, isReplaced, exitcode in zip(Dimuons, replacedDimuons, wasReplaced, exitcodes) if isReplaced}

    self.COUNTS['selected'] += len(selectedIDs)
    self.COUNTS['replaced'] += len([ID for ID in selectedIDs if ID in replacedIDs])

    for dim in selectedDimuons:
        if dim.ID in replacedIDs:
            for result in replacedIDs[dim.ID]['exitcode']:
                self.COUNTS['results'][result] += 1

                #if result: # False and None both fail this
                #    rdim = replacedIDs[dim.ID]['rdim']
                #    print '{:d} {:7d} {:9d} ::: {} ==> {} ::: {:9.4f} ==> {:9.4f} ::: {:8.4f} ==> {:8.4f} ::: {:8.2f} ==> {:8.2f}'.format(
                #        Event.run, Event.lumi, Event.event,
                #        dim.ID, rdim.ID,
                #        dim.LxySig(), rdim.LxySig(),
                #        dim.Lxy(), rdim.Lxy(),
                #        dim.normChi2, rdim.normChi2,
                #        )

# cleanup function for Analyzer class
def end(self, PARAMS=None):
    if self.SP is not None:
        print '{:5s} {:4d} {:3d} {:4d} {:5d} {:5d} {:5d} {:5d} {:5d}'.format('4Mu' if '4Mu' in self.NAME else '2Mu2J', self.SP.mH, self.SP.mX, self.SP.cTau, self.COUNTS['selected'], self.COUNTS['replaced'], self.COUNTS['results'][None], self.COUNTS['results'][True], self.COUNTS['results'][False])
    else:
        print '{:s} {:5d} {:5d} {:5d} {:5d} {:5d}'.format(self.NAME, self.COUNTS['selected'], self.COUNTS['replaced'], self.COUNTS['results'][None], self.COUNTS['results'][True], self.COUNTS['results'][False]) 

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
