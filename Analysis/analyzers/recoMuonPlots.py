import math
import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Analysis.Primitives as Primitives
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedMuons, matchedDimuons

# CONFIG stores the axis and function information so that histograms can be filled and declared in a loop
HEADERS = ('AXES', 'LAMBDA', 'PRETTY')
VALUES = (
    ('pT'       , (1000, 0., 500.), lambda muon: muon.pt                                     , 'p_{T} [GeV]'               ),
    ('eta'      , (1000,-3., 3.  ), lambda muon: muon.eta                                    , '#eta'                      ),
    ('d0'       , (1000, 0., 200.), lambda muon: muon.d0()                                   , 'd_{0} [cm]'                ),
    ('d0Sig'    , (1000, 0., 20. ), lambda muon: muon.d0Sig()                                , '|d_{0}|/#sigma_{d_{0}}'    ),
    ('dz'       , (1000, 0., 200.), lambda muon: muon.dz()                                   , 'd_{z} [cm]'                ),
    ('dzSig'    , (1000, 0., 20. ), lambda muon: muon.dzSig()                                , '|d_{z}|/#sigma_{d_{z}}'    ),
    ('d0Lin'    , (1000, 0., 200.), lambda muon: muon.d0(extrap='LIN')                       , 'lin d_{0} [cm]'            ),
    ('d0SigLin' , (1000, 0., 20. ), lambda muon: muon.d0Sig(extrap='LIN')                    , 'lin |d_{0}|/#sigma_{d_{0}}'),
    ('dzLin'    , (1000, 0., 200.), lambda muon: muon.dz(extrap='LIN')                       , 'lin d_{z} [cm]'            ),
    ('dzSigLin' , (1000, 0., 20. ), lambda muon: muon.dzSig(extrap='LIN')                    , 'lin |d_{z}|/#sigma_{d_{z}}'),
    ('normChi2' , (1000, 0., 20. ), lambda muon: muon.chi2/muon.ndof if muon.ndof != 0 else 0, '#mu #chi^{2}/dof'          ),
    ('nMuonHits', (50  , 0., 50. ), lambda muon: muon.nMuonHits                              , 'N(Hits)'                   ),
    ('nStations', (15  , 0., 15. ), lambda muon: muon.nDTStations + muon.nCSCStations        , 'N(Stations)'               ),
    ('pTSig'    , (1000, 0.,  3. ), lambda muon: muon.ptError/muon.pt                        , '#sigma_{pT}/p_{T}'         ),
)
CONFIG = {}
for VAL in VALUES:
    CONFIG[VAL[0]] = dict(zip(HEADERS, VAL[1:]))

EXTRACONFIG = {
    'fYVSfX' : {},
    'fRVSfZ' : {}
}

EXTRACONFIG['fYVSfX']['TITLE' ] = ';x_{f} [cm];y_{f} [cm];Counts'
EXTRACONFIG['fRVSfZ']['TITLE' ] = ';z_{f} [cm];R_{f} [cm];Counts'

EXTRACONFIG['fYVSfX']['AXES'  ] = (800 , -800. , 800. , 800, -800., 800.)
EXTRACONFIG['fRVSfZ']['AXES'  ] = (1100, -1100., 1100., 800,    0., 800.)

EXTRACONFIG['fYVSfX']['LAMBDA'] = (lambda muon: muon.fhit.X(), lambda muon: muon.fhit.Y()   )
EXTRACONFIG['fRVSfZ']['LAMBDA'] = (lambda muon: muon.fhit.Z(), lambda muon: muon.fhit.Perp())

EXTRACONFIG['fYVSfX']['LAMBDA'] = (lambda muon: muon.fhit.X(), lambda muon: muon.fhit.Y()   )
EXTRACONFIG['fRVSfZ']['LAMBDA'] = (lambda muon: muon.fhit.Z(), lambda muon: muon.fhit.Perp())

#### CLASS AND FUNCTION DEFINITIONS ####
# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    for KEY in CONFIG:

        XTIT = CONFIG[KEY]['PRETTY']

        for MUON in ('DSA', 'RSA', 'REF'):
            if True:
                self.HistInit(MUON+'_'+KEY           , ';'+XTIT+';Counts', *CONFIG[KEY]['AXES'])

            if self.SP is not None:
                self.HistInit(MUON+'_'+KEY+'_Matched', ';'+XTIT+';Counts', *CONFIG[KEY]['AXES'])

    for KEY in EXTRACONFIG:
        for MUON in ('DSA', 'RSA', 'REF'):
            if True:
                self.HistInit(MUON+'_'+KEY           , EXTRACONFIG[KEY]['TITLE'], *EXTRACONFIG[KEY]['AXES'])

            if self.SP is not None:
                self.HistInit(MUON+'_'+KEY+'_Matched', EXTRACONFIG[KEY]['TITLE'], *EXTRACONFIG[KEY]['AXES'])


    for MUON in ('DSA', 'RSA', 'REF'):
        if True:
            self.HistInit(MUON+'_nMuon'           , ';Muon Multiplicity;Counts', 15  , 0., 15.)

        if self.SP is not None:
            self.HistInit(MUON+'_nMuon_Matched'   , ';Muon Multiplicity;Counts', 15  , 0., 15.)
            self.HistInit(MUON+'_deltaRGR_Matched', ';#DeltaR(gen-reco);Counts', 100 , 0., 0.3)
            self.HistInit(MUON+'_deltaRGR_Closest', ';#DeltaR(gen-reco);Counts', 100 , 0., 0.3)

# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    if self.TRIGGER and self.SP is not None:
        if not Selections.passedTrigger(E): return
    Event    = E.getPrimitives('EVENT')
    DSAmuons = E.getPrimitives('DSAMUON')
    RSAmuons = E.getPrimitives('RSAMUON')
    Dimuons  = E.getPrimitives('DIMUON' )

    Primitives.CopyExtraRecoMuonInfo(Dimuons, DSAmuons)

    eventWeight = 1.
    try:
        eventWeight = 1. if Event.weight > 0. else -1.
    except:
        pass

    # whether to BLIND. Could depend on Analyzer parameters, which is why it's here.
    ALL = True if 'All' in self.CUTS else False
    PROMPT = True if '_Prompt' in self.CUTS else False
    NOPROMPT = True if '_NoPrompt' in self.CUTS else False

    # require muons to pass all selections
    if ALL:
        DSASelections    = [Selections.MuonSelection(muon) for muon in DSAmuons]
        RSASelections    = [Selections.MuonSelection(muon) for muon in RSAmuons]
        selectedDSAmuons = [mu for idx,mu in enumerate(DSAmuons) if DSASelections[idx]]
        selectedRSAmuons = [mu for idx,mu in enumerate(RSAmuons) if RSASelections[idx]]
        selectedDimuons  = Dimuons

    # return if there are LxySig > 3
    elif PROMPT:
        highLxySigExists = False
        for dimuon in Dimuons:
            if dimuon.LxySig() > 3.:
                highLxySigExists = True
                break
        if highLxySigExists:
            return
        selectedDSAmuons = DSAmuons
        selectedRSAmuons = RSAmuons
        selectedDimuons  = Dimuons

    # return if there are NO LxySig > 3 -- that's category 1
    elif NOPROMPT:
        highLxySigExists = False
        for dimuon in Dimuons:
            if dimuon.LxySig() > 3.:
                highLxySigExists = True
                break
        if not highLxySigExists:
            return
        selectedDSAmuons = DSAmuons
        selectedRSAmuons = RSAmuons
        selectedDimuons  = Dimuons

    # don't require reco muons to pass all selections
    else:
        selectedDSAmuons = DSAmuons
        selectedRSAmuons = RSAmuons
        selectedDimuons  = Dimuons
    
    # all refitted muons
    allRefittedMuons = []
    for dimuon in selectedDimuons:
        allRefittedMuons.append(dimuon.mu1)
        allRefittedMuons.append(dimuon.mu2)

    # fill histograms for every reco muon
    for MUON, recoMuons in (('DSA', selectedDSAmuons), ('RSA', selectedRSAmuons), ('REF', allRefittedMuons)):
        self.HISTS[MUON+'_nMuon'].Fill(len(recoMuons), eventWeight)
        for muon in recoMuons:
            for KEY in CONFIG:
                self.HISTS[MUON+'_'+KEY].Fill(CONFIG[KEY]['LAMBDA'](muon), eventWeight)
            for KEY in EXTRACONFIG:
                F1 = EXTRACONFIG[KEY]['LAMBDA'][0]
                F2 = EXTRACONFIG[KEY]['LAMBDA'][1]
                self.HISTS[MUON+'_'+KEY].Fill(F1(muon), F2(muon), eventWeight)

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

        MuonMatches = {'DSA':[], 'RSA':[], 'REF':[]}
        # get matched reco muons
        for genMuon in genMuons:
            # cut genMuons outside the detector acceptance
            # don't do it for now
            #genMuonSelection = Selections.AcceptanceSelection(genMuon)

            for MUON, recoMuons in (('DSA', selectedDSAmuons), ('RSA', selectedRSAmuons)):
                MuonMatches[MUON].append(matchedMuons(genMuon, recoMuons, vertex='BS'))

        # and for refitted muons for matched dimuons
        for genMuonPair in genMuonPairs:
            for MUON in ('REF',):
                dimuonMatches, muonMatches, exitcode = matchedDimuons(genMuonPair, selectedDimuons)
                MuonMatches[MUON].append(muonMatches[0])
                MuonMatches[MUON].append(muonMatches[1])

        # fill histograms
        # for each major muon type,
        # MuonMatches contains 2 lists of matches corresponding to each gen muon
        # Each match in each of those 2 lists is a list of individual muon matches
        for MUON in ('DSA', 'RSA', 'REF'):
            for matches in MuonMatches[MUON]:
                for match in matches:
                    muon = match['muon']
                    deltaR = match['deltaR']
                    for KEY in CONFIG:
                        self.HISTS[MUON+'_'+KEY+'_Matched'].Fill(CONFIG[KEY]['LAMBDA'](muon), eventWeight)
                    for KEY in EXTRACONFIG:
                        F1 = EXTRACONFIG[KEY]['LAMBDA'][0]
                        F2 = EXTRACONFIG[KEY]['LAMBDA'][1]
                        self.HISTS[MUON+'_'+KEY+'_Matched'].Fill(F1(muon), F2(muon), eventWeight)
                    self.HISTS[MUON+'_deltaRGR_Matched'].Fill(deltaR, eventWeight)
                self.HISTS[MUON+'_nMuon_Matched'].Fill(len(matches), eventWeight)
                if len(matches) > 0:
                    self.HISTS[MUON+'_deltaRGR_Closest'].Fill(matches[0]['deltaR'], eventWeight)

#### RUN ANALYSIS ####
if __name__ == '__main__':
    ARGS = Analyzer.PARSER.parse_args()
    Analyzer.setSample(ARGS)
    for METHOD in ('declareHistograms', 'analyze'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])
    analyzer = Analyzer.Analyzer(
        ARGS        = ARGS,
        BRANCHKEYS  = ('EVENT', 'DSAMUON', 'RSAMUON', 'GEN', 'TRIGGER', 'DIMUON'),
    )
    analyzer.writeHistograms('roots/RecoMuonPlots{}{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else '', ARGS.CUTS))
