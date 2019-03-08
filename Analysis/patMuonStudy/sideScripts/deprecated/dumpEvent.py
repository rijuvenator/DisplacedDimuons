import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedDimuons, matchedTrigger, applyPairingCriteria, replaceDSADimuons
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

    Dimuons = [dim for dim in Dimuons3 if dim.composition == 'DSA']

    if self.SP is not None:
        if '4Mu' in self.NAME:
            mu11, mu12, mu21, mu22, X1, X2, H, P, extramu = E.getPrimitives('GEN')
            genMuons = (mu11, mu12, mu21, mu22)
            genMuonPairs = ((mu11, mu12), (mu21, mu22))
        elif '2Mu2J' in self.NAME:
            mu1, mu2, j1, j2, X, XP, H, P, extramu = E.getPrimitives('GEN')
            genMuons = (mu1, mu2)
            genMuonPairs = ((mu1, mu2),)

    eventWeight = 1.
    try:
        eventWeight = 1. if Event.weight > 0. else -1.
    except:
        pass

    selectedDimuons, selectedDSAmuons = Selector.SelectObjects(E, self.CUTS, Dimuons, DSAmuons)
    if selectedDimuons is None: return

    selectedIDs = [dim.ID for dim in selectedDimuons]
    replacedDimuons, wasReplaced = replaceDSADimuons(Dimuons3, DSAmuons, mode='PAT')
    replacedIDs = {dim.ID:rdim for dim, rdim, isReplaced in zip(Dimuons, replacedDimuons, wasReplaced) if isReplaced}

    # this script is for dumping Drell Yan events with Lxy Sig > 100
    # the output of this is used in badChi2.py

    for dim in selectedDimuons:
        if dim.ID in replacedIDs:
            rdim = replacedIDs[dim.ID]
            if rdim.LxySig() > 100.:
                print '{:d} {:7d} {:10d} ::: {} ==> {} ::: {:9.4f} ==> {:9.4f} ::: {:8.4f} ==> {:8.4f} ::: {:10.2f} ==> {:10.2f}'.format(
                    Event.run, Event.lumi, Event.event,
                    dim.ID, rdim.ID,
                    dim.LxySig(), rdim.LxySig(),
                    dim.Lxy(), rdim.Lxy(),
                    dim.normChi2, rdim.normChi2,
                    )

# cleanup function for Analyzer class
def end(self, PARAMS=None):
    pass

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
