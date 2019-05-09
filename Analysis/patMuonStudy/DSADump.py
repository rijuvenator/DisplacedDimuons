import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Analysis.RootTools as RT
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedDimuons, numberOfParallelPairs
import DisplacedDimuons.Analysis.Selector as Selector
import DisplacedDimuons.Analysis.PrimitivesPrinter as Printer

Printer.COLORON = True

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

    Event = E.getPrimitives('EVENT')

    # take 10% of data: event numbers ending in 7
    if 'DoubleMuon' in self.NAME:
        if Event.event % 10 != 7: return

    DSAmuons = E.getPrimitives('DSAMUON')
    PATmuons = E.getPrimitives('PATMUON')
    Dimuons3 = E.getPrimitives('DIMUON')

    eventWeight = 1.
    try:
        eventWeight = 1. if Event.weight > 0. else -1.
    except:
        pass

    selectedDimuons, selectedDSAmuons, selectedPATmuons = Selector.SelectObjects(E, self.CUTS, Dimuons3, DSAmuons, PATmuons)
    if selectedDimuons is None: return

    def getOriginalMuons(dim, DSAmuons):
        if dim.composition == 'PAT':
            return PATmuons[dim.idx1], PATmuons[dim.idx2]
        elif dim.composition == 'DSA':
            return DSAmuons[dim.idx1], DSAmuons[dim.idx2]
        else:
            return DSAmuons[dim.idx1], PATmuons[dim.idx2]

    def modifiedName(name):
        if 'DoubleMuon' in name:
            return 'Data'+name[17]
        if 'QCD' in name:
            return 'QCD'
        if 'HTo2X' in name:
            return '{:4d} {:3d} {:4d}'.format(*self.SP.SP)
        return name

    cleanMuons = [d for d in DSAmuons if d.nCSCHits+d.nDTHits>12 and d.pt>5.]

    for dim in selectedDimuons:
        if dim.composition != 'DSA': continue
        #if not (dim.composition == 'DSA' or dim.composition == 'HYBRID'): continue

        mu1, mu2 = getOriginalMuons(dim, DSAmuons)
        nMinusPP, nPlusPP = numberOfParallelPairs(DSAmuons)

        print '{:9s} {:d} {:7d} {:10d} {:2d} ::: {:3s} {:2d} {:2d} ::: {:9.4f} {:8.4f} {:5.2f} {:6.3f} {:6.3f} {:.3e} ::: {:6.2f} {:6.2f} {:7.2f} {:7.2f} ::: {:2d} {:2d} {:2d} {:2d} {:2d} ::: {:6.3f} {:6.3f} ::: {:.3e} {:.3e} {:.3e}'.format(
                modifiedName(self.NAME), Event.run, Event.lumi, Event.event, int(eventWeight),
                dim.composition[:3], dim.idx1, dim.idx2,
                dim.LxySig(), dim.Lxy(), dim.normChi2, dim.cosAlpha, dim.cosAlphaOriginal, dim.DCA,
                mu1.d0(), mu2.d0(), mu1.d0Sig(), mu2.d0Sig(),
                len(DSAmuons), len(cleanMuons), nMinusPP, nPlusPP, nMinusPP+nPlusPP,
                mu1.normChi2, mu2.normChi2,
                dim.pos.Dist(dim.PCA), dim.pos.Proj2D().Dist(dim.PCA.Proj2D()), abs(dim.z-dim.z_PCA),
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
        BRANCHKEYS  = ('DIMUON', 'PATMUON', 'DSAMUON', 'TRIGGER', 'GEN', 'EVENT', 'FILTER'),
    )
