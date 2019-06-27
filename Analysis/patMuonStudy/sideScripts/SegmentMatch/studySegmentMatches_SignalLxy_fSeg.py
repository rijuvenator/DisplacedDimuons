import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Analysis.RootTools as RT
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedDimuons, numberOfParallelPairs
import DisplacedDimuons.Analysis.Selector as Selector
import DisplacedDimuons.Analysis.PrimitivesPrinter as Printer

Printer.COLORON = True

FSEGS = {
    .9999 : {'tag':'1' },
    .7499 : {'tag':'34'},
    .6599 : {'tag':'23'},
    .4599 : {'tag':'12'},
}

#### CLASS AND FUNCTION DEFINITIONS ####
# setup function for Analyzer class
def begin(self, PARAMS=None):
    self.COUNTS = {fSeg:0 for fSeg in FSEGS}

# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    if self.SP is not None:
        for fSeg in FSEGS:
            self.HistInit('Lxy_{}'.format(FSEGS[fSeg]['tag']), ';gen L_{xy} [cm];Efficiency', 800, 0., 800.)

# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    if self.TRIGGER and self.SP is not None:
        if not Selections.passedTrigger(E): return

    Event = E.getPrimitives('EVENT')

    # no Lxy sig
    CUTSTRING = '_Combined_NS_NH_FPTE_HLT_REP_PT_TRK_NDT_DCA_PC_LXYE_MASS_CHI2_VTX_COSA_NPP_OS'
    if 'DoubleMuon' in self.NAME:
        CUTSTRING += '_IDPHI'
    else:
        CUTSTRING += '_DPHI'

    DSAmuons = E.getPrimitives('DSAMUON')
    PATmuons = E.getPrimitives('PATMUON')
    Dimuons3 = E.getPrimitives('DIMUON')

    eventWeight = 1.
    try:
        eventWeight = 1. if Event.weight > 0. else -1.
    except:
        pass

    # gen stuff
    if self.SP is not None:
        if '4Mu' in self.NAME:
            mu11, mu12, mu21, mu22, X1, X2, H, P, extramu = E.getPrimitives('GEN')
            genMuons = (mu11, mu12, mu21, mu22)
            genMuonPairs = ((mu11, mu12), (mu21, mu22))
        elif '2Mu2J' in self.NAME:
            mu1, mu2, j1, j2, X, XP, H, P, extramu = E.getPrimitives('GEN')
            genMuons = (mu1, mu2)
            genMuonPairs = ((mu1, mu2),)

    # do the selection
    selectedDimuons, selectedDSAmuons, selectedPATmuons, DSADimuons = {}, {}, {}, {}
    for fSeg in FSEGS:
        # fSeg was a keyword here controlling the fSeg parameter, now 0.66
        selectedDimuons[fSeg], selectedDSAmuons[fSeg], selectedPATmuons[fSeg] = Selector.SelectObjects(E, CUTSTRING, Dimuons3, DSAmuons, PATmuons)
        if selectedDimuons[fSeg] is None:
            DSADimuons[fSeg] = []
            continue
        DSADimuons[fSeg] = [dim for dim in selectedDimuons[fSeg] if dim.composition == 'DSA']

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

    # meh
    for fSeg in FSEGS:

        # do the signal matching
        if self.SP is not None:
            if len(genMuonPairs) == 1:
                genMuonPair = genMuonPairs[0]
                dimuonMatches, muonMatches, exitcode = matchedDimuons(genMuonPair, DSADimuons[fSeg])
                if len(dimuonMatches) > 0:
                    realMatches = {0:dimuonMatches[0]}
                else:
                    realMatches = {}
            else:
                realMatches, dimuonMatches, muon0Matches, muon1Matches = matchedDimuonPairs(genMuonPairs, DSADimuons[fSeg])

            for pairIndex in realMatches:
                genMuon = genMuonPairs[pairIndex][0]
                self.HISTS['Lxy_{}'.format(FSEGS[fSeg]['tag'])].Fill(genMuon.Lxy())

        else:
            self.COUNTS[fSeg] += len(DSADimuons[fSeg])

# cleanup function for Analyzer class
def end(self, PARAMS=None):
    if self.SP is None:
        print 'Data{:1s} {:3d} {:3d} {:3d} {:3d}'.format(self.NAME[17], *(self.COUNTS[fSeg] for fSeg in (.9999, .7499, .6599, .4599)))

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

    # write plots
    analyzer.writeHistograms('roots/mcbg/SegMatchPlots{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else ''))
