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
DO_CREATE_TURNON_HISTS = True

# this will be used as a fallback if the option --HLTfilter is NOT explicitly given
accepted_HLTpaths_fallback = ['HLT_L2Mu10_NoVertex_pp']

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
    # 'pT': Selections.Cut('pT',
    #     lambda muon: muon.pt,
    #     operator.gt, 20.),
    # 'eta': Selections.Cut('eta',
    #     lambda muon: abs(muon.eta),
    #     operator.lt, 1.2),
}

# define muon pair cuts
MUONPAIR_SELECTION = {
    'alpha': Selections.Cut(
        'alpha', lambda (m1,m2): m1.p4.Angle(m2.p4.Vect()),
        operator.gt, 2.9),
}

# define dimuon cuts
DIMUON_SELECTION = {
    # 'vtxChiSqu': Selections.Cut('vtxChiSqu',
    #     lambda dim: dim.normChi2,
    #     operator.lt, 50.),
}

# pT cuts applied to muon pairs ("L1 seed emulation"):
# (the first muon has to pass the first cut and the second muon has to pass the
# second cut) OR (the first muon has to pass the second cut and the second muon
# has to pass the first cut)
L1_pairthresholds = (0.,0.)

DO_SELECT_LARGEST_ALPHA_PAIR = True
DO_REQUIRE_OPPOSITE_HEMISPHERES = False
DO_REQUIRE_ONE_LEG_MATCHED = True
DO_REQUIRE_BOTH_LEGS_MATCHED = False
DO_REQUIRE_DIMUON_VERTEX = False

# deltaR matching threshold for reco-HLT matches
MATCHING_THRESHOLD_HLT = 0.2

# pT threshold values for matched HLT objects, applied to the turn-on curves
PTTHRESHOLDS = [23., 25., 28.]  

# additional L1 pT cuts applied consecutively to the sets of turn-on curves
L1THRESHOLDS = (0.0, 4.0, 5.0, 7.0, 11.0, 12.0, 15.0)

# different dimuon populations, defined by their alpha(mu,mu) values
# define tuples of (min,max,name), corresponding to min<alpha<max and the name
# tag for the corresponding histograms.
# "(None,None,'')" is the alpha-inclusive case.
ALPHA_CATEGORIES = (
        (None, None, ''),
        # (2.8, math.pi, '__2p8alphaPi'),
        # (2.8, math.pi, '__SSpairs_2p8alphaPi'),
        # (2.8, math.pi, '__goodQuality_2p8alphaPi'),
        # (0.3, 2.8, '__0p3alpha2p8'),
        # (0., 0.3, '__0p0alpha0p3'),
        # (0., 2.8, '__noOppositeMuonMatch_0p0alpha2p8'),
)

# list of d0 intervals to process, "(None, None)" gives the d0-inclusive results
D0INTERVALS = [(None,None)]
# 2.5-cm steps for small d0
# D0INTERVALS += ([(i,i+2.5) for i in np.arange(0., 30., 2.5)])
# 5-cm steps for small d0
# D0INTERVALS += ([(i,i+5.0) for i in np.arange(0., 30., 5.)])
# 10-cm steps for the entire d0 range
# D0INTERVALS += ([(i,i+10.) for i in np.arange(0., 500., 10.)])
# custom d0 bins
D0INTERVALS += ([(0,5),(5,10),(10,15),(15,20),(20,25),(25,30)])
D0INTERVALS += ([(0,10),(10,50),(0,50),(50,100),(100,150),(150,250),(250,350),(250,1000),(350,1000)])

# make sure that all of the values are actually floats
D0INTERVALS = [(float(l), float(h)) if l is not None and h is not None else (l,h) for l,h in D0INTERVALS]

SINGLEMUVARIABLES = ['pT','eta','phi','charge','d0','x_fhit','y_fhit','z_fhit','nStations','nCSCDTHits','pTSig','chi2']
PAIRVARIABLES = ['pTdiff','deltaR','mass','cosAlpha','alpha','dimuonPTOverM', 'pairPT', 'chargeprod', 'dNStations', 'dNCSCDTHits', 'dEta', 'dPhi', 'dD0', 'dChi2']
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
    ('cosAlpha',      'cos#alpha',        (1000,      -1.,      1.), lambda (m1,m2): m1.p4.Vect().Dot(m2.p4.Vect())/m1.p4.P()/m2.p4.P(),'cos(#alpha)'),
    ('alpha',         '#alpha',           (1000,       0., math.pi), lambda (m1,m2): m1.p4.Angle(m2.p4.Vect())           , 'cos(#alpha)'),
    # ('dimuonPTOverM', 'dimuon p_{T} / M', (1000,       0.,     20.), lambda (m1,m2): (m1.p4+m2.p4).Pt()/(m1.p4+m2.p4).M(), 'p_{T} / M'),
    # ('pairPT',        'pair p_{T}',       (1000,       0.,   1000.), lambda (m1,m2): (m1.p4+m2.p4).Pt()                  , 'pair p_{T}'),
    ('chargeprod',    'q(#mu_{1})#times q(#mu_{2})',(  4, -2.,  2.), lambda (m1,m2): m1.charge*m2.charge                 , 'q(#mu_{1},#mu_{2})'),
    ('dNStations',    '|nStations(#mu_{1}) - nStations(#mu_{2})|', (10, 0., 10.), lambda (m1,m2): abs(m1.nDTStations+m1.nCSCStations-m2.nDTStations-m2.nCSCStations), '|nStations(#mu_{1}) - nStations(#mu_{2})|'),
    ('dNCSCDTHits',   '|nCSC+DTHits(#mu_{1}) - nCSC+DTHits(#mu_{2})|', (50, 0., 50.), lambda (m1,m2): abs(m1.nCSCHits+m1.nDTHits-m2.nCSCHits-m2.nDTHits), '|nCSC+DTHits(#mu_{1}) - nCSC+DTHits(#mu_{2})|'),
    ('dEta',          '|#eta(#mu_{1}) - #eta(#mu_{2})|', (1000, 0., 3.), lambda (m1,m2): abs(m1.eta-m2.eta)              , '|#eta(#mu_{1}) - #eta(#mu_{2})|'),
    ('dPhi',          '|#phi(#mu_{1}) - #phi(#mu_{2})|', (1000, 0., 2*math.pi), lambda (m1,m2): abs(m1.phi-m2.phi)              , '|#phi(#mu_{1}) - #phi(#mu_{2})|'),
    ('dChi2',         '|#chi^{2}/ndof(#mu_{1}) - #chi^{2}/ndof(#mu_{2})|', (1000, -1., 30.), lambda (m1,m2): abs(m1.chi2/m1.ndof-m2.chi2/m2.ndof) if m1.ndof != 0 and m2.ndof != 0 else -1. , '|#chi^{2}(#mu_{1}) - #chi^{2}(#mu_{2})|'),
    ('dimLxy',        'dim. L_{xy} [cm]',    (1000,    0.,    500.), lambda dimuon: dimuon.Lxy()                         , 'dim. L_{xy}'  ),
    ('dimMass',       'dim. mass',        (1000,       0.,    500.), lambda dimuon: (dimuon.mu1.p4+dimuon.mu2.p4).M()    , 'dim. mass'  ),
    ('dimVtxChi2',    'vertex #chi^{2}/dof', (1000,    0.,    200.), lambda dimuon: dimuon.normChi2                      , 'vertex #chi^{2}/dof'),
    ('dimCosAlpha',   'dim. cos(#alpha)', (1000,      -1.,      1.), lambda dimuon: dimuon.cosAlpha                      , 'dim. cos(#alpha)'),
    ('dimLxySig',     'dim. L_{xy}/#sigma_{L_{xy}}', (1000, 0., 300.), lambda dimuon: dimuon.LxySig()                    , 'dim. L_{xy}/#sigma_{L_{xy}}'),
    ('L1pTres',       '(p_{T}^{L1}-p_{T}^{DSA})/p_{T}^{DSA}', (1000, -1., 20.), lambda (dsamu,l1mu): (l1mu.pt-dsamu.pt)/dsamu.pt, '(p_{T}^{L1}-p_{T}^{DSA})/p_{T}^{DSA}'),
    ('L2pTres',       '(p_{T}^{L2}-p_{T}^{DSA})/p_{T}^{DSA}', (1000, -1., 20.), lambda (dsamu,l2mu): (l2mu.pt-dsamu.pt)/dsamu.pt, '(p_{T}^{L2}-p_{T}^{DSA})/p_{T}^{DSA}'),
)
CONFIG = {}
for VAL in VALUES:
    KEY, VALS = VAL[0], VAL[1:]
    CONFIG[KEY] = dict(zip(HEADERS, VALS))


# some consistency checks
if DO_REQUIRE_BOTH_LEGS_MATCHED and not DO_REQUIRE_ONE_LEG_MATCHED:
    raise Exception('If DO_REQUIRE_BOTH_LEGS_MATCHED should be True, also '
            'DO_REQUIRE_ONE_LEG_MATCHED has to be True')

if any([threshold > 0. for threshold in L1_pairthresholds]) and not \
        DO_REQUIRE_BOTH_LEGS_MATCHED:
    raise Exception('If L1 pair thresholds are >0, both legs must be required '
            'to match a L2 muon')

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

            self.HistInit('cutFlow'+d0intervals_str+alpha_categories_str, ';applied cuts;number of events passing', 30,0,30)
            self.HistInit('L1TObjectsPerHLTObject_noSelections'+d0intervals_str+alpha_categories_str, ';number of L1 objects per HLT muon;Yield', 40, 0, 10)
            self.HistInit('L1TObjectsPerHLTObject'+d0intervals_str+alpha_categories_str, ';number of L1 objects per HLT muon;Yield', 40, 0, 10)
            self.HistInit('lowerLegMu_HLTmatches'+d0intervals_str+alpha_categories_str, ';HLT matches for lower leg muon;Yield', 2, 0, 2)
            self.HistInit('upperLegMu_HLTmatches'+d0intervals_str+alpha_categories_str, ';HLT matches for upper leg muon;Yield', 2, 0, 2)
            self.HistInit('lowerLegMu_HLTmatches_upperLegMu_HLTmatches'+d0intervals_str+alpha_categories_str, ';HLT matches for both lower and upper leg muons;Yield', 2, 0, 2)
            self.HistInit('DSAmuonMultiplicity_noSelections'+d0intervals_str+alpha_categories_str, ';DSA muon multiplicity; Yield', 29, 1, 30)
            self.HistInit('DSAmuonMultiplicity'+d0intervals_str+alpha_categories_str, ';DSA muon multiplicity; Yield', 29, 1, 30)
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

    HLTpaths, HLTmuons, L1Tmuons = E.getPrimitives('TRIGGER')
    DSAmuons = E.getPrimitives('DSAMUON')
    DIMUONS3 = E.getPrimitives('DIMUON')
    # restore "old" (pre-January-2019) dimuon behavior
    DIMUONS = [dim for dim in DIMUONS3 if dim.composition == 'DSA']

    event = E.getPrimitives('EVENT')

    # override HLT path filter if the option has been passed
    if ARGS.HLTFILTER is not None:
        accepted_HLTpaths = [ARGS.HLTFILTER]
    else:
        accepted_HLTpaths = accepted_HLTpaths_fallback

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

            # count DSA muons before any selections
            self.HISTS['DSAmuonMultiplicity_noSelections'+d0intervals_str+alpha_categories_str].Fill(len(DSAmuons))

            # count events without any selections
            self.HISTS['cutFlow'+d0intervals_str+alpha_categories_str].Fill(0)

            do_skip_event = False

            # Accept only events that pass the following HLT triggers
            HLTpaths_list = [str(path) for path in HLTpaths]
            if not any([any([(accepted_path in HLTpath) for accepted_path in accepted_HLTpaths]) for HLTpath in HLTpaths_list]):
                do_skip_event = True

            if do_skip_event:
                return
            else:
                # count events that pass the HLT paths filter
                self.HISTS['cutFlow'+d0intervals_str+alpha_categories_str].Fill(1)

            for HLTmuon in HLTmuons:
                nL1Tmuons = len([m for m in L1Tmuons if m.idx == HLTmuon.idx])
                self.HISTS['L1TObjectsPerHLTObject_noSelections'+d0intervals_str+alpha_categories_str].Fill(nL1Tmuons)


            for MUONTYPE, MUONS in (('DSA', DSAmuons),):

                # discard events with too few reco muons
                if len(MUONS) < 2:
                    continue
                else:
                    # count events with at least two reco muons
                    self.HISTS['cutFlow'+d0intervals_str+alpha_categories_str].Fill(2)

                accepted_muons = []
                accepted_matchedMuons = []
                accepted_matchedHLTMuons = []

                # check if there are any HLT-matched muons in the event (but do
                # nothing else at the moment - everything else will be taken
                # care of later on)
                nHLTmatchedMuons = 0
                for muon in MUONS:
                    muonMatches = matchedMuons(muon, HLTmuons, threshold=MATCHING_THRESHOLD_HLT)
                    if len(muonMatches) > 0:
                        self.HISTS['cutFlow'+d0intervals_str+alpha_categories_str].Fill(3)
                        break


                for muon in MUONS:

                    # count all muons in the events that have been selected so far
                    self.HISTS['cutFlow'+d0intervals_str+alpha_categories_str].Fill(4)

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
                        continue
                    else:
                        # count muons remaining after single muon cuts
                        self.HISTS['cutFlow'+d0intervals_str+alpha_categories_str].Fill(5)

                    # store muon
                    accepted_muons.append(muon)

                    # store muon if matched
                    muonMatches = matchedMuons(muon, HLTmuons, threshold=MATCHING_THRESHOLD_HLT)
                    if len(muonMatches) > 0:
                        accepted_matchedMuons.append(muon)
                        accepted_matchedHLTMuons.append(muonMatches[0]['muon'])

                # skip event if there are no HLT-matched muons at all
                if len(accepted_matchedMuons) < 1: 
                    continue
                else:
                    # count events with at least one HLT matched muon
                    self.HISTS['cutFlow'+d0intervals_str+alpha_categories_str].Fill(6)


                # further cleanup of the selected muons: find the most cosmic-like pair
                # by requiring different hemispheres and a large angle between the muons
                if DO_SELECT_LARGEST_ALPHA_PAIR:
                    temp_maxalpha = -1
                    selected_muonpairs = ()
                else:
                    selected_muonpairs = []

                for m1,m2 in list(itertools.combinations(accepted_muons, 2)):
                    # count muon pairs that have passed all previous selections
                    self.HISTS['cutFlow'+d0intervals_str+alpha_categories_str].Fill(7)

                    # require at least one muon to be matched to an HLT object
                    if DO_REQUIRE_ONE_LEG_MATCHED:
                        if all([m not in accepted_matchedMuons for m in (m1,m2)]):
                            continue
                        else:
                            # count all muon pairs with >=1 HLT-matched leg
                            self.HISTS['cutFlow'+d0intervals_str+alpha_categories_str].Fill(8)

                    # require the muons to be in different detector hemispheres
                    if DO_REQUIRE_OPPOSITE_HEMISPHERES:
                        if ([hemisphere(m1), hemisphere(m2)]).count('upper') != 1:
                            continue
                        else:
                            # count muon pairs with legs in different hemispheres
                            self.HISTS['cutFlow'+d0intervals_str+alpha_categories_str].Fill(9)

                    # find muon with the largest alpha(mu,mu)
                    if DO_SELECT_LARGEST_ALPHA_PAIR:
                        temp_alpha = CONFIG['alpha']['LAMBDA']((m1,m2))
                        if temp_alpha > temp_maxalpha:
                            if alpha_min is not None and alpha_max is not None:
                                # apply simple alpha cuts here, if applicable
                                # treatment of some special cases for certain
                                # alpha bins will be done further below
                                if alpha_min < temp_alpha < alpha_max:
                                    temp_maxalpha = temp_alpha
                                    selected_muonpairs = (m1,m2)

                            else:
                                temp_maxalpha = temp_alpha
                                selected_muonpairs = (m1,m2)

                    else:
                        if alpha_min is not None and alpha_max is not None:
                            # apply simple alpha cuts here, if applicable
                            # treatment of some special cases for certain
                            # alpha bins will be done further below
                            if alpha_min < CONFIG['alpha']['LAMBDA']((m1,m2)) < alpha_max:
                                selected_muonpairs.append((m1,m2))

                        else:
                            selected_muonpairs.append((m1,m2))

                # make everything compatible again
                if DO_SELECT_LARGEST_ALPHA_PAIR: 
                    if len(selected_muonpairs) > 0:
                        selected_muonpairs = [selected_muonpairs]
                    else:
                        selected_muonpairs = []

                # skip events without any selected muon pairs
                if len(selected_muonpairs) == 0:
                    continue
                else:
                    # count events with >=1 selected muon pair
                    self.HISTS['cutFlow'+d0intervals_str+alpha_categories_str].Fill(10)

                buffer_selected_muonpairs = []  # stores next subset of muon pairs
                buffer_HLTmatches_selected_muonpairs = []  # stores corresponding HLT matches

                for m1,m2 in selected_muonpairs:
                    # count all muon pairs selected so far
                    self.HISTS['cutFlow'+d0intervals_str+alpha_categories_str].Fill(11)

                    # apply muon pair cuts
                    do_skip_muonpair = False
                    for var in MUONPAIR_SELECTION.keys():
                        if not MUONPAIR_SELECTION[var].apply((m1,m2)):
                            do_skip_muonpair = True

                    if do_skip_muonpair:
                        continue
                    else:
                        # count muon pairs that pass the muon pairs selection
                        self.HISTS['cutFlow'+d0intervals_str+alpha_categories_str].Fill(12)

                    do_skip_muonpair = False
                    # require both DSA to be matched to HLT objects
                    if DO_REQUIRE_BOTH_LEGS_MATCHED:
                        muonMatches_m1 = matchedMuons(m1, HLTmuons, threshold=MATCHING_THRESHOLD_HLT)
                        muonMatches_m2 = matchedMuons(m2, HLTmuons, threshold=MATCHING_THRESHOLD_HLT)
                        if not (len(muonMatches_m1) > 0 and len(muonMatches_m2) > 0):
                            do_skip_muonpair = True

                        # require matches to different HLT objects
                        if len(muonMatches_m1) > 0 and len(muonMatches_m2) > 0 \
                                and muonMatches_m1[0]['muon'] == muonMatches_m2[0]['muon']:
                            do_skip_muonpair = True

                    if do_skip_muonpair:
                        continue
                    else:
                        # count muon pairs that have HLT matches for both legs
                        self.HISTS['cutFlow'+d0intervals_str+alpha_categories_str].Fill(13)

                    # if muon pair passed all the selections, store it for later
                    buffer_selected_muonpairs.append((m1,m2))
                    if DO_REQUIRE_BOTH_LEGS_MATCHED:
                        buffer_HLTmatches_selected_muonpairs.append((
                            muonMatches_m1[0]['muon'],
                            muonMatches_m2[0]['muon']))

                selected_muonpairs = buffer_selected_muonpairs
                HLTmatches_selected_muonpairs = buffer_HLTmatches_selected_muonpairs

                for HLTmuon in HLTmuons:
                    nL1Tmuons = len([m for m in L1Tmuons if m.idx == HLTmuon.idx])
                    self.HISTS['L1TObjectsPerHLTObject'+d0intervals_str+alpha_categories_str].Fill(nL1Tmuons)

                dimuon_multiplicity = 0
                selected_muons = []

                cnt_pos_muonpairs = -1
                for m1,m2 in selected_muonpairs:
                    cnt_pos_muonpairs += 1
                    # count all muon pairs selected so far
                    self.HISTS['cutFlow'+d0intervals_str+alpha_categories_str].Fill(14)

                    # apply pT cuts on L1 muons pairs ("L1 seed emulation")
                    if DO_REQUIRE_BOTH_LEGS_MATCHED:
                        m1_passes_first_cut  = any([mu.pt >= L1_pairthresholds[0] for mu in L1Tmuons if mu.idx == HLTmatches_selected_muonpairs[cnt_pos_muonpairs][0].idx])
                        m1_passes_second_cut = any([mu.pt >= L1_pairthresholds[1] for mu in L1Tmuons if mu.idx == HLTmatches_selected_muonpairs[cnt_pos_muonpairs][0].idx])
                        m2_passes_first_cut  = any([mu.pt >= L1_pairthresholds[0] for mu in L1Tmuons if mu.idx == HLTmatches_selected_muonpairs[cnt_pos_muonpairs][1].idx])
                        m2_passes_second_cut = any([mu.pt >= L1_pairthresholds[1] for mu in L1Tmuons if mu.idx == HLTmatches_selected_muonpairs[cnt_pos_muonpairs][1].idx])

                        if not (m1_passes_first_cut and m2_passes_second_cut) \
                                and not (m1_passes_second_cut and m2_passes_first_cut):
                            continue
                        else:
                            # count all muon pars that pass the L1 trigger cuts
                            self.HISTS['cutFlow'+d0intervals_str+alpha_categories_str].Fill(15)


                    # check whether the selected two muons belong to a dimuon
                    # (i.e., have a dimuon vertex etc.)
                    for dimuon in DIMUONS:
                        if dimuon.idx1 == m1.idx and dimuon.idx2 == m2.idx or \
                                dimuon.idx1 == m2.idx and dimuon.idx2 == m1.idx:
                            is_dimuon = True
                            selected_dimuon = dimuon

                            # count selected dimuons
                            self.HISTS['cutFlow'+d0intervals_str+alpha_categories_str].Fill(16)
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

                    if do_skip_dimuon:
                        continue
                    else:
                        # count dimuons passing the dimuon selection
                        self.HISTS['cutFlow'+d0intervals_str+alpha_categories_str].Fill(17)

                    # special treatment of some alpha categories
                    if 'noOppositeMuonMatch' in alpha_category_name and \
                            not DO_SELECT_LARGEST_ALPHA_PAIR:

                        do_skip_muonpair_duplicate = False
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

                        if do_skip_muonpair_duplicate:
                            continue
                        else:
                            # count selected non-duplicate muon pairs
                            self.HISTS['cutFlow'+d0intervals_str+alpha_categories_str].Fill(18)

                    if 'SSpairs' in alpha_category_name:
                        if m1.charge*m2.charge < 0:
                            continue
                        else:
                            # count selected same-sign pairs
                            self.HISTS['cutFlow'+d0intervals_str+alpha_categories_str].Fill(19)

                    if 'goodQuality' in alpha_category_name:
                        if DO_REQUIRE_DIMUON_VERTEX:
                            if selected_dimuon.normChi2 > 4.0:
                                continue
                            else:
                                # count dimuons with good-quality fit
                                self.HISTS['cutFlow'+d0intervals_str+alpha_categories_str].Fill(20)

                    if is_dimuon:
                        dimuon_multiplicity += 1

                    # collect all selected muons in order to calculate the
                    # multiplicity of selected reco muons
                    if m1 not in selected_muons: selected_muons.append(m1)
                    if m2 not in selected_muons: selected_muons.append(m2)

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
                        reference_leg = ARGS.REFLEG
                        other_leg = 'upper' if reference_leg == 'lower' else 'lower'
                        lowerHSmuon = m1 if hemisphere(m1) == reference_leg else m2
                        upperHSmuon = m1 if hemisphere(m1) == other_leg else m2

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

                self.HISTS['dimuonMultiplicity'+d0intervals_str+alpha_categories_str].Fill(dimuon_multiplicity)
                if len(selected_muons) > 0:
                    self.HISTS['DSAmuonMultiplicity'+d0intervals_str+alpha_categories_str].Fill(len(selected_muons))


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
    if DO_REQUIRE_DIMUON_VERTEX: filename += '_requireDimVtx'

    if not DO_CREATE_SIMPLE_HISTS: filename += '_noSimpleHists'
    if not DO_CREATE_TURNON_HISTS: filename += '_noTurnOnHists'

    filename += suffix
    filename += '_{}'  # will be replaced by the signal point string later on
    filename += fext
    return filename


#### RUN ANALYSIS ####
if __name__ == '__main__':

    Analyzer.PARSER.add_argument('--HLTfilter',
            help='Specify the name (or a substring) of the HLT path to filter by',
            dest='HLTFILTER',
            type=str,
            default=None)
    Analyzer.PARSER.add_argument('--output-prefix',
            help='Define an optional prefix for all output files',
            dest='OUTPUTPREFIX',
            type=str,
            default=None)
    Analyzer.PARSER.add_argument('--reference-leg',
            help='Define which muon leg to use as reference leg (default: \'lower\')',
            dest='REFLEG',
            type=str,
            default='lower')

    ARGS = Analyzer.PARSER.parse_args()
    Analyzer.setSample(ARGS)

    if ARGS.REFLEG not in ('lower','upper'):
        raise Exception('Invalid value of reference-leg (allowed: '
                '\'lower\', \'upper\'')

    for METHOD in ('declareHistograms', 'analyze'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])
    
    analyzer = Analyzer.Analyzer(
            ARGS = ARGS,
            BRANCHKEYS = ('DSAMUON', 'DIMUON', 'TRIGGER', 'EVENT'),
    )

    outputname = parse_filename(
            path='roots/',
            prefix=ARGS.OUTPUTPREFIX if ARGS.OUTPUTPREFIX is not None else 'test')

    analyzer.writeHistograms(outputname)
