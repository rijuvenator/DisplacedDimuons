import math
import itertools
import operator
import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Analysis.Primitives as Primitives
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedMuons

# DEBUG = False

# define single muon quality cuts
SINGLEMU_QUALITYCUTS = {
    'nStations': Selections.Cut('nStations',
        lambda muon: muon.nDTStations + muon.nCSCStations,
        operator.gt, 1),
    'nCSCDTHits': Selections.Cut('nCSCDTHits',
        lambda muon: muon.nCSCHits + muon.nDTHits,
        operator.gt, 12),
    'pTSig': Selections.Cut('pTSig',
        lambda muon: muon.ptError / muon.pt,
        operator.lt, 1.),
}

# define muon pair quality cuts
DIMUON_QUALITYCUTS = {
    'alpha': Selections.Cut(
        'alpha', lambda (m1,m2): m1.p4.Angle(m2.p4.Vect()),
        operator.gt, 2.9),
}


PTTHRESHOLDS = [23., 25., 28.]  # pT threshold values for matched HLT objects

# list of d0 intervals to process, "(None, None)" gives the d0-inclusive results
D0INTERVALS = (
    (None, None),
    (0,10),
    (10,50),
    (0,50),
    (50,100),
    (100,150),
    (150,250),
    (250,350),
    (250,1000),
    (350,1000),
)

L1THRESHOLDS = (0.0, 4.0, 5.0, 11.0, 12.0, 15.0)  # pT threshold values for L1 objects

matching_threshold_HLT = 0.2
matching_threshold_L1 = 1.2  # TODO deprecate this!


SINGLEMUVARIABLES = ['pT','eta','phi','charge','d0','x_fhit','y_fhit','z_fhit']
PAIRVARIABLES = ['pTdiff','deltaR','mass','cosAlpha','alpha','dimuonPTOverM', 'pairPT', 'chargeprod']
RESOLUTIONVARIABLES = ['L1pTres']
DIMUONVARIABLES = ['dimLxy','dimMass']


HEADERS = ('XTITLE', 'AXES', 'LAMBDA', 'PRETTY')
VALUES  = (
    ('pT' ,           'p_{T} [GeV]',      (1000,       0.,    500.), lambda muon: muon.pt                                , 'p_{T}'   ), 
    ('eta',           '#eta'       ,      (1000,      -3.,      3.), lambda muon: muon.eta                               , '#eta'    ),
    ('phi',           '#phi'       ,      (1000, -math.pi, math.pi), lambda muon: muon.phi                               , '#phi'    ),
    ('charge',        'q(#mu)'     ,         (4,       -2,       2), lambda muon: muon.charge                            , 'q(#mu)'  ),
    ('d0' ,           'd_{0} [cm]' ,      (1000,       0.,   1100.), lambda muon: abs(muon.d0())                         , 'd_{0}'   ),
    ('x_fhit',        'x_{innermost hit}',(1000,    -800.,    800.), lambda muon: muon.x_fhit                            , 'x_{innermost hit}'),
    ('y_fhit',        'y_{innermost hit}',(1000,    -800.,    800.), lambda muon: muon.y_fhit                            , 'y_{innermost hit}'),
    ('z_fhit',        'z_{innermost hit}',(1000,   -1100.,   1100.), lambda muon: muon.z_fhit                            , 'z_{innermost hit}'),
    ('pTdiff',        '(p_{T}^{upper}-p_{T}^{lower})/p_{T}^{lower}', (1000, -10., 100.), lambda (m1,m2): (m1.pt-m2.pt)/m2.pt, 'p_{T}^{upper}-p_{T}^{lower}/p_{T}^{lower}'),
    ('deltaR',        '#Delta R',         (1000,       0.,      5.), lambda (m1,m2): m1.p4.DeltaR(m2.p4)                 , '#DeltaR(#mu#mu)'),
    ('mass',          'M_{#mu#mu}',       (1000,       0.,    500.), lambda (m1,m2): (m1.p4+m2.p4).M()                   , 'M(#mu#mu) [GeV]'),
    ('cosAlpha',      'cos#alpha',        (1000,      -1.,      1.), lambda (m1,m2): m1.p4.Vect().Dot(m2.p4.Vect())/m1.p4.P()/m2.p4.P(),'cos(#alpha)'),
    ('alpha',         '#alpha',           (1000,       0., math.pi), lambda (m1,m2): m1.p4.Angle(m2.p4.Vect())           , 'cos(#alpha)'),
    ('dimuonPTOverM', 'dimuon p_{T} / M', (1000,       0.,     20.), lambda (m1,m2): (m1.p4+m2.p4).Pt()/(m1.p4+m2.p4).M(), 'p_{T} / M'),
    ('pairPT',        'pair p_{T}',       (1000,       0.,   1000.), lambda (m1,m2): (m1.p4+m2.p4).Pt()                  , 'pair p_{T}'),
    ('chargeprod',    'q(#mu_{1})#times q(#mu_{2})',(  4, -2.,  2.), lambda (m1,m2): m1.charge*m2.charge                 , 'q(#mu_{1},#mu_{2})'),
    ('L1pTres',       '(p_{T}^{DSA}-p_{T}^{L1})/p_{T}^{L1}', (1000, -2., 50.), lambda (dsamu,l1mu): (dsamu.pt-l1mu.pt)/l1mu.pt, '(p_{T}^{DSA}-p_{T}^{L1})/p_{T}^{L1}'),
    ('dimLxy',           'dim. L_{xy} [cm]', (1000,    0.,    500.), lambda dimuon: dimuon.Lxy()                         , 'dim. L_{xy}'  ),
    ('dimMass',           'dim. mass',    (1000,       0.,    500.), lambda dimuon: (dimuon.mu1.p4+dimuon.mu2.p4).M()    , 'dim. mass'  ),
)
CONFIG = {}
for VAL in VALUES:
    KEY, VALS = VAL[0], VAL[1:]
    CONFIG[KEY] = dict(zip(HEADERS, VALS))


###############################################################################

#### CLASS AND FUNCTION DEFINITIONS ####

# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):

    for d0min,d0max in D0INTERVALS:
        d0intervals_str = '__d0GT{}__d0LT{}'.format(d0min,d0max) if \
                d0min is not None and d0max is not None else ''

        self.HistInit('L1TObjectsPerHLTObject'+d0intervals_str, 'number of L1T muons per number of HLT muons', 40, 0, 10)
        self.HistInit('skippedEvents'+d0intervals_str, 'skipped events', 7, -2, 5)
        self.HistInit('selectedMuons'+d0intervals_str, 'selected muons', 2, 0, 2)
        self.HistInit('selectedMuonPairs'+d0intervals_str, 'selected dimuons', 2, 0, 2)
        self.HistInit('lowerLegMu_HLTmatches'+d0intervals_str, 'HLT matches for lower leg muon', 2, 0, 2)
        self.HistInit('lowerLegMu_L1matches'+d0intervals_str, 'L1 matches for lower leg muon', 2, 0, 2)
        self.HistInit('upperLegMu_HLTmatches'+d0intervals_str, 'HLT matches for upper leg muon', 2, 0, 2)
        self.HistInit('upperLegMu_L1matches'+d0intervals_str, 'L1 matches for upper leg muon', 2, 0, 2)
        self.HistInit('lowerLegMu_HLTmatches_upperLegMu_HLTmatches'+d0intervals_str, 'HLT matches for both lower and upper leg muons', 2, 0, 2)
        self.HistInit('lowerLegMu_HLTmatches_lowerLegMu_L1matches_upperLegMu_HLTmatches_upperLegMu_L1matches'+d0intervals_str, 'HLT and L1 matches for both lower and upper leg muons', 2, 0, 2)
        self.HistInit('identifiedDimuons'+d0intervals_str, 'identified dimuons', 2, 0, 2)

        for MUONTYPE in ('DSA',):
            for KEY in CONFIG:

                BASETITLE = ';'+CONFIG[KEY]['XTITLE']+';'+MUONTYPE+' '

                # define histograms for turn-on curves
                self.HistInit(MUONTYPE+'_'+KEY+'EffDen'+d0intervals_str,
                        BASETITLE+'Yield', *CONFIG[KEY]['AXES'])

                for L1threshold in L1THRESHOLDS:
                    for threshold in PTTHRESHOLDS:
                        self.HistInit(MUONTYPE+'_pTGT{}'.format(
                            str(threshold).replace('.','p'))+'_L1pTGT{}'.format(
                                str(L1threshold).replace('.','p'))+'_'+KEY+'EffNum'+d0intervals_str,
                            BASETITLE+'Efficiency', *CONFIG[KEY]['AXES'])

                # define histograms for simple distributions
                if KEY in PAIRVARIABLES:
                    self.HistInit(MUONTYPE+'_'+KEY+d0intervals_str,
                            BASETITLE+'Yield', *CONFIG[KEY]['AXES'])

                    self.HistInit(MUONTYPE+'_oppositeCharges'+'_'+KEY+d0intervals_str, BASETITLE+'Yield',
                                *CONFIG[KEY]['AXES'])
                    self.HistInit(MUONTYPE+'_equalCharges'+'_'+KEY+d0intervals_str, BASETITLE+'Yield',
                                *CONFIG[KEY]['AXES'])

                elif KEY in SINGLEMUVARIABLES:
                    for HEMISPHERE in ('_upperHemisphere', '_lowerHemisphere', ''):
                        self.HistInit(MUONTYPE+HEMISPHERE+'_'+KEY+d0intervals_str, BASETITLE+'Yield',
                                *CONFIG[KEY]['AXES'])
                        self.HistInit(MUONTYPE+HEMISPHERE+'_posCharge'+'_'+KEY+d0intervals_str, BASETITLE+'Yield',
                                *CONFIG[KEY]['AXES'])
                        self.HistInit(MUONTYPE+HEMISPHERE+'_negCharge'+'_'+KEY+d0intervals_str, BASETITLE+'Yield',
                                *CONFIG[KEY]['AXES'])

                elif KEY in RESOLUTIONVARIABLES:
                    self.HistInit(MUONTYPE+'_lowerHemisphere'+'_'+KEY+d0intervals_str, BASETITLE+'Yield',
                            *CONFIG[KEY]['AXES'])

                elif KEY in DIMUONVARIABLES:
                    self.HistInit(MUONTYPE+'_'+KEY+d0intervals_str,
                            BASETITLE+'Yield', *CONFIG[KEY]['AXES'])

# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    if not 'NoBPTX' in self.NAME:
        raise NotImplementedError('[ANALYZER ERROR]: Non-NoBPTX datasets are not supported')

    HLTpaths, HLTmuons, L1Tmuons = E.getPrimitives('TRIGGER')
    DSAmuons = E.getPrimitives('DSAMUON')
    DIMUONS = E.getPrimitives('DIMUON')

    event = E.getPrimitives('EVENT')

    # if True: #len(HLTmuons) != len(L1Tmuons):
    #     print(event)
    #     for HLTpath in HLTpaths: print(HLTpath)
    #     for HLTmuon in HLTmuons:
    #         print(HLTmuon)

    #     print('\n')
    #     for L1Tmuon in L1Tmuons:
    #         print(L1Tmuon)

    #     print('\n')

    #     print('##########\n\n')

    for d0min,d0max in D0INTERVALS:
        # is_event_printed = False  # TODO remove temporary variable

        d0intervals_str = '__d0GT{}__d0LT{}'.format(d0min,d0max) if \
                d0min is not None and d0max is not None else ''

        self.HISTS['L1TObjectsPerHLTObject'+d0intervals_str].Fill(1.*len(L1Tmuons)/len(HLTmuons))

        do_skip_event = False

        # Accept only events that pass the following HLT triggers
        accepted_HLTpaths = ['HLT_L2Mu10_NoVertex_NoBPTX3BX']
        HLTpaths_list = [str(path) for path in HLTpaths]
        if not any([any([(accepted_path in HLTpath) for accepted_path in accepted_HLTpaths]) for HLTpath in HLTpaths_list]):
            do_skip_event = True

        if do_skip_event:
            self.HISTS['skippedEvents'+d0intervals_str].Fill(0)
            return

        for MUONTYPE, MUONS in (('DSA', DSAmuons),):

            # discard events with too few reco muons
            if len(MUONS) < 2:
                self.HISTS['skippedEvents'+d0intervals_str].Fill(1)
                continue

            accepted_muons = []
            accepted_matchedMuons = []
            accepted_matchedHLTMuons = []

            for muon in MUONS:

                # apply single muon quality cuts
                do_skip_muon = False
                for var in SINGLEMU_QUALITYCUTS.keys():
                    if not SINGLEMU_QUALITYCUTS[var].apply(muon):
                        do_skip_muon = True

                # apply additional d0 cuts
                if d0min is not None and d0max is not None:
                    if not (d0min <= abs(muon.d0()) < d0max):
                        do_skip_muon = True

                if do_skip_muon:
                    self.HISTS['selectedMuons'+d0intervals_str].Fill(0)
                    continue

                # store muon
                accepted_muons.append(muon)

                # store muon if matched
                muonMatches = matchedMuons(muon, HLTmuons, threshold=matching_threshold_HLT)
                if len(muonMatches) > 0:
                    accepted_matchedMuons.append(muon)
                    accepted_matchedHLTMuons.append(muonMatches[0]['muon'])

            # skip event if there are no HLT-matched muons at all
            if len(accepted_matchedMuons) < 1: 
                self.HISTS['skippedEvents'+d0intervals_str].Fill(2)
                continue


            # further cleanup of the selected muons: find the most cosmic-like pair
            # by requiring different hemispheres and a large angle between the muons
            temp_maxalpha = -1
            selected_muonpair = ()
            for m1,m2 in list(itertools.combinations(accepted_muons, 2)):
                # require at least one muon to be matched to an HLT object
                if all([m not in accepted_matchedMuons for m in (m1,m2)]):
                    continue

                # require the muons to be in different detector hemispheres
                if ([hemisphere(m1), hemisphere(m2)]).count('upper') != 1:
                    continue

                # find muon with the largest alpha(mu,mu)
                temp_alpha = CONFIG['alpha']['LAMBDA']((m1,m2))
                if temp_alpha > temp_maxalpha:
                    temp_maxalpha = temp_alpha
                    selected_muonpair = (m1,m2)

            # skip events which have all muons in the same hemisphere
            if len(selected_muonpair) == 0:
                self.HISTS['skippedEvents'+d0intervals_str].Fill(3)
                continue

            # apply "dimuon" quality cuts
            do_skip_dimuon = False
            for var in DIMUON_QUALITYCUTS.keys():
                if not DIMUON_QUALITYCUTS[var].apply(
                        (selected_muonpair[0], selected_muonpair[1])):
                    do_skip_dimuon = True

            if do_skip_dimuon:
                self.HISTS['selectedMuonPairs'+d0intervals_str].Fill(0)
                continue
            else:
                self.HISTS['selectedMuonPairs'+d0intervals_str].Fill(1)


            m1,m2 = selected_muonpair

            # check whether the selected two muons belong to a dimuon
            # (i.e., have a dimuon vertex)
            for dimuon in DIMUONS:
                if dimuon.idx1 == m1.idx and dimuon.idx2 == m2.idx or \
                        dimuon.idx1 == m2.idx and dimuon.idx2 == m1.idx:
                    is_dimuon = True
                    break
            else:
                is_dimuon = False

            if is_dimuon:
                self.HISTS['identifiedDimuons'+d0intervals_str].Fill(1)
            else:
                self.HISTS['identifiedDimuons'+d0intervals_str].Fill(0)


            # # print event info for edmPickEvents.py
            # print('{}:{}:{}'.format(event.run, event.lumi, event.event))  # TODO


            ###############################################################
            ##################### fill the histograms #####################
            ###############################################################

            # fill simple yield histograms
            for KEY in CONFIG:
                F = CONFIG[KEY]['LAMBDA']

                if KEY in PAIRVARIABLES:
                    self.HISTS[MUONTYPE+'_'+KEY+d0intervals_str].Fill(F((m1,m2)))

                    if m1.charge * m2.charge < 0:
                        self.HISTS[MUONTYPE+'_oppositeCharges'+'_'+KEY+d0intervals_str].Fill(
                                F((m1, m2)))
                    else:
                        self.HISTS[MUONTYPE+'_equalCharges'+'_'+KEY+d0intervals_str].Fill(
                                F((m1,m2)))

                elif KEY in SINGLEMUVARIABLES:
                    for muon in selected_muonpair:
                        self.HISTS[MUONTYPE+'_'+KEY+d0intervals_str].Fill(F(muon))
                        if muon.charge > 0:
                            self.HISTS[MUONTYPE+'_posCharge'+'_'+KEY+d0intervals_str].Fill(F(muon))
                        else:
                            self.HISTS[MUONTYPE+'_negCharge'+'_'+KEY+d0intervals_str].Fill(F(muon))

                        if hemisphere(muon) == 'upper':
                            self.HISTS[MUONTYPE+'_upperHemisphere'+'_'+KEY+d0intervals_str].Fill(F(muon))
                            if muon.charge > 0:
                                self.HISTS[MUONTYPE+'_upperHemisphere'+'_posCharge'+'_'+KEY+d0intervals_str].Fill(F(muon))
                            else:
                                self.HISTS[MUONTYPE+'_upperHemisphere'+'_negCharge'+'_'+KEY+d0intervals_str].Fill(F(muon))
                        else:
                            self.HISTS[MUONTYPE+'_lowerHemisphere'+'_'+KEY+d0intervals_str].Fill(F(muon))
                            if muon.charge > 0:
                                self.HISTS[MUONTYPE+'_lowerHemisphere'+'_posCharge'+'_'+KEY+d0intervals_str].Fill(F(muon))
                            else:
                                self.HISTS[MUONTYPE+'_lowerHemisphere'+'_negCharge'+'_'+KEY+d0intervals_str].Fill(F(muon))

                elif KEY in DIMUONVARIABLES:
                    for dimuon in DIMUONS:
                        if (dimuon.idx1 == selected_muonpair[0].idx and dimuon.idx2 == selected_muonpair[1].idx) or \
                                (dimuon.idx1 == selected_muonpair[1].idx and dimuon.idx2 == selected_muonpair[0].idx):
                            self.HISTS[MUONTYPE+'_'+KEY+d0intervals_str].Fill(F(dimuon))

                elif KEY in RESOLUTIONVARIABLES:
                    pass  # resolution variables are processed further below

                else:
                    print('[ANALYZER WARNING] Key {} not processed'.format(KEY))


            # fill turn-on histograms
            lowerHSmuon = m1 if hemisphere(m1) == 'lower' else m2
            upperHSmuon = m1 if hemisphere(m1) == 'upper' else m2

            # match lower-HS muon
            muonMatches = matchedMuons(lowerHSmuon, HLTmuons, threshold=matching_threshold_HLT)
            if len(muonMatches) > 0:
                is_matched_lowerHSmuon_HLT = True
                self.HISTS['lowerLegMu_HLTmatches'+d0intervals_str].Fill(1)

                # # TODO
                # if len(HLTmuons) != len(L1Tmuons):
                #     print('##################################################')
                #     print(event)
                #     print('\nselected DSA muon (lower HS):')
                #     print(lowerHSmuon)
                #     # print('d0 = {}'.format(lowerHSmuon.d0()))
                #     for HLTpath in HLTpaths: print(HLTpath)
                #     print('\nHLT muons:')
                #     for HLTmuon in HLTmuons: print(HLTmuon)
                #         # if all([SINGLEMU_QUALITYCUTS[var].apply(HLTmuon) for var in SINGLEMU_QUALITYCUTS.keys()]): print(HLTmuon)
                #     print('\nL1 muons:')
                #     for L1Tmuon in L1Tmuons: print(L1Tmuon)

                lowerHSmuon_HLTmatch = muonMatches[0]['muon']

                # find the associated L1 muon
                muonMatches_L1 = matchedMuons(lowerHSmuon, L1Tmuons, threshold=matching_threshold_L1)
                if len(muonMatches_L1) > 0:
                    is_matched_lowerHSmuon_L1 = True
                    self.HISTS['lowerLegMu_L1matches'+d0intervals_str].Fill(1)
                    lowerHSmuon_L1muon = muonMatches_L1[0]['muon']
                    # print('[INFO] L1 muon match found\n')
                    # print('[DUMP] selected lower-HS DSA muon:')
                    # print(lowerHSmuon)
                    # print('\n[DUMP] available L1 muons (at least one of them is matched):')
                    # for L1muon in L1Tmuons: print(L1muon)
                    # print('\n[DUMP] available HLT paths:')
                    # for HLTpath in HLTpaths: print(HLTpath)

                    for KEY in RESOLUTIONVARIABLES:
                        self.HISTS[MUONTYPE+'_lowerHemisphere'+'_'+KEY+d0intervals_str].Fill(
                                CONFIG[KEY]['LAMBDA']((lowerHSmuon, lowerHSmuon_L1muon)))

                else:
                    is_matched_lowerHSmuon_L1 = False
                    self.HISTS['lowerLegMu_L1matches'+d0intervals_str].Fill(0)
                    lowerHSmuon_L1muon = None
                    # print('[INFO] L1 muon match NOT found\n')
                    # print('[DUMP] selected lower-HS DSA muon:')
                    # print(lowerHSmuon)
                    # print('\n[DUMP] available L1 muons (none of them are matched):')
                    # for L1muon in L1Tmuons: print(L1muon)
                    # print('\n[DUMP] available HLT paths:')
                    # for HLTpath in HLTpaths: print(HLTpath)


                for KEY in CONFIG:
                    if KEY in SINGLEMUVARIABLES:
                        F = CONFIG[KEY]['LAMBDA']
                        self.HISTS[MUONTYPE+'_'+KEY+'EffDen'+d0intervals_str].Fill(F(lowerHSmuon))
                        for HLTthreshold in PTTHRESHOLDS:
                            for L1threshold in L1THRESHOLDS:
                                if lowerHSmuon_HLTmatch.pt > HLTthreshold:
                                    passed_HLT = True
                                else:
                                    passed_HLT = False

                                if lowerHSmuon_L1muon is not None and lowerHSmuon_L1muon.pt > L1threshold:
                                    passed_L1 = True
                                else:
                                    passed_L1 = False

                                if passed_HLT and passed_L1:
                                    self.HISTS[MUONTYPE+'_pTGT{}'.format(str(HLTthreshold).replace('.','p'))+'_L1pTGT{}'.format(str(L1threshold).replace('.','p'))+'_'+KEY+'EffNum'+d0intervals_str].Fill(F(lowerHSmuon))

            else:
                # print('No HLT match found. Printing event information...')
                # print((event))
                is_matched_lowerHSmuon_HLT = False
                self.HISTS['lowerLegMu_HLTmatches'+d0intervals_str].Fill(0)

            # match upper-HS muon
            muonMatches = matchedMuons(upperHSmuon, HLTmuons, threshold=matching_threshold_HLT)
            if len(muonMatches) > 0:
                is_matched_upperHSmuon_HLT = True
                self.HISTS['upperLegMu_HLTmatches'+d0intervals_str].Fill(1)

                muonMatches_L1 = matchedMuons(upperHSmuon, L1Tmuons, threshold=matching_threshold_L1)
                if len(muonMatches_L1) > 0:
                    is_matched_upperHSmuon_L1 = True
                    self.HISTS['upperLegMu_L1matches'+d0intervals_str].Fill(1)
                else:
                    is_matched_upperHSmuon_L1 = False
                    self.HISTS['upperLegMu_L1matches'+d0intervals_str].Fill(0)

            else:
                is_matched_upperHSmuon_HLT = False
                self.HISTS['upperLegMu_HLTmatches'+d0intervals_str].Fill(0)

            if is_matched_lowerHSmuon_HLT and is_matched_upperHSmuon_HLT:
                self.HISTS['lowerLegMu_HLTmatches_upperLegMu_HLTmatches'+d0intervals_str].Fill(1)

                # # TODO
                # if len(HLTmuons) != len(L1Tmuons):
                #     print('##################################################')
                #     print(event)
                #     print('\nselected DSA muon (lower HS):')
                #     print(lowerHSmuon)
                #     print('\nselected DSA muon (upper HS):')
                #     print(upperHSmuon)
                #     # print('d0 = {}'.format(lowerHSmuon.d0()))
                #     for HLTpath in HLTpaths: print(HLTpath)
                #     print('\nHLT muons:')
                #     for HLTmuon in HLTmuons: print(HLTmuon)
                #         # if all([SINGLEMU_QUALITYCUTS[var].apply(HLTmuon) for var in SINGLEMU_QUALITYCUTS.keys()]): print(HLTmuon)
                #     print('\nL1 muons:')
                #     for L1Tmuon in L1Tmuons: print(L1Tmuon)


            else:
                self.HISTS['lowerLegMu_HLTmatches_upperLegMu_HLTmatches'+d0intervals_str].Fill(0)

            if is_matched_lowerHSmuon_HLT and is_matched_lowerHSmuon_L1 and is_matched_upperHSmuon_HLT and is_matched_upperHSmuon_L1:
                self.HISTS['lowerLegMu_HLTmatches_lowerLegMu_L1matches_upperLegMu_HLTmatches_upperLegMu_L1matches'+d0intervals_str].Fill(1)
            else:
                self.HISTS['lowerLegMu_HLTmatches_lowerLegMu_L1matches_upperLegMu_HLTmatches_upperLegMu_L1matches'+d0intervals_str].Fill(0)

            # count accepted events
            self.HISTS['skippedEvents'+d0intervals_str].Fill(-1)


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
    for CUT_SET in (SINGLEMU_QUALITYCUTS, DIMUON_QUALITYCUTS):
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
            path='roots/testing/',
            prefix='test_cosmicsPlots')

    analyzer.writeHistograms(outputname)
