import math
import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedDimuons, matchedTrigger, applyPairingCriteria


# CONFIG stores the axis and function information so that histograms can be filled and declared in a loop
CONFIG = {
    'vtxChi2' : {'AXES':(1000,      0., 500.   ), 'LAMBDA': lambda dim: dim.normChi2                      , 'PRETTY':'vtx #chi^{2}/dof'      },
}

#### CLASS AND FUNCTION DEFINITIONS ####
# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    for KEY in CONFIG:

        XTIT = CONFIG[KEY]['PRETTY']

        if True:
            self.HistInit('Dim_'+KEY           , ';'+XTIT+';Counts', *CONFIG[KEY]['AXES'])

        if self.SP is not None:
            self.HistInit('Dim_'+KEY+'_Matched', ';'+XTIT+';Counts', *CONFIG[KEY]['AXES'])

    self.HistInit('Lxy2D'         , ';gen L_{xy} [cm];reco L_{xy} [cm];Counts', 1000, 0., 500., 1000, 0., 500.)
    self.HistInit('Lxy2D-LxySig10', ';gen L_{xy} [cm];reco L_{xy} [cm];Counts', 1000, 0., 500., 1000, 0., 500.)

# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    if self.TRIGGER and self.SP is not None:
        if not Selections.passedTrigger(E): return
    Event    = E.getPrimitives('EVENT'  )
    DSAmuons = E.getPrimitives('DSAMUON')
    Dimuons  = E.getPrimitives('DIMUON' )
    Vertex   = E.getPrimitives('VERTEX' )

    eventWeight = 1.
    try:
        eventWeight = 1. if Event.weight > 0. else -1.
    except:
        pass

    # decide what set of cuts to apply based on self.CUTS cut string
    ALL       = 'All'       in self.CUTS
    PROMPT    = '_Prompt'   in self.CUTS
    NOPROMPT  = '_NoPrompt' in self.CUTS
    NSTATIONS = '_NS'       in self.CUTS
    NMUONHITS = '_NH'       in self.CUTS
    FPTERR    = '_FPTE'     in self.CUTS
    PT        = '_PT'       in self.CUTS
    HLT       = '_HLT'      in self.CUTS
    PC        = '_PC'       in self.CUTS
    LXYERR    = '_LXYE'     in self.CUTS
    MASS      = '_M'        in self.CUTS

    def boolsToMuonCutList(NSTATIONS, NMUONHITS, FPTERR, PT):
        cutList = []
        if NSTATIONS:
            cutList.append('b_nStations')
        if NMUONHITS:
            cutList.append('b_nMuonHits')
        if FPTERR:
            cutList.append('b_FPTE')
        if PT:
            cutList.append('b_pT')
        return cutList

    def boolsToDimuonCutList(LXYERR, MASS):
        cutList = []
        if LXYERR:
            cutList.append('b_LxyErr')
        if MASS:
            cutList.append('b_mass')
        return cutList

    # require DSA muons to pass all selections, and require dimuons to pass all selections except LxySig and deltaPhi
    if ALL:
        DSASelections    = [Selections.MuonSelection(muon) for muon in DSAmuons]
        DimuonSelections = [Selections.DimuonSelection(dimuon) for dimuon in Dimuons ]
        selectedDSAmuons = [mu for idx,mu in enumerate(DSAmuons) if DSASelections[idx]]
        selectedDimuons  = [dim for idx,dim in enumerate(Dimuons) if DimuonSelections[idx].allExcept('LxySig', 'deltaPhi') and DSASelections[dim.idx1] and DSASelections[dim.idx2]]

    # no cuts
    else:
        selectedDSAmuons = DSAmuons
        selectedDimuons  = Dimuons

    # for PROMPT and NOPROMPT event selections
    if PROMPT or NOPROMPT:
        highLxySigExists = False
        for dimuon in Dimuons:
            if dimuon.LxySig() > 3.:
                highLxySigExists = True
                break

        # return if there are LxySig > 3
        if PROMPT:
            if highLxySigExists:
                return
        # return if there are NO LxySig > 3 -- that's category 1
        elif NOPROMPT:
            if not highLxySigExists:
                return

    if PROMPT or NOPROMPT:
        # compute all the baseline selection booleans
        DSASelections = [Selections.MuonSelection(muon, cutList='BaselineMuonCutList') for muon in DSAmuons]

        # figure out which cuts we actually care about
        cutList = boolsToMuonCutList(NSTATIONS, NMUONHITS, FPTERR, PT)

        # no selection
        if len(cutList) == 0:
            selectedDSAmuons = DSAmuons
            selectedDimuons  = Dimuons
        # cutList is some nonzero list, meaning keep only the muons that pass the cut keys in cutList
        else:
            selectedDSAmuons = [mu for i,mu in enumerate(DSAmuons) if DSASelections[i].allOf(*cutList)]
            selectedOIndices = [mu.idx for mu in selectedDSAmuons]
            selectedDimuons  = [dim for dim in Dimuons if dim.idx1 in selectedOIndices and dim.idx2 in selectedOIndices]

    # apply HLT RECO matching
    if HLT:
        HLTPaths, HLTMuons, L1TMuons = E.getPrimitives('TRIGGER')
        DSAMuonsForHLTMatch = [mu for mu in selectedDSAmuons if abs(mu.eta) < 2.]
        HLTMuonMatches = matchedTrigger(HLTMuons, DSAMuonsForHLTMatch)
        if not any([HLTMuonMatches[ij]['matchFound'] for ij in HLTMuonMatches]): return

    # apply pairing criteria and transform selectedDimuons
    if PC:
        selectedDimuons = applyPairingCriteria(selectedDSAmuons, selectedDimuons)

    if PROMPT or NOPROMPT:
        # compute all the baseline selection booleans
        DimuonSelections = {dim.ID:Selections.DimuonSelection(dim, cutList='BaselineDimuonCutList') for dim in selectedDimuons}

        # figure out which cuts we actually care about
        cutList = boolsToDimuonCutList(LXYERR, MASS)

        # cutList is some nonzero list, meaning keep only the muons that pass the cut keys in cutList
        if len(cutList) > 0:
            selectedDimuons = [dim for dim in selectedDimuons if DimuonSelections[dim.ID].allOf(*cutList)]

    # for the MC/Data events, skip events with no dimuons, but not for "no selection"
    if (PROMPT or NOPROMPT) and NSTATIONS:
        if len(selectedDimuons) == 0: return

    # also filter selectedDSAmuons to only be of those indices that are in the final dimuons
    if PROMPT or NOPROMPT:
        selectedOIndices = []
        for dim in selectedDimuons:
            selectedOIndices.append(dim.idx1)
            selectedOIndices.append(dim.idx2)
        selectedOIndices = list(set(selectedOIndices))
        selectedDSAmuons = [mu for mu in selectedDSAmuons if mu.idx in selectedOIndices]

    # fill histograms for every dimuon
    for dimuon in selectedDimuons:
        for KEY in CONFIG:
            self.HISTS['Dim_'+KEY].Fill(CONFIG[KEY]['LAMBDA'](dimuon), eventWeight)
            if self.SP is None:
                if CONFIG[KEY]['LAMBDA'](dimuon) > 50.:
                    self.HISTS['Lxy2D'].Fill(50., dimuon.Lxy())
                    if dimuon.LxySig() > 10.:
                        self.HISTS['Lxy2D-LxySig10'].Fill(50., dimuon.Lxy())

    # get gen particles if this is a signal sample
    if self.SP is not None:
        if '4Mu' in self.NAME:
            mu11, mu12, mu21, mu22, X1, X2, H, P, extramu = E.getPrimitives('GEN')
            genMuons = (mu11, mu12, mu21, mu22)
            genMuonPairs = ((mu11, mu12), (mu21, mu22))
        elif '2Mu2J' in self.NAME:
            mu1, mu2, j1, j2, X, XP, H, P, extramu = E.getPrimitives('GEN')
            genMuons = (mu1, mu2)
            genMuonPairs = ((mu1, mu2),)

        # fill histograms only for matched reco muons
        for genMuonPair in genMuonPairs:
            # require genMuonPair to be within acceptance
            # don't do it for now
            #genMuonSelection = Selections.AcceptanceSelection(genMuonPair)

            # find the matching dimuon, if any, and fill
            dimuonMatches, muonMatches, exitcode = matchedDimuons(genMuonPair, selectedDimuons)

            if len(dimuonMatches) > 0:
                for match in dimuonMatches:
                    dimuon = match['dim']
                    for KEY in CONFIG:
                        self.HISTS['Dim_'+KEY+'_Matched'].Fill(CONFIG[KEY]['LAMBDA'](dimuon), eventWeight)
                        if CONFIG[KEY]['LAMBDA'](dimuon) > 50.:
                            self.HISTS['Lxy2D'].Fill(genMuonPair[0].Lxy(), dimuon.Lxy())
                            if dimuon.LxySig() > 10.:
                                self.HISTS['Lxy2D-LxySig10'].Fill(genMuonPair[0].Lxy(), dimuon.Lxy())
                                print '{:6.3f} {:6.3f} {:6.3f} {:6.3f}'.format(dimuon.Lxy(), genMuonPair[0].Lxy(), dimuon.LxyErr(), abs(dimuon.Lxy()-genMuonPair[0].Lxy())/dimuon.LxyErr())
                                #print Event
                                #print genMuonPair[0]
                                #print genMuonPair[1]
                                #print dimuon
                                #print '=' * 20

#### RUN ANALYSIS ####
if __name__ == '__main__':
    ARGS = Analyzer.PARSER.parse_args()
    Analyzer.setSample(ARGS)
    for METHOD in ('declareHistograms', 'analyze'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])
    analyzer = Analyzer.Analyzer(
        ARGS        = ARGS,
        BRANCHKEYS  = ('EVENT', 'GEN', 'DSAMUON', 'DIMUON', 'TRIGGER', 'VERTEX'),
    )
    analyzer.writeHistograms('roots/mcbg/Chi2Plots{}{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else '', ARGS.CUTS))
