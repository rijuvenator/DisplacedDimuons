import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Analysis.RootTools as RT
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedDimuons, numberOfParallelPairs
import DisplacedDimuons.Analysis.Selector as Selector
import DisplacedDimuons.Analysis.PrimitivesPrinter as Printer

Printer.COLORON = True

DELTARS = {
    .0  : {'tag':'00'},
    .05 : {'tag':'05'},
    .10 : {'tag':'10'},
    .15 : {'tag':'15'},
}

#### CLASS AND FUNCTION DEFINITIONS ####
# setup function for Analyzer class
def begin(self, PARAMS=None):
    self.COUNTS = {deltaR:0 for deltaR in DELTARS}

# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    if self.SP is not None:
        for deltaR in DELTARS:
            self.HistInit('Lxy_{}'.format(DELTARS[deltaR]['tag']), ';gen L_{xy} [cm];Efficiency', 800, 0., 800.)

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
    for deltaR in DELTARS:
        # deltaR was a keyword here controlling the deltaR parameter, now 0.1 with PP
        selectedDimuons[deltaR], selectedDSAmuons[deltaR], selectedPATmuons[deltaR] = Selector.SelectObjects(E, CUTSTRING, Dimuons3, DSAmuons, PATmuons, deltaR=deltaR)
        if selectedDimuons[deltaR] is None:
            DSADimuons[deltaR] = []
            continue
        DSADimuons[deltaR] = [dim for dim in selectedDimuons[deltaR] if dim.composition == 'DSA']

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
    for deltaR in DELTARS:

        # do the signal matching
        if self.SP is not None:
            if len(genMuonPairs) == 1:
                genMuonPair = genMuonPairs[0]
                dimuonMatches, muonMatches, exitcode = matchedDimuons(genMuonPair, DSADimuons[deltaR])
                if len(dimuonMatches) > 0:
                    realMatches = {0:dimuonMatches[0]}
                else:
                    realMatches = {}
            else:
                realMatches, dimuonMatches, muon0Matches, muon1Matches = matchedDimuonPairs(genMuonPairs, DSADimuons[deltaR])

            for pairIndex in realMatches:
                genMuon = genMuonPairs[pairIndex][0]
                self.HISTS['Lxy_{}'.format(DELTARS[deltaR]['tag'])].Fill(genMuon.Lxy())

        else:
            self.COUNTS[deltaR] += len(DSADimuons[deltaR])

# cleanup function for Analyzer class
def end(self, PARAMS=None):
    if self.SP is None:
        print 'Data{:1s} {:3d} {:3d} {:3d} {:3d}'.format(self.NAME[17], *(self.COUNTS[deltaR] for deltaR in (0., .05, .1, .15)))

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
