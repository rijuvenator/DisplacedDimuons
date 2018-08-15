import math
import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import findDimuon

# CONFIG stores the axis and function information so that histograms can be filled and declared in a loop
CONFIG = {
    'pT'      : {'AXES':( 0., 500.   ), 'LAMBDA': lambda dimuon: dimuon.pt      , 'PRETTY':'p_{T} [GeV]'    },
    'eta'     : {'AXES':(-3., 3.     ), 'LAMBDA': lambda dimuon: dimuon.eta     , 'PRETTY':None             },
    'Lxy'     : {'AXES':( 0., 800.   ), 'LAMBDA': lambda dimuon: dimuon.Lxy()   , 'PRETTY':'L_{xy} [cm]'    },
    'LxySig'  : {'AXES':( 0., 20.    ), 'LAMBDA': lambda dimuon: dimuon.LxySig(), 'PRETTY':None             },
    'vtxChi2' : {'AXES':( 0., 5.     ), 'LAMBDA': lambda dimuon: dimuon.normChi2, 'PRETTY':None             },
    'deltaR'  : {'AXES':( 0., 5.     ), 'LAMBDA': lambda dimuon: dimuon.deltaR  , 'PRETTY':'#DeltaR(#mu#mu)'},
    'mass'    : {'AXES':( 0., 1000.  ), 'LAMBDA': lambda dimuon: dimuon.mass    , 'PRETTY':'M(#mu#mu) [GeV]'},
    'deltaPhi': {'AXES':( 0., math.pi), 'LAMBDA': lambda dimuon: dimuon.deltaPhi, 'PRETTY':None             },
    'cosAlpha': {'AXES':(-1., 1.     ), 'LAMBDA': lambda dimuon: dimuon.cosAlpha, 'PRETTY':None             },
    'pTT'     : {'AXES':( 0., 100.   ), 'LAMBDA': None                          , 'PRETTY':'p_{T,p} [GeV]'  }
}

# define some additional functions
def getPTT(dimuon, which='1'):
    muon = getattr(dimuon, 'mu'+which)
    dimPT = dimuon.p3.Proj2D()
    muPT  = muon  .p3.Proj2D()
    return muPT.Cross(dimPT).Mag() / dimPT.Mag()

def getLxyErr(dimuon):
    return CONFIG['Lxy']['LAMBDA'](dimuon)/CONFIG['LxySig']['LAMBDA'](dimuon)

# actually set the lambda for pTT -- that's why it had to be None before
CONFIG['pTT']['LAMBDA'] = getPTT

# EXTRACONFIG stores some information about additional histograms
EXTRACONFIG = {
    'LxySigVSLxy'      : {},
    'LxyErrVSLxy'      : {},
    'deltaRVSdeltaPhi' : {},
    'nDimuon'          : {}
}

EXTRACONFIG['LxySigVSLxy'     ]['TITLE' ] = ';' + CONFIG['Lxy']['PRETTY']             + ';' + Selections.PrettyTitles['LxySig'] + ';Counts'
EXTRACONFIG['LxyErrVSLxy'     ]['TITLE' ] = ';' + CONFIG['Lxy']['PRETTY']             + ';' + '#sigma_{L_{xy}} [cm]'            + ';Counts'
EXTRACONFIG['deltaRVSdeltaPhi']['TITLE' ] = ';' + Selections.PrettyTitles['deltaPhi'] + ';' + CONFIG['deltaR']['PRETTY']        + ';Counts'
EXTRACONFIG['nDimuon'         ]['TITLE' ] = ';Dimuon Multiplicity;Counts'

EXTRACONFIG['LxySigVSLxy'     ]['AXES'  ] = (1000,) + CONFIG['Lxy']     ['AXES'] + (1000,) + CONFIG['LxySig']['AXES']
EXTRACONFIG['LxyErrVSLxy'     ]['AXES'  ] = (1000,) + CONFIG['Lxy']     ['AXES'] + (1000,) + (0., 200.)
EXTRACONFIG['deltaRVSdeltaPhi']['AXES'  ] = (1000,) + CONFIG['deltaPhi']['AXES'] + (1000,) + CONFIG['deltaR']['AXES']
EXTRACONFIG['nDimuon'         ]['AXES'  ] = (22, 0., 22.)

EXTRACONFIG['LxySigVSLxy'     ]['LAMBDA'] = (CONFIG['Lxy']['LAMBDA']     , CONFIG['LxySig']['LAMBDA'])
EXTRACONFIG['LxyErrVSLxy'     ]['LAMBDA'] = (CONFIG['Lxy']['LAMBDA']     , getLxyErr                 )
EXTRACONFIG['deltaRVSdeltaPhi']['LAMBDA'] = (CONFIG['deltaPhi']['LAMBDA'], CONFIG['deltaR']['LAMBDA'])
EXTRACONFIG['nDimuon'         ]['LAMBDA'] = None

#### CLASS AND FUNCTION DEFINITIONS ####
# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    for KEY in CONFIG:

        # the pretty strings are mostly in the cut dictionary
        # so use it if it's None
        # but use the string given if not
        XTIT = Selections.PrettyTitles[KEY] if CONFIG[KEY]['PRETTY'] is None else CONFIG[KEY]['PRETTY']

        if True:
            self.HistInit('Dim_'+KEY           , ';'+XTIT+';Counts', 1000, *CONFIG[KEY]['AXES'])

        if self.SP is not None:
            self.HistInit('Dim_'+KEY+'_Matched', ';'+XTIT+';Counts', 1000, *CONFIG[KEY]['AXES'])

    for KEY in EXTRACONFIG:
        TITLE = EXTRACONFIG[KEY]['TITLE']
        AXES  = EXTRACONFIG[KEY]['AXES']
        self.HistInit('Dim_'+KEY, TITLE, *AXES)
        if self.SP is not None and KEY != 'nDimuon':
            self.HistInit('Dim_'+KEY+'_Matched', TITLE, *AXES)

# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    Event    = E.getPrimitives('EVENT'  )
    DSAmuons = E.getPrimitives('DSAMUON')
    Dimuons  = E.getPrimitives('DIMUON' )

    eventWeight = 1.
    try:
        eventWeight = 1. if Event.weight > 0. else -1.
    except:
        pass

    # whether to BLIND. Could depend on Analyzer parameters, which is why it's here.
    BLIND = True if 'Blind' in self.CUTS else False

    # modify this to determine what type of selections to apply, if any
    SelectDimuons    = False
    SelectMuons      = False
    SelectMuons_pT30 = True if 'pT30' in self.CUTS else False

    # require dimuons to pass all selections and the DSA muons to pass all selections
    if SelectDimuons and SelectMuons:
        DSASelections    = [Selections.MuonSelection(muon) for muon in DSAmuons]
        DimuonSelections = [Selections.DimuonSelection(dimuon) for dimuon in Dimuons ]
        selectedDSAmuons = [mu for idx,mu in enumerate(DSAmuons) if DSASelections[idx]]
        selectedDimuons  = [dim for idx,dim in enumerate(Dimuons) if DimuonSelections[idx] and DSASelections[dim.idx1] and DSASelections[dim.idx2]]

    # don't require dimuons to pass all selections, but require DSA muons to pass all selections
    elif not SelectDimuons and SelectMuons:
        DSASelections    = [Selections.MuonSelection(muon) for muon in DSAmuons]
        selectedDSAmuons = [mu for idx,mu in enumerate(DSAmuons) if DSASelections[idx]]
        selectedDimuons  = [dim for idx,dim in enumerate(Dimuons) if DSASelections[dim.idx1] and DSASelections[dim.idx2]]

    # don't require dimuons to pass all selections, and require DSA muons to pass only the pT cut
    elif not SelectDimuons and SelectMuons_pT30:
        DSASelections    = [Selections.MuonSelection(muon, cutList=('pT',)) for muon in DSAmuons]
        selectedDSAmuons = [mu for idx,mu in enumerate(DSAmuons) if DSASelections[idx]]
        selectedDimuons  = [dim for idx,dim in enumerate(Dimuons) if DSASelections[dim.idx1] and DSASelections[dim.idx2]]

    # don't require dimuons to pass all selections, and don't require DSA muons to pass all selections, either
    elif not SelectDimuons and not SelectMuons:
        selectedDSAmuons = DSAmuons
        selectedDimuons  = Dimuons

    # fill histograms for every dimuon
    for dimuon in selectedDimuons:
        # data blinding!
        if BLIND:
            if dimuon.LxySig() > 3. or dimuon.mu1.d0Sig() > 3. or dimuon.mu2.d0Sig() > 3.:
                continue
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
        if self.TRIGGER:
            if not Selections.passedTrigger(E): return
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
            dimuon, exitcode, muonMatches, oMuonMatches = findDimuon(genMuonPair, selectedDSAmuons, selectedDimuons)

            if dimuon is not None:
                for KEY in CONFIG:
                    self.HISTS['Dim_'+KEY+'_Matched'].Fill(CONFIG[KEY]['LAMBDA'](dimuon), eventWeight)
                for KEY in EXTRACONFIG:
                    if EXTRACONFIG[KEY]['LAMBDA'] is None: continue
                    F1 = EXTRACONFIG[KEY]['LAMBDA'][0]
                    F2 = EXTRACONFIG[KEY]['LAMBDA'][1]
                    self.HISTS['Dim_'+KEY+'_Matched'].Fill(F1(dimuon), F2(dimuon), eventWeight)

#### RUN ANALYSIS ####
if __name__ == '__main__':
    ARGS = Analyzer.PARSER.parse_args()
    Analyzer.setSample(ARGS)
    for METHOD in ('declareHistograms', 'analyze'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])
    analyzer = Analyzer.Analyzer(
        ARGS        = ARGS,
        BRANCHKEYS  = ('EVENT', 'GEN', 'DSAMUON', 'DIMUON', 'TRIGGER'),
    )
    analyzer.writeHistograms('roots/DimuonPlots{}{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else '', ARGS.CUTS))
