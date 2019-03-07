import math
import itertools
import operator
import numpy as np
import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Analysis.Primitives as Primitives
from DisplacedDimuons.Analysis.AnalysisTools import matchedMuons

# toggle the creation of histograms related to turn-on curves
DO_CREATE_SIMPLE_HISTS = True
DO_CREATE_TURNON_HISTS = False

# define single muon cuts
SINGLEMU_SELECTION = {
    'nStations': Selections.Cut('nStations',
        lambda muon: muon.nDTStations + muon.nCSCStations,
        operator.gt, 1),
    'nCSCDTHits': Selections.Cut('nCSCDTHits',
        lambda muon: muon.nCSCHits + muon.nDTHits,
        operator.gt, 12),
    'pTSig': Selections.Cut('pTSig',
        lambda muon: muon.ptError / muon.pt,
        operator.lt, 1.),
    'pT': Selections.Cut('pT',
        lambda muon: muon.pt,
        operator.gt, 5.),
    # 'eta': Selections.Cut('eta',
    #     lambda muon: abs(muon.eta),
    #     operator.lt, 1.2),
}

# define muon pair cuts
MUONPAIR_SELECTION = {
    # 'alpha': Selections.Cut(
    #     'alpha', lambda (m1,m2): m1.p4.Angle(m2.p4.Vect()),
    #     operator.gt, 2.9),
}

# define dimuon cuts
DIMUON_SELECTION = {
    'vtxChiSqu': Selections.Cut('vtxChiSqu',
        lambda dim: dim.normChi2,
        operator.lt, 50.),
}

# pT cuts applied to muon pairs ("L1 seed emulation"):
# (the first muon has to pass the first cut and the second muon has to pass the
# second cut) OR (the first muon has to pass the second cut and the second muon
# has to pass the first cut)
L1_pairthresholds = (5.,12.)

DO_SELECT_LARGEST_ALPHA_PAIR = False
DO_REQUIRE_OPPOSITE_HEMISPHERES = False
DO_REQUIRE_ONE_LEG_MATCHED = True
DO_REQUIRE_BOTH_LEGS_MATCHED = True
DO_REQUIRE_DIMUON_VERTEX = True

# deltaR matching threshold for reco-HLT matches
MATCHING_THRESHOLD_HLT = 0.2

# pT threshold values for matched HLT objects, applied to the turn-on curves
PTTHRESHOLDS = [23., 25., 28.]  

# additional L1 pT cuts applied consecutively to the sets of turn-on curves
L1THRESHOLDS = (0.0, 4.0, 5.0, 11.0, 12.0, 15.0)

# different dimuon populations, defined by their alpha(mu,mu) values
# define tuples of (min,max,name), corresponding to min<alpha<max and the name
# tag for the corresponding histograms.
# "(None,None,'')" is the alpha-inclusive case.
ALPHA_CATEGORIES = (
        (None, None, ''),
        (2.8, math.pi, '__2p8alphaPi'),
        (0.3, 2.8, '__0p3alpha2p8'),
        (0., 0.3, '__0p0alpha0p3'),
        (0., 2.8, '__noOppositeMuonMatch_0p0alpha2p8'),
)

# list of d0 intervals to process, "(None, None)" gives the d0-inclusive results
D0INTERVALS = [(None,None)]
# # 2.5-cm steps for small d0
D0INTERVALS += ([(i,i+2.5) for i in np.arange(0., 30., 2.5)])
# 5-cm steps for small d0
D0INTERVALS += ([(i,i+5.0) for i in np.arange(0., 30., 5.)])
# 10-cm steps for the entire d0 range
D0INTERVALS += ([(i,i+10.) for i in np.arange(0., 500., 10.)])
# custom d0 bins
# D0INTERVALS += ([(0,10),(10,50),(0,50),(50,100),(100,150),(150,250),(250,350),(250,1000),(350,1000)])

# make sure that all of the values are actually floats
D0INTERVALS = [(float(l), float(h)) if l is not None and h is not None else (l,h) for l,h in D0INTERVALS]

SINGLEMUVARIABLES = ['pT','eta','phi','charge','d0','x_fhit','y_fhit','z_fhit','nStations','nCSCDTHits','pTSig','chi2']
PAIRVARIABLES = ['pTdiff','deltaR','mass','cosAlpha','alpha','dimuonPTOverM', 'pairPT', 'chargeprod']
DIMUONVARIABLES = ['dimLxy','dimMass','dimVtxChi2','dimCosAlpha','dimLxySig']
L1RESOLUTIONVARIABLES = ['L1pTres']
L2RESOLUTIONVARIABLES = ['L2pTres']

HEADERS = ('XTITLE', 'AXES', 'LAMBDA', 'PRETTY')
VALUES  = (
    ('pT' ,           'p_{T} [GeV]',      (1000,       0.,    500.), lambda muon: muon.pt                                , 'p_{T}'   ), 
    ('eta',           '#eta'       ,      (1000,      -3.,      3.), lambda muon: muon.eta                               , '#eta'    ),
    ('phi',           '#phi'       ,      (1000, -math.pi, math.pi), lambda muon: muon.phi                               , '#phi'    ),
    ('charge',        'q(#mu)'     ,         (4,       -2,       2), lambda muon: muon.charge                            , 'q(#mu)'  ),
    ('d0' ,           'd_{0} [cm]' ,      (1000,       0.,   1100.), lambda muon: abs(muon.d0())                         , 'd_{0}'   ),
    # ('x_fhit',        'x_{innermost hit}',(1000,    -800.,    800.), lambda muon: muon.x_fhit                            , 'x_{innermost hit}'),
    # ('y_fhit',        'y_{innermost hit}',(1000,    -800.,    800.), lambda muon: muon.y_fhit                            , 'y_{innermost hit}'),
    # ('z_fhit',        'z_{innermost hit}',(1000,   -1100.,   1100.), lambda muon: muon.z_fhit                            , 'z_{innermost hit}'),
    ('chi2',          'muon #chi^{2}/ndof', (1000,    -1.,    100.), lambda muon: muon.chi2/muon.ndof if muon.ndof != 0 else -1., 'muon #chi^{2}/ndof'),
    ('nStations',     'nStations',        (  20,       0.,     20.), lambda muon: muon.nDTStations+muon.nCSCStations     , 'nStations'),
    ('nCSCDTHits',    'nCSC+DTHits',      ( 100,       0.,    100.), lambda muon: muon.nCSCHits+muon.nDTHits             , 'nCSC+DTHits'),
    ('pTSig',         '#sigma_{p_{T}} / p_{T}', (1000, 0.,     10.), lambda muon: muon.ptError / muon.pt                , '#sigma_{p_{T}} / p_{T}'),
    ('pTdiff',        '(p_{T}^{upper}-p_{T}^{lower})/p_{T}^{lower}', (1000, -10., 100.), lambda (m1,m2): (m1.pt-m2.pt)/m2.pt, 'p_{T}^{upper}-p_{T}^{lower}/p_{T}^{lower}'),
    ('deltaR',        '#Delta R',         (1000,       0.,      5.), lambda (m1,m2): m1.p4.DeltaR(m2.p4)                 , '#DeltaR(#mu#mu)'),
    ('mass',          'M_{#mu#mu}',       (1000,       0.,    500.), lambda (m1,m2): (m1.p4+m2.p4).M()                   , 'M(#mu#mu) [GeV]'),
    # ('cosAlpha',      'cos#alpha',        (1000,      -1.,      1.), lambda (m1,m2): m1.p4.Vect().Dot(m2.p4.Vect())/m1.p4.P()/m2.p4.P(),'cos(#alpha)'),
    ('alpha',         '#alpha',           (1000,       0., math.pi), lambda (m1,m2): m1.p4.Angle(m2.p4.Vect())           , 'cos(#alpha)'),
    # ('dimuonPTOverM', 'dimuon p_{T} / M', (1000,       0.,     20.), lambda (m1,m2): (m1.p4+m2.p4).Pt()/(m1.p4+m2.p4).M(), 'p_{T} / M'),
    # ('pairPT',        'pair p_{T}',       (1000,       0.,   1000.), lambda (m1,m2): (m1.p4+m2.p4).Pt()                  , 'pair p_{T}'),
    ('chargeprod',    'q(#mu_{1})#times q(#mu_{2})',(  4, -2.,  2.), lambda (m1,m2): m1.charge*m2.charge                 , 'q(#mu_{1},#mu_{2})'),
    ('dimLxy',        'dim. L_{xy} [cm]',    (1000,    0.,    500.), lambda dimuon: dimuon.Lxy()                         , 'dim. L_{xy}'  ),
    ('dimMass',       'dim. mass',        (1000,       0.,    500.), lambda dimuon: (dimuon.mu1.p4+dimuon.mu2.p4).M()    , 'dim. mass'  ),
    ('dimVtxChi2',    'vertex #chi^{2}/dof', (1000,    0.,    200.), lambda dimuon: dimuon.normChi2                      , 'vertex #chi^{2}/dof'),
    ('dimCosAlpha',   'dim. cos(#alpha)', (1000,      -1.,      1.), lambda dimuon: dimuon.cosAlpha                      , 'dim. cos(#alpha)'),
    ('dimLxySig',     'dim. L_{xy}/#sigma_{L_{xy}}', (1000, 0., 300.), lambda dimuon: dimuon.LxySig()                    , 'dim. L_{xy}/#sigma_{L_{xy}}'),
    ('L1pTres',       '(p_{T}^{L1}-p_{T}^{DSA})/p_{T}^{DSA}', (1000, -1., 10.), lambda (dsamu,l1mu): (l1mu.pt-dsamu.pt)/dsamu.pt, '(p_{T}^{L1}-p_{T}^{DSA})/p_{T}^{DSA}'),
    ('L2pTres',       '(p_{T}^{L2}-p_{T}^{DSA})/p_{T}^{DSA}', (1000, -1.,  5.), lambda (dsamu,l2mu): (l2mu.pt-dsamu.pt)/dsamu.pt, '(p_{T}^{L2}-p_{T}^{DSA})/p_{T}^{DSA}'),
)
CONFIG = {}
for VAL in VALUES:
    KEY, VALS = VAL[0], VAL[1:]
    CONFIG[KEY] = dict(zip(HEADERS, VALS))


# some consistency checks
if DO_REQUIRE_BOTH_LEGS_MATCHED and not DO_REQUIRE_ONE_LEG_MATCHED:
    raise Exception('If DO_REQUIRE_BOTH_LEGS_MATCHED should be True, also '
            'DO_REQUIRE_ONE_LEG_MATCHED has to be True')

if len(L1_pairthresholds) != 2:
    raise Exception('\'L1_pairthresholds\' must hold exactly two values')


###############################################################################

#### CLASS AND FUNCTION DEFINITIONS ####

# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):

    for d0min,d0max in D0INTERVALS:
        d0intervals_str = '__d0GT{}__d0LT{}'.format(str(d0min).replace('.','p'),
                str(d0max).replace('.','p')) if d0min is not None and \
                        d0max is not None else ''

        for __,__,alpha_category_name in ALPHA_CATEGORIES:
            alpha_categories_str = alpha_category_name

            self.HistInit('L1TObjectsPerHLTObject_noSelections'+d0intervals_str+alpha_categories_str, ';number of L1 objects per HLT muon;Yield', 40, 0, 10)
            self.HistInit('L1TObjectsPerHLTObject'+d0intervals_str+alpha_categories_str, ';number of L1 objects per HLT muon;Yield', 40, 0, 10)
            self.HistInit('skippedEvents'+d0intervals_str+alpha_categories_str, ';skipped events;Yield', 7, -2, 5)
            self.HistInit('selectedMuons'+d0intervals_str+alpha_categories_str, ';selected muons;Yield', 2, 0, 2)
            self.HistInit('selectedMuonPairs'+d0intervals_str+alpha_categories_str, ';selected dimuons;Yield', 2, 0, 2)
            self.HistInit('lowerLegMu_HLTmatches'+d0intervals_str+alpha_categories_str, ';HLT matches for lower leg muon;Yield', 2, 0, 2)
            self.HistInit('upperLegMu_HLTmatches'+d0intervals_str+alpha_categories_str, ';HLT matches for upper leg muon;Yield', 2, 0, 2)
            self.HistInit('lowerLegMu_HLTmatches_upperLegMu_HLTmatches'+d0intervals_str+alpha_categories_str, ';HLT matches for both lower and upper leg muons;Yield', 2, 0, 2)
            self.HistInit('identifiedDimuons'+d0intervals_str+alpha_categories_str, ';identified dimuons;Yield', 2, 0, 2)
            self.HistInit('dimuonMultiplicity'+d0intervals_str+alpha_categories_str, ';dim. multiplicity;Yield', 10, 0, 10)

            for MUONTYPE in ('DSA',):
                for KEY in CONFIG:

                    BASETITLE = ';'+CONFIG[KEY]['XTITLE']+';'+MUONTYPE+' '

                    # define histograms for turn-on curves and resolution plots
                    if DO_CREATE_TURNON_HISTS:
                        self.HistInit(MUONTYPE+'__'+KEY+'VAR'+'EffDen'+d0intervals_str+alpha_categories_str,
                                BASETITLE+'Yield', *CONFIG[KEY]['AXES'])

                        for L1threshold in L1THRESHOLDS:
                            for threshold in PTTHRESHOLDS:
                                self.HistInit(MUONTYPE+'_pTGT{}'.format(
                                    str(threshold).replace('.','p'))+'_L1pTGT{}'.format(
                                        str(L1threshold).replace('.','p'))+'__'+KEY+'VAR'+'EffNum'+d0intervals_str+alpha_categories_str,
                                    BASETITLE+'Efficiency', *CONFIG[KEY]['AXES'])

                        if KEY in L1RESOLUTIONVARIABLES or KEY in L2RESOLUTIONVARIABLES:
                            self.HistInit(MUONTYPE+'_lowerHemisphere'+'__'+KEY+'VAR'+d0intervals_str+alpha_categories_str, BASETITLE+'Yield',
                                    *CONFIG[KEY]['AXES'])

                    # define histograms for simple distributions
                    if DO_CREATE_SIMPLE_HISTS:
                        if KEY in PAIRVARIABLES:
                            self.HistInit(MUONTYPE+'__'+KEY+'VAR'+d0intervals_str+alpha_categories_str,
                                    BASETITLE+'Yield', *CONFIG[KEY]['AXES'])

                            self.HistInit(MUONTYPE+'_oppositeCharges'+'__'+KEY+'VAR'+d0intervals_str+alpha_categories_str, BASETITLE+'Yield',
                                        *CONFIG[KEY]['AXES'])
                            self.HistInit(MUONTYPE+'_equalCharges'+'__'+KEY+'VAR'+d0intervals_str+alpha_categories_str, BASETITLE+'Yield',
                                        *CONFIG[KEY]['AXES'])

                        elif KEY in SINGLEMUVARIABLES:
                            for HEMISPHERE in ('_upperHemisphere', '_lowerHemisphere', ''):
                                self.HistInit(MUONTYPE+HEMISPHERE+'__'+KEY+'VAR'+d0intervals_str+alpha_categories_str, BASETITLE+'Yield',
                                        *CONFIG[KEY]['AXES'])
                                self.HistInit(MUONTYPE+HEMISPHERE+'_posCharge'+'__'+KEY+'VAR'+d0intervals_str+alpha_categories_str, BASETITLE+'Yield',
                                        *CONFIG[KEY]['AXES'])
                                self.HistInit(MUONTYPE+HEMISPHERE+'_negCharge'+'__'+KEY+'VAR'+d0intervals_str+alpha_categories_str, BASETITLE+'Yield',
                                        *CONFIG[KEY]['AXES'])

                        # elif KEY in L1RESOLUTIONVARIABLES or KEY in L2RESOLUTIONVARIABLES:
                        #     self.HistInit(MUONTYPE+'_lowerHemisphere'+'__'+KEY+'VAR'+d0intervals_str+alpha_categories_str, BASETITLE+'Yield',
                        #             *CONFIG[KEY]['AXES'])

                        elif KEY in DIMUONVARIABLES:
                            self.HistInit(MUONTYPE+'__'+KEY+'VAR'+d0intervals_str+alpha_categories_str,
                                    BASETITLE+'Yield', *CONFIG[KEY]['AXES'])

    # summary of booked histograms
    print('\n[ANALYZER INFO] Number of booked histograms: {}'.format(len(self.HISTS)))
    if len(self.HISTS) > 85000:  # some very rough heuristics
        print('\n  ***** CRITICAL NUMBER OF BOOKED HISTOGRAMS: script will run '
                'for a very long time *****\n')


# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    if not 'NoBPTX' in self.NAME:
        raise NotImplementedError('[ANALYZER ERROR]: Non-NoBPTX datasets are not supported')

    HLTpaths, HLTmuons, L1Tmuons = E.getPrimitives('TRIGGER')
    DSAmuons = E.getPrimitives('DSAMUON')
    DIMUONS = E.getPrimitives('DIMUON')

    event = E.getPrimitives('EVENT')

    # if len(HLTmuons) != len(L1Tmuons):
    #     do_print = False
    #     for HLTmuon in HLTmuons:
    #         n_L1muonsPerHLTmuon = 0
    #         for L1Tmuon in L1Tmuons:
    #             if L1Tmuon.idx == HLTmuon.idx: n_L1muonsPerHLTmuon += 1
    #         if n_L1muonsPerHLTmuon >= 8: do_print = True

    #     if do_print:
    #         print(event)
    #         for HLTpath in HLTpaths:
    #             print('----------------------------------------\n')
    #             print(HLTpath)
    #             for HLTmuon in HLTmuons:
    #                 if HLTmuon.idx == HLTpath.idx:
    #                     print('########## HLT muon:')
    #                     print(HLTmuon)
    #                     print('########## L1 muons:')
    #                     for L1Tmuon in L1Tmuons:
    #                         if L1Tmuon.idx == HLTmuon.idx:
    #                             print(L1Tmuon)

    #                     temp_matches = matchedMuons(HLTmuon, DSAmuons, threshold=MATCHING_THRESHOLD_HLT)
    #                     if len(temp_matches) > 0:
    #                         print('########## Matched DSA muon (dR=0.2):')
    #                         print(temp_matches[0]['muon'])
    #                     else:
    #                         print('########## [No DSA muon match for this HLT muon!]')

    #         print('\n')

    #         print('################################################################################\n\n')

    for d0min,d0max in D0INTERVALS:

        d0intervals_str = '__d0GT{}__d0LT{}'.format(str(d0min).replace('.','p'),
                str(d0max).replace('.','p')) if \
                d0min is not None and d0max is not None else ''

        for alpha_min,alpha_max,alpha_category_name in ALPHA_CATEGORIES:
            alpha_categories_str = alpha_category_name

            do_skip_event = False

            # Accept only events that pass the following HLT triggers
            accepted_HLTpaths = ['HLT_L2Mu10_NoVertex_NoBPTX3BX']
            HLTpaths_list = [str(path) for path in HLTpaths]
            if not any([any([(accepted_path in HLTpath) for accepted_path in accepted_HLTpaths]) for HLTpath in HLTpaths_list]):
                do_skip_event = True

            if do_skip_event:
                self.HISTS['skippedEvents'+d0intervals_str+alpha_categories_str].Fill(0)
                return

            for HLTmuon in HLTmuons:
                nL1Tmuons = len([m for m in L1Tmuons if m.idx == HLTmuon.idx])
                self.HISTS['L1TObjectsPerHLTObject_noSelections'+d0intervals_str+alpha_categories_str].Fill(nL1Tmuons)


            for MUONTYPE, MUONS in (('DSA', DSAmuons),):

                # discard events with too few reco muons
                if len(MUONS) < 2:
                    self.HISTS['skippedEvents'+d0intervals_str+alpha_categories_str].Fill(1)
                    continue

                accepted_muons = []
                accepted_matchedMuons = []
                accepted_matchedHLTMuons = []

                for muon in MUONS:

                    # apply single muon cuts
                    do_skip_muon = False
                    for var in SINGLEMU_SELECTION.keys():
                        if not SINGLEMU_SELECTION[var].apply(muon):
                            do_skip_muon = True

                    # apply additional d0 cuts
                    if d0min is not None and d0max is not None:
                        if not (d0min <= abs(muon.d0()) < d0max):
                            do_skip_muon = True

                    if do_skip_muon:
                        self.HISTS['selectedMuons'+d0intervals_str+alpha_categories_str].Fill(0)
                        continue

                    # store muon
                    accepted_muons.append(muon)

                    # store muon if matched
                    muonMatches = matchedMuons(muon, HLTmuons, threshold=MATCHING_THRESHOLD_HLT)
                    if len(muonMatches) > 0:
                        accepted_matchedMuons.append(muon)
                        accepted_matchedHLTMuons.append(muonMatches[0]['muon'])

                # skip event if there are no HLT-matched muons at all
                if len(accepted_matchedMuons) < 1: 
                    self.HISTS['skippedEvents'+d0intervals_str+alpha_categories_str].Fill(2)
                    continue


                # further cleanup of the selected muons: find the most cosmic-like pair
                # by requiring different hemispheres and a large angle between the muons
                if DO_SELECT_LARGEST_ALPHA_PAIR:
                    temp_maxalpha = -1
                    selected_muonpairs = ()
                else:
                    selected_muonpairs = []

                for m1,m2 in list(itertools.combinations(accepted_muons, 2)):
                    # require at least one muon to be matched to an HLT object
                    if DO_REQUIRE_ONE_LEG_MATCHED and \
                            all([m not in accepted_matchedMuons for m in (m1,m2)]):
                        continue

                    # require the muons to be in different detector hemispheres
                    if DO_REQUIRE_OPPOSITE_HEMISPHERES and \
                            ([hemisphere(m1), hemisphere(m2)]).count('upper') != 1:
                        continue

                    # find muon with the largest alpha(mu,mu)
                    if DO_SELECT_LARGEST_ALPHA_PAIR:
                        temp_alpha = CONFIG['alpha']['LAMBDA']((m1,m2))
                        if temp_alpha > temp_maxalpha:
                            temp_maxalpha = temp_alpha
                            if alpha_min is not None and alpha_max is not None:
                                # apply simple alpha cuts here, if applicable
                                # treatment of some special cases for certain
                                # alpha bins will be done further below
                                if alpha_min < temp_alpha < alpha_max:
                                    selected_muonpairs = (m1,m2)

                            else:
                                selected_muonspairs = (m1,m2)

                    else:
                        if alpha_min is not None and alpha_max is not None:
                            # apply simple alpha cuts here, if applicable
                            # treatment of some special cases for certain
                            # alpha bins will be done further below
                            if alpha_min < CONFIG['alpha']['LAMBDA']((m1,m2)) < alpha_max:
                                selected_muonpairs.append((m1,m2))

                        else:
                            selected_muonpairs.append((m1,m2))


                # skip events without any selected muon pairs
                if len(selected_muonpairs) == 0:
                    self.HISTS['skippedEvents'+d0intervals_str+alpha_categories_str].Fill(3)
                    continue

                # apply muon pair cuts
                do_skip_muonpair = False
                for var in MUONPAIR_SELECTION.keys():
                    if not MUONPAIR_SELECTION[var].apply(
                            (selected_muonpairs[0], selected_muonpairs[1])):
                        do_skip_muonpair = True

                # require both DSA to be matched to HLT objects
                if DO_REQUIRE_BOTH_LEGS_MATCHED:
                    muonMatches_m1 = matchedMuons(m1, HLTmuons, threshold=MATCHING_THRESHOLD_HLT)
                    muonMatches_m2 = matchedMuons(m2, HLTmuons, threshold=MATCHING_THRESHOLD_HLT)
                    if not (len(muonMatches_m1) > 0 and len(muonMatches_m2) > 0):
                        do_skip_muonpair = True

                if do_skip_muonpair:
                    self.HISTS['selectedMuonPairs'+d0intervals_str+alpha_categories_str].Fill(0)
                    continue
                else:
                    self.HISTS['selectedMuonPairs'+d0intervals_str+alpha_categories_str].Fill(1)

                for HLTmuon in HLTmuons:
                    nL1Tmuons = len([m for m in L1Tmuons if m.idx == HLTmuon.idx])
                    self.HISTS['L1TObjectsPerHLTObject'+d0intervals_str+alpha_categories_str].Fill(nL1Tmuons)
                    # self.HISTS['L1TObjectsPerHLTObject'+d0intervals_str+alpha_categories_str].Fill(1.*len(L1Tmuons)/len(HLTmuons))

                dimuon_multiplicity = 0

                if DO_SELECT_LARGEST_ALPHA_PAIR: selected_muonpairs = [selected_muonpairs]

                for m1,m2 in selected_muonpairs:

                    # apply pT cuts on L1 muons pairs ("L1 seed emulation")
                    m1_passes_first_cut = any([mu.pt > L1_pairthresholds[0] for mu in L1Tmuons if mu.idx == m1.idx])
                    m1_passes_second_cut = any([mu.pt > L1_pairthresholds[1] for mu in L1Tmuons if mu.idx == m1.idx])
                    m2_passes_first_cut = any([mu.pt > L1_pairthresholds[0] for mu in L1Tmuons if mu.idx == m2.idx])
                    m2_passes_second_cut = any([mu.pt > L1_pairthresholds[1] for mu in L1Tmuons if mu.idx == m2.idx])
                    if not ((m1_passes_first_cut and m2_passes_second_cut) or \
                            (m1_passes_second_cut and m2_passes_first_cut)):
                        continue


                    # check whether the selected two muons belong to a dimuon
                    # (i.e., have a dimuon vertex etc.)
                    for dimuon in DIMUONS:
                        if dimuon.idx1 == m1.idx and dimuon.idx2 == m2.idx or \
                                dimuon.idx1 == m2.idx and dimuon.idx2 == m1.idx:
                            is_dimuon = True
                            selected_dimuon = dimuon
                            break
                    else:
                        is_dimuon = False
                        selected_dimuon = None

                    if DO_REQUIRE_DIMUON_VERTEX and not is_dimuon:
                        continue

                    # apply dimuon cuts
                    do_skip_dimuon = False
                    if DO_REQUIRE_DIMUON_VERTEX:
                        for var in DIMUON_SELECTION.keys():
                            if not DIMUON_SELECTION[var].apply(selected_dimuon):
                                do_skip_dimuon = True

                    if do_skip_dimuon: continue

                    # special treatment of some alpha categories
                    do_skip_muonpair_duplicate = False
                    if alpha_min is not None and alpha_max is not None:
                        if 'noOppositeMuonMatch' in alpha_category_name and \
                                not DO_SELECT_LARGEST_ALPHA_PAIR:
                            # remove those dimuons which have a back-to-back muon
                            # in the same event for at least one of their muons
                            othermuons = [(om1,om2) for om1,om2 in selected_muonpairs if (om1,om2) != (m1,m2)]
                            for thismuon in (m1,m2):
                                alphas_with_othermuons = [CONFIG['alpha']['LAMBDA'](
                                    (thismuon,othermuon)) for othermuon,__ in othermuons]
                                alphas_with_othermuons += [CONFIG['alpha']['LAMBDA'](
                                    (thismuon,othermuon)) for __,othermuon in othermuons]

                            if not any([a > 2.8 for a in alphas_with_othermuons]):
                                do_skip_muonpair_duplicate = True

                    if do_skip_muonpair_duplicate: continue


                    if is_dimuon:
                        dimuon_multiplicity += 1
                        self.HISTS['identifiedDimuons'+d0intervals_str+alpha_categories_str].Fill(1)
                    else:
                        self.HISTS['identifiedDimuons'+d0intervals_str+alpha_categories_str].Fill(0)

                    # # print event info for edmPickEvents.py
                    # print('{}:{}:{}'.format(event.run, event.lumi, event.event))


                    ###############################################################
                    ##################### fill the histograms #####################
                    ###############################################################

                    # fill simple yield histograms
                    if DO_CREATE_SIMPLE_HISTS:
                        for KEY in CONFIG:
                            F = CONFIG[KEY]['LAMBDA']

                            if KEY in PAIRVARIABLES:
                                self.HISTS[MUONTYPE+'__'+KEY+'VAR'+d0intervals_str+alpha_categories_str].Fill(F((m1,m2)))

                                if m1.charge * m2.charge < 0:
                                    self.HISTS[MUONTYPE+'_oppositeCharges'+'__'+KEY+'VAR'+d0intervals_str+alpha_categories_str].Fill(
                                            F((m1, m2)))
                                else:
                                    self.HISTS[MUONTYPE+'_equalCharges'+'__'+KEY+'VAR'+d0intervals_str+alpha_categories_str].Fill(
                                            F((m1,m2)))

                            elif KEY in SINGLEMUVARIABLES:
                                for muon in (m1,m2):
                                    self.HISTS[MUONTYPE+'__'+KEY+'VAR'+d0intervals_str+alpha_categories_str].Fill(F(muon))
                                    if muon.charge > 0:
                                        self.HISTS[MUONTYPE+'_posCharge'+'__'+KEY+'VAR'+d0intervals_str+alpha_categories_str].Fill(F(muon))
                                    else:
                                        self.HISTS[MUONTYPE+'_negCharge'+'__'+KEY+'VAR'+d0intervals_str+alpha_categories_str].Fill(F(muon))

                                    if hemisphere(muon) == 'upper':
                                        self.HISTS[MUONTYPE+'_upperHemisphere'+'__'+KEY+'VAR'+d0intervals_str+alpha_categories_str].Fill(F(muon))
                                        if muon.charge > 0:
                                            self.HISTS[MUONTYPE+'_upperHemisphere'+'_posCharge'+'__'+KEY+'VAR'+d0intervals_str+alpha_categories_str].Fill(F(muon))
                                        else:
                                            self.HISTS[MUONTYPE+'_upperHemisphere'+'_negCharge'+'__'+KEY+'VAR'+d0intervals_str+alpha_categories_str].Fill(F(muon))
                                    else:
                                        self.HISTS[MUONTYPE+'_lowerHemisphere'+'__'+KEY+'VAR'+d0intervals_str+alpha_categories_str].Fill(F(muon))
                                        if muon.charge > 0:
                                            self.HISTS[MUONTYPE+'_lowerHemisphere'+'_posCharge'+'__'+KEY+'VAR'+d0intervals_str+alpha_categories_str].Fill(F(muon))
                                        else:
                                            self.HISTS[MUONTYPE+'_lowerHemisphere'+'_negCharge'+'__'+KEY+'VAR'+d0intervals_str+alpha_categories_str].Fill(F(muon))

                            elif KEY in DIMUONVARIABLES:
                                for dimuon in DIMUONS:
                                    if (dimuon.idx1 == m1.idx and dimuon.idx2 == m2.idx) or \
                                            (dimuon.idx1 == m2.idx and dimuon.idx2 == m1.idx):
                                        self.HISTS[MUONTYPE+'__'+KEY+'VAR'+d0intervals_str+alpha_categories_str].Fill(F(dimuon))

                            elif KEY in L1RESOLUTIONVARIABLES or KEY in L2RESOLUTIONVARIABLES:
                                pass  # resolution variables are processed further down

                            else:
                                print('[ANALYZER WARNING] Key {} not processed'.format(KEY))


                    # fill turn-on histograms and resolution plots
                    if DO_CREATE_TURNON_HISTS:
                        lowerHSmuon = m1 if hemisphere(m1) == 'lower' else m2
                        upperHSmuon = m1 if hemisphere(m1) == 'upper' else m2

                        # match lower-HS muon
                        muonMatches = matchedMuons(lowerHSmuon, HLTmuons, threshold=MATCHING_THRESHOLD_HLT)
                        if len(muonMatches) > 0:
                            is_matched_lowerHSmuon_HLT = True
                            self.HISTS['lowerLegMu_HLTmatches'+d0intervals_str+alpha_categories_str].Fill(1)

                            lowerHSmuon_HLTmatch = muonMatches[0]['muon']

                            for KEY in L2RESOLUTIONVARIABLES:
                                self.HISTS[MUONTYPE+'_lowerHemisphere'+'__'+KEY+'VAR'+d0intervals_str+alpha_categories_str].Fill(
                                        CONFIG[KEY]['LAMBDA']((lowerHSmuon, lowerHSmuon_HLTmatch)))

                            # find the associated L1 muon
                            # there can be more than one L1 object for a given HLT object
                            lowerHSmuon_L1muons = [L1Tmuon for L1Tmuon in L1Tmuons if L1Tmuon.idx == lowerHSmuon_HLTmatch.idx]
                            if len(lowerHSmuon_L1muons) > 0:
                                for L1Tmuon in lowerHSmuon_L1muons:
                                    for KEY in L1RESOLUTIONVARIABLES:
                                        self.HISTS[MUONTYPE+'_lowerHemisphere'+'__'+KEY+'VAR'+d0intervals_str+alpha_categories_str].Fill(
                                                CONFIG[KEY]['LAMBDA']((lowerHSmuon, L1Tmuon)))

                            else:
                                pass

                            for KEY in CONFIG:
                                if KEY in SINGLEMUVARIABLES:
                                    F = CONFIG[KEY]['LAMBDA']
                                    for lowerHSmuon_L1muon in lowerHSmuon_L1muons:
                                        self.HISTS[MUONTYPE+'__'+KEY+'VAR'+'EffDen'+d0intervals_str+alpha_categories_str].Fill(F(lowerHSmuon))
                                        for HLTthreshold in PTTHRESHOLDS:
                                            for L1threshold in L1THRESHOLDS:
                                                if lowerHSmuon_HLTmatch.pt > HLTthreshold:
                                                    passed_HLT = True
                                                else:
                                                    passed_HLT = False

                                                if lowerHSmuon_L1muon.pt > L1threshold:
                                                    passed_L1 = True
                                                else:
                                                    passed_L1 = False

                                                if passed_HLT and passed_L1:
                                                    self.HISTS[MUONTYPE+'_pTGT{}'.format(str(HLTthreshold).replace('.','p'))+'_L1pTGT{}'.format(str(L1threshold).replace('.','p'))+'__'+KEY+'VAR'+'EffNum'+d0intervals_str+alpha_categories_str].Fill(F(lowerHSmuon))

                        else:
                            # print('No HLT match found. Printing event information...')
                            # print((event))
                            is_matched_lowerHSmuon_HLT = False
                            self.HISTS['lowerLegMu_HLTmatches'+d0intervals_str+alpha_categories_str].Fill(0)

                        # match upper-HS muon
                        muonMatches = matchedMuons(upperHSmuon, HLTmuons, threshold=MATCHING_THRESHOLD_HLT)
                        if len(muonMatches) > 0:
                            is_matched_upperHSmuon_HLT = True
                            upperHSmuon_HLTmatch = muonMatches[0]['muon']

                            self.HISTS['upperLegMu_HLTmatches'+d0intervals_str+alpha_categories_str].Fill(1)

                        else:
                            is_matched_upperHSmuon_HLT = False
                            self.HISTS['upperLegMu_HLTmatches'+d0intervals_str+alpha_categories_str].Fill(0)

                        if is_matched_lowerHSmuon_HLT and is_matched_upperHSmuon_HLT:
                            self.HISTS['lowerLegMu_HLTmatches_upperLegMu_HLTmatches'+d0intervals_str+alpha_categories_str].Fill(1)

                        else:
                            self.HISTS['lowerLegMu_HLTmatches_upperLegMu_HLTmatches'+d0intervals_str+alpha_categories_str].Fill(0)

                        # count accepted events
                        self.HISTS['skippedEvents'+d0intervals_str+alpha_categories_str].Fill(-1)


                self.HISTS['dimuonMultiplicity'+d0intervals_str+alpha_categories_str].Fill(dimuon_multiplicity)


def hemisphere(muon):
    if 0 <= muon.phi <= math.pi:
        return 'upper'
    else:
        return 'lower'


def parse_filename(path='roots/', prefix='', suffix='', fext='.root'):
    OpStr_as_FStr = {
        '>': 'GT',
        '<': 'LT',
        u'\u2265': 'GE',
        u'\u2264': 'LE',
    }

    cut_variables = {}
    for CUT_SET in (SINGLEMU_SELECTION, MUONPAIR_SELECTION, DIMUON_SELECTION):
        for var in CUT_SET.keys():
            cut_str = CUT_SET[var].__str__().split(' ')
            cut_variables[var] = {
                'operator': OpStr_as_FStr[cut_str[1]],
                'value': cut_str[2]
            }

    # sort keys alphabetically
    orderedKeys = sorted(cut_variables.keys(), key=lambda k: k.lower())

    if path[-1] != '/': path += '/'
    filename = path + prefix
    for cut in orderedKeys:
        filename += '_' + cut
        filename += cut_variables[cut]['operator']
        filename += cut_variables[cut]['value'].replace('.','p')

    if any([val > 0. for val in L1_pairthresholds]):
        filename += '_pairL1pT{}AND{}'.format(
                str(L1_pairthresholds[0]).replace('.','p'),
                str(L1_pairthresholds[1]).replace('.','p'))

    if DO_SELECT_LARGEST_ALPHA_PAIR: filename += '_largestAlphaPair'
    if DO_REQUIRE_OPPOSITE_HEMISPHERES: filename += '_oppositeHS'
    if DO_REQUIRE_ONE_LEG_MATCHED and not DO_REQUIRE_BOTH_LEGS_MATCHED:
        filename += '_oneLegMatched'
    if DO_REQUIRE_BOTH_LEGS_MATCHED: filename += '_bothLegsMatched'
    if DO_REQUIRE_DIMUON_VERTEX: filename += '_requireDimVTx'

    if not DO_CREATE_SIMPLE_HISTS: filename += '_noSimpleHists'
    if not DO_CREATE_TURNON_HISTS: filename += '_noTurnOnHists'

    filename += suffix
    filename += '_{}'  # will be replaced by the signal point string later on
    filename += fext
    return filename


#### RUN ANALYSIS ####
if __name__ == '__main__':

    ARGS = Analyzer.PARSER.parse_args()
    Analyzer.setSample(ARGS)

    for METHOD in ('declareHistograms', 'analyze'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])
    
    analyzer = Analyzer.Analyzer(
            ARGS = ARGS,
            BRANCHKEYS = ('DSAMUON', 'DIMUON', 'TRIGGER', 'EVENT'),
    )

    outputname = parse_filename(
            path='roots/',
            prefix='test_backgrEstimation_extraMuon_cosmicsPlots')

    analyzer.writeHistograms(outputname)
