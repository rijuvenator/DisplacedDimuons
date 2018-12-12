import math
import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedDimuons, matchedTrigger, applyPairingCriteria


# CONFIG stores the axis and function information so that histograms can be filled and declared in a loop
CONFIG = {
    'pT'      : {'AXES':(1500,      0., 1500.  ), 'LAMBDA': lambda dim: dim.pt                            , 'PRETTY':'p_{T} [GeV]'           },
    'pTCosPhi': {'AXES':(1500,      0., 1500.  ), 'LAMBDA': lambda dim: math.cos(dim.deltaPhi)*dim.pt     , 'PRETTY':'p_{T}cos(#Phi) [GeV]'  },
    'pTOverM' : {'AXES':(1000,      0., 50.    ), 'LAMBDA': lambda dim: dim.pt/dim.mass                   , 'PRETTY':'p_{T}/M(#mu#mu)'       },
    'eta'     : {'AXES':(1000,     -3., 3.     ), 'LAMBDA': lambda dim: dim.eta                           , 'PRETTY':'#eta'                  },
    'Lxy'     : {'AXES':(1000,      0., 800.   ), 'LAMBDA': lambda dim: dim.Lxy()                         , 'PRETTY':'L_{xy} [cm]'           },
    'LxySig'  : {'AXES':(2000,      0., 200.   ), 'LAMBDA': lambda dim: dim.LxySig()                      , 'PRETTY':'L_{xy}/#sigma_{L_{xy}}'},
    'LxyErr'  : {'AXES':(1000,      0., 100.   ), 'LAMBDA': lambda dim: dim.LxyErr()                      , 'PRETTY':'#sigma_{L_{xy}} [cm]'  },
    'vtxChi2' : {'AXES':(1000,      0., 50.    ), 'LAMBDA': lambda dim: dim.normChi2                      , 'PRETTY':'vtx #chi^{2}/dof'      },
    'deltaR'  : {'AXES':(1000,      0., 5.     ), 'LAMBDA': lambda dim: dim.deltaR                        , 'PRETTY':'#DeltaR(#mu#mu)'       },
    'deltaEta': {'AXES':(1000,     -5., 5.     ), 'LAMBDA': lambda dim: dim.mu1.eta-dim.mu2.eta           , 'PRETTY':'#Delta#eta(#mu#mu)'    },
    'deltaphi': {'AXES':(1000,-math.pi, math.pi), 'LAMBDA': lambda dim: dim.mu1.p4.DeltaPhi(dim.mu2.p4)   , 'PRETTY':'#Delta#phi(#mu#mu)'    },
    'mass'    : {'AXES':(1000,      0., 1000.  ), 'LAMBDA': lambda dim: dim.mass                          , 'PRETTY':'M(#mu#mu) [GeV]'       },
    'deltaPhi': {'AXES':(1000,      0., math.pi), 'LAMBDA': lambda dim: dim.deltaPhi                      , 'PRETTY':'#Delta#Phi'            },
    'cosAlpha': {'AXES':(1000,     -1., 1.     ), 'LAMBDA': lambda dim: dim.cosAlpha                      , 'PRETTY':'cos(#alpha)'           },
}

# EXTRACONFIG stores some information about additional histograms
EXTRACONFIG = {
    'nDimuon' : {}
}

for q1 in ('Lxy', 'LxySig', 'LxyErr', 'deltaR', 'deltaEta', 'deltaphi', 'mass'):
    for q2 in ('Lxy', 'deltaPhi'):
        if q1 == q2: continue
        if q1 == 'mass' and q2 == 'Lxy': continue
        key = q1 + 'VS' + q2
        EXTRACONFIG[key] = {}
        TITLE1 = CONFIG[q1]['PRETTY']
        TITLE2 = CONFIG[q2]['PRETTY']
        EXTRACONFIG[key]['TITLE' ] = ';' + TITLE2 + ';' + TITLE1 + ';Counts'
        EXTRACONFIG[key]['AXES'  ] = CONFIG[q2]['AXES'] + CONFIG[q1]['AXES']
        EXTRACONFIG[key]['LAMBDA'] = (CONFIG[q2]['LAMBDA'], CONFIG[q1]['LAMBDA'])

EXTRACONFIG['nDimuon']['TITLE' ] = ';Dimuon Multiplicity;Counts'
EXTRACONFIG['nDimuon']['AXES'  ] = (22, 0., 22.)
EXTRACONFIG['nDimuon']['LAMBDA'] = None

#### CLASS AND FUNCTION DEFINITIONS ####
# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    for KEY in CONFIG:

        XTIT = CONFIG[KEY]['PRETTY']

        if True:
            self.HistInit('Dim_'+KEY           , ';'+XTIT+';Counts', *CONFIG[KEY]['AXES'])

        if self.SP is not None:
            self.HistInit('Dim_'+KEY+'_Matched', ';'+XTIT+';Counts', *CONFIG[KEY]['AXES'])

    for KEY in EXTRACONFIG:
        TITLE = EXTRACONFIG[KEY]['TITLE']
        AXES  = EXTRACONFIG[KEY]['AXES']
        self.HistInit('Dim_'+KEY, TITLE, *AXES)
        if self.SP is not None:
            self.HistInit('Dim_'+KEY+'_Matched', TITLE, *AXES)

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

        for KEY in EXTRACONFIG:
            if EXTRACONFIG[KEY]['LAMBDA'] is None: continue
            F1 = EXTRACONFIG[KEY]['LAMBDA'][0]
            F2 = EXTRACONFIG[KEY]['LAMBDA'][1]
            self.HISTS['Dim_'+KEY].Fill(F1(dimuon), F2(dimuon), eventWeight)
    self.HISTS['Dim_nDimuon'].Fill(len(selectedDimuons), eventWeight)

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
                    for KEY in EXTRACONFIG:
                        if EXTRACONFIG[KEY]['LAMBDA'] is None: continue
                        F1 = EXTRACONFIG[KEY]['LAMBDA'][0]
                        F2 = EXTRACONFIG[KEY]['LAMBDA'][1]
                        self.HISTS['Dim_'+KEY+'_Matched'].Fill(F1(dimuon), F2(dimuon), eventWeight)
            self.HISTS['Dim_nDimuon_Matched'].Fill(len(dimuonMatches))

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
    analyzer.writeHistograms('roots/DimuonPlots{}{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else '', ARGS.CUTS))
