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
    self.HistInit('Prox_PD_deltaR', ';Prox #DeltaR (PD);Counts', 100, 0., 0.4)
    self.HistInit('Prox_PP_deltaR', ';Prox #DeltaR (PP);Counts', 100, 0., 0.4)
    self.HistInit('Seg_PD_deltaR' , ';Seg #DeltaR (PD);Counts' , 100, 0., 0.4)
    self.HistInit('Seg_PP_deltaR' , ';Seg #DeltaR (PP);Counts' , 100, 0., 0.4)

    self.HistInit('Prox_PD_fSeg', ';Prox f(Matched Segs);Counts', 20, 0., 1.)
    self.HistInit('Prox_PP_fSeg', ';Prox f(Matched Segs);Counts', 20, 0., 1.)
    self.HistInit('Seg_PD_fSeg' , ';Seg f(Matched Segs);Counts' , 20, 0., 1.)
    self.HistInit('Seg_PP_fSeg' , ';Seg f(Matched Segs);Counts' , 20, 0., 1.)

    if self.SP is not None:
        self.HistInit('Prox_PD_deltaR_Matched', ';Prox #DeltaR (PD);Counts', 100, 0., 0.4)
        self.HistInit('Prox_PP_deltaR_Matched', ';Prox #DeltaR (PP);Counts', 100, 0., 0.4)
        self.HistInit('Seg_PD_deltaR_Matched' , ';Seg #DeltaR (PD);Counts' , 100, 0., 0.4)
        self.HistInit('Seg_PP_deltaR_Matched' , ';Seg #DeltaR (PP);Counts' , 100, 0., 0.4)

        self.HistInit('Prox_PD_fSeg_Matched', ';Prox f(Matched Segs);Counts', 20, 0., 1.)
        self.HistInit('Prox_PP_fSeg_Matched', ';Prox f(Matched Segs);Counts', 20, 0., 1.)
        self.HistInit('Seg_PD_fSeg_Matched' , ';Seg f(Matched Segs);Counts' , 20, 0., 1.)
        self.HistInit('Seg_PP_fSeg_Matched' , ';Seg f(Matched Segs);Counts' , 20, 0., 1.)

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

    # do the selection
    selectedDimuons, selectedDSAmuons, selectedPATmuons = Selector.SelectObjects(E, CUTSTRING, Dimuons3, DSAmuons, PATmuons)
    if selectedDimuons is None:
        DSADimuons = []
        return
    DSADimuons = [dim for dim in selectedDimuons if dim.composition == 'DSA']

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

        if len(genMuonPairs) == 1:
            genMuonPair = genMuonPairs[0]
            dimuonMatches, muonMatches, exitcode = matchedDimuons(genMuonPair, selectedDimuons)#DSADimuons)
            if len(dimuonMatches) > 0:
                realMatches = {0:dimuonMatches[0]}
            else:
                realMatches = {}
        else:
            realMatches, dimuonMatches, muon0Matches, muon1Matches = matchedDimuonPairs(genMuonPairs, selectedDimuons)# DSADimuons)


    # the other plots
    for dim in DSADimuons:

        matched = None
        if self.SP is not None and dim.ID in [realMatches[pIdx]['dim'].ID for pIdx in realMatches]:
            matched = True

        mu1, mu2 = getOriginalMuons(dim, DSAmuons)

        for mu in (mu1, mu2):
            for matchType in ('Prox', 'Seg'):
                for vectorType in ('PD', 'PP'):
                    match = getattr(mu, '{}Match{}'.format(matchType, vectorType))
                    if match.idx is not None:
                        if matchType == 'Prox':
                            iterables = [(match.idx, match.deltaR, match.nSeg, mu.nSegments)]
                        else:
                            iterables = [(a, b, c, mu.nSegments) for a, b, c in zip(match.idx, match.deltaR, match.nSeg)]

                        for idx, deltaR, nSeg, nDSASeg in iterables:
                            self.HISTS['{}_{}_deltaR'.format(matchType, vectorType)].Fill(deltaR)
                            self.HISTS['{}_{}_fSeg'  .format(matchType, vectorType)].Fill(float(nSeg)/nDSASeg if nDSASeg != 0 else 0.)

                            if matched is not None:
                                self.HISTS['{}_{}_deltaR_Matched'.format(matchType, vectorType)].Fill(deltaR)
                                self.HISTS['{}_{}_fSeg_Matched'  .format(matchType, vectorType)].Fill(float(nSeg)/nDSASeg if nDSASeg != 0 else 0.)

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

    # write plots
    analyzer.writeHistograms('roots/mcbg/SegMatchPlots{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else ''))
