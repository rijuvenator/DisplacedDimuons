import math
import operator
import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Analysis.Primitives as Primitives
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedMuons

# specifiy which muon to process ('subleading', 'largestD0')
MUON_TO_PROCESS = 'largestD0'

# specify whether selection cuts should be applied on GEN level
SELECT_ON_GEN_LEVEL = True

# define cuts that are applied to all objects
MUONCUTS = {
        'pT': Selections.Cut(
            'pT', lambda muon: muon.pt,
            operator.gt, 30.),
        'eta': Selections.Cut(
            'eta', lambda muon: abs(muon.eta),
            operator.lt, 2.0),
        # 'd0': Selections.Cut(
        #     'd0', lambda muon: abs(muon.d0()),
        #     operator.lt, 7.0),
}

MUONCUTS_RECOONLY = {
        'nStations': Selections.Cut('nStations',
            lambda muon: muon.nDTStations + muon.nCSCStations,
            operator.gt, 1),
}

DIMUONCUTS = {
        'mass': Selections.Cut(
            'mass', lambda (m1,m2): (m1.p4+m2.p4).M(),
            operator.gt, 15.),
        'deltaRleft': Selections.Cut(
            'deltaRleft', lambda (m1,m2): m1.p4.DeltaR(m2.p4),
            operator.gt, 0.5),
        # 'deltaRright': Selections.Cut(
        #     'deltaRright', lambda (m1,m2): m1.p4.DeltaR(m2.p4),
        #     operator.lt, 2.5),
        'cosAlpha': Selections.Cut(
            'cosAlpha', lambda (m1,m2): m1.p4.Vect().Dot(m2.p4.Vect())/m1.p4.P()/m2.p4.P(),
            operator.gt, -0.8),
}

XCUTS = {
        # 'XBeta': Selections.Cut(
        #     'XBeta', lambda X: X.p4.Beta(),
        #     operator.gt, 0.7),
}

PAIRVARIABLES = ['XBeta','deltaR','mass','cosAlpha','dimuonPTOverM']  # include XBeta here for technical reasons

d0max = 150. if 'd0' not in MUONCUTS.keys() else MUONCUTS['d0'].val+3

HEADERS = ('XTITLE', 'AXES', 'LAMBDA', 'PRETTY')
VALUES  = (
    ('pT' ,           'p_{T} [GeV]',      (1000,       0.,    500.), lambda muon: muon.pt                                , 'p_{T}'   ), 
    ('eta',           '#eta'       ,      (1000,      -3.,      3.), lambda muon: muon.eta                               , '#eta'    ),
    ('phi',           '#phi'       ,      (1000, -math.pi, math.pi), lambda muon: muon.phi                               , '#phi'    ),
    ('Lxy',           'gen. L_{xy} [cm]', (1000,       0.,    500.), lambda muon: muon.Lxy()                             , 'L_{xy}'  ),
    ('d0' ,           'd_{0} [cm]' ,      (1000,       0.,   d0max), lambda muon: abs(muon.d0())                         , 'd_{0}'   ),
    ('XBeta',         '#beta_{X}',        (1000,       0.,      1.), lambda X   : X.p4.Beta()                            , '#beta_{X}'),
    ('deltaR',        '#Delta R',         (1000,       0.,      5.), lambda (m1,m2): m1.p4.DeltaR(m2.p4)                 , '#DeltaR(#mu#mu)'),
    ('mass',          'M_{#mu#mu}',       (1000,       0.,    500.), lambda (m1,m2): (m1.p4+m2.p4).M()                   , 'M(#mu#mu) [GeV]'),
    ('cosAlpha',      'cos#alpha',        (1000,      -1.,      1.), lambda (m1,m2): m1.p4.Vect().Dot(m2.p4.Vect())/m1.p4.P()/m2.p4.P(),'cos(#alpha)'),
    ('dimuonPTOverM', 'dimuon p_{T} / M', (1000,       0.,     20.), lambda (m1,m2): (m1.p4+m2.p4).Pt()/(m1.p4+m2.p4).M(), 'p_{T} / M'),
)
CONFIG = {}
for VAL in VALUES:
    KEY, VALS = VAL[0], VAL[1:]
    CONFIG[KEY] = dict(zip(HEADERS, VALS))


###############################################################################

# sanity checks
if MUON_TO_PROCESS not in ['subleading', 'largestD0']:
    raise NotImplementedError('Invalid value of MUON_TO_PROCESS. Available '
            'options: subleading, largestD0')


#### CLASS AND FUNCTION DEFINITIONS ####

# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    for KEY in CONFIG:
        for MUONTYPE in ('GEN','DSA','RSA'):
            # if KEY == 'd0':
            #     BASETITLE = BASETITLE.replace(CONFIG[KEY]['XTITLE'],
            #             'max. '+CONFIG[KEY]['XTITLE'])
            # else:
            #     BASETITLE = BASETITLE.replace(CONFIG[KEY]['XTITLE'],
            #             CONFIG[KEY]['XTITLE']+' (of max-d_{0} muon)')

            BASETITLE = ';'+CONFIG[KEY]['XTITLE']+';'+MUONTYPE+' '
            self.HistInit(MUONTYPE+'_'+KEY+'Num', BASETITLE+'Trigger Efficiency',
                    *CONFIG[KEY]['AXES'])
            self.HistInit(MUONTYPE+'_'+KEY+'Den', BASETITLE+'Yield',
                    *CONFIG[KEY]['AXES'])


# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    if '4Mu' in self.NAME:
        raise NotImplementedError('[ANALYZER ERROR]: 4Mu samples are not '
                'supported yet')

    if self.SP is None:
        raise NotImplementedError('[ANALYZER ERROR]: This script runs on '
                'signal samples only.')

    mu1, mu2, j1, j2, X, XP, H, P, extramu = E.getPrimitives('GEN')
    GENmuons = (mu1, mu2)
    
    HLTpaths, HLTmuons, L1Tmuons = E.getPrimitives('TRIGGER')

    DSAmuons = E.getPrimitives('DSAMUON')
    RSAmuons = E.getPrimitives('RSAMUON')

    # denominator matching: define which types of muons are to be matched with
    # which other types of muons
    matchWith_den = {
        'GEN': None,
        'DSA': GENmuons,
        'RSA': GENmuons,
    }

    # numerator matching: define which types of muons are to be matched with
    # which other types of muons (NB: the denominator matching automatically
    # applies to the numberator muons, so no need to re-declare it here)
    matchWith_num = {
        'GEN': HLTmuons,
        'DSA': HLTmuons,
        'RSA': HLTmuons,
    }

    do_skip_event = False
    for var in XCUTS.keys():
        if not XCUTS[var].apply(X): do_skip_event = True

    if do_skip_event: return


    for MUONTYPE,MUONS in (('GEN',GENmuons), ('DSA',DSAmuons),
            ('RSA',RSAmuons)):

        # loop over the entire event and collect the selected muons, separately
        # for the denominator and the numerator (but do not fill any histograms
        # yet)
        accepted_muons_den = []
        accepted_muons_num = []
        for muon in MUONS:

            # apply selections: skip muons that do not pass the cuts
            do_skip_muon = False
            for var in MUONCUTS.keys():
                if SELECT_ON_GEN_LEVEL is True:
                    selection_muon = getGENmuon(muon, GENmuons)
                    if selection_muon is None: do_skip_muon = True
                else:
                    selection_muon = muon

                # apply MUONCUTS
                if selection_muon is not None and not MUONCUTS[var].apply(
                        selection_muon):
                    do_skip_muon = True

            # apply MUONCUTS_RECOONLY
            if MUONTYPE != 'GEN':
                for var in MUONCUTS_RECOONLY.keys():
                    if not MUONCUTS_RECOONLY[var].apply(muon):
                        do_skip_muon = True

            # apply Lxy cuts
            temp_gen_mu = getGENmuon(muon, GENmuons)
            if temp_gen_mu is not None:
                if LXYMIN is not None and \
                        temp_gen_mu.Lxy() < LXYMIN:
                    do_skip_muon = True
                if LXYMAX is not None and \
                        temp_gen_mu.Lxy() > LXYMAX:
                    do_skip_muon = True
            else:
                do_skip_muon = True

            if do_skip_muon: continue

            # denominator: match the current muon if it's supposed to be matched
            if matchWith_den[MUONTYPE] is not None:
                muonMatches_den = matchedMuons(muon, matchWith_den[MUONTYPE])
                if len(muonMatches_den) != 0:
                    # collect the matched muon for the denominator
                    accepted_muons_den.append(muon)

                    # numerator: match the current muon if it is supposed to be
                    # matched
                    if matchWith_num[MUONTYPE] is not None:
                        matchedMuons_den_num = matchedMuons(muon,
                                matchWith_num[MUONTYPE])
                        if len(matchedMuons_den_num) != 0:
                            # collect the matched muon for the numerator
                            accepted_muons_num.append(muon)

                    else:
                        # numerator: just collect the muon if it is not supposed
                        # to be matched
                        accepted_muons_num.append(muon)

            else:
                # denominator: just collect the muon if it is not supposed to
                # be matched
                accepted_muons_den.append(muon)

                # numerator: match the current muon if it is supposed to be
                # matched
                if matchWith_num[MUONTYPE] is not None:
                    matchedMuons_den_num = matchedMuons(muon,
                            matchWith_num[MUONTYPE])
                    if len(matchedMuons_den_num) != 0:
                        # collect the matched muons for the numerator
                        accepted_muons_num.append(muon)

                else:
                    # numerator: just collect the muon if it is not supposed
                    # to be matched
                    accepted_muons_num.append(muon)

        # skip the event if not enough muons pass the selection for the
        # denominator
        if len(accepted_muons_den) < 2: continue

        # apply dimuon selections
        if SELECT_ON_GEN_LEVEL is True:
            temp_mu1 = getGENmuon(accepted_muons_den[0], GENmuons)
            temp_mu2 = getGENmuon(accepted_muons_den[1], GENmuons)
        else:
            temp_mu1 = accepted_muons_den[0]
            temp_mu2 = accepted_muons_den[1]

        do_skip_dimuon = False
        for var in DIMUONCUTS.keys():
            if not DIMUONCUTS[var].apply((temp_mu1,temp_mu2)):
                do_skip_dimuon = True

        if do_skip_dimuon: continue

        # sort collected muons according to their pT (descending order),
        # if applicable
        if MUON_TO_PROCESS == 'subleading':
            accepted_muons_den.sort(key=lambda m: m.pt, reverse=True)
            muon_den = accepted_muons_den[1]
        elif MUON_TO_PROCESS == 'largestD0':
            if abs(accepted_muons_den[0].d0())>abs(accepted_muons_den[1].d0()):
                muon_den = accepted_muons_den[0]
            else:
                muon_den = accepted_muons_den[1]

        # if existing, select the same muon for the numerator
        for m in accepted_muons_num:
            if m == muon_den:
                muon_num = m
                break
        else:
            muon_num = None

        # fill the histograms
        for KEY in CONFIG:
            F = CONFIG[KEY]['LAMBDA']

            if KEY not in PAIRVARIABLES:
                if MUONTYPE in ['DSA','RSA'] and KEY == 'Lxy':
                    gen_muon_den = getGENmuon(muon_den, GENmuons)
                    if gen_muon_den is not None:
                        self.HISTS[MUONTYPE+'_'+KEY+'Den'].Fill(
                                F(gen_muon_den))

                        # fill the numberator only if there are at least two
                        # muons in the event that satisfy the numerator matching
                        # requirement
                        if muon_num is not None and len(accepted_muons_num) > 1:
                            # muon_num and muon_den are the same object at this
                            # point, so they have the same Lxy
                            self.HISTS[MUONTYPE+'_'+KEY+'Num'].Fill(
                                    F(gen_muon_den))

                else:
                    self.HISTS[MUONTYPE+'_'+KEY+'Den'].Fill(F(muon_den))

                    # fill the numerator only if there are at least two
                    # muons in the event that satisfy the numerator matching
                    # requirement
                    if muon_num is not None and len(accepted_muons_num) > 1:
                        self.HISTS[MUONTYPE+'_'+KEY+'Num'].Fill(F(muon_num))

            elif len(accepted_muons_den) > 1:
                if KEY == 'dimuonPTOverM':
                    temp_mu1 = getGENmuon(accepted_muons_den[0], GENmuons)
                    temp_mu2 = getGENmuon(accepted_muons_den[1], GENmuons)
                    if temp_mu1 is not None and temp_mu2 is not None:
                        if abs(temp_mu1.Lxy() - temp_mu2.Lxy()) < 1e-3:
                            self.HISTS[MUONTYPE+'_'+KEY+'Den'].Fill(F((
                                    accepted_muons_den[0],
                                    accepted_muons_den[1])))

                            if len(accepted_muons_num) > 1:
                                self.HISTS[MUONTYPE+'_'+KEY+'Num'].Fill(F((
                                        accepted_muons_num[0],
                                        accepted_muons_num[1])))

                elif KEY == 'XBeta':
                    if MUONTYPE == 'GEN':
                        self.HISTS[MUONTYPE+'_'+KEY+'Den'].Fill(F(X))
                        if len(accepted_muons_num) > 1:
                            self.HISTS[MUONTYPE+'_'+KEY+'Num'].Fill(F(X))

                else:
                    self.HISTS[MUONTYPE+'_'+KEY+'Den'].Fill(
                            F((accepted_muons_den[0], accepted_muons_den[1])))

                    if len(accepted_muons_num) > 1:
                        self.HISTS[MUONTYPE+'_'+KEY+'Num'].Fill(
                            F((accepted_muons_num[0], accepted_muons_num[1])))


def getGENmuon(muon, GENmuons):
    if isinstance(muon, Primitives.GenMuon):
        return muon
    else:
        matchedGenMuons = matchedMuons(muon, GENmuons)
        if len(matchedGenMuons) != 0:
            return GENmuons[matchedGenMuons[0]['idx']]
        else:
            return None


def parse_filename(path='roots/', prefix='', suffix='', fext='.root'):
    OpStr_as_FStr = {
        '>': 'GT',
        '<': 'LT',
        u'\u2265': 'GE',
        u'\u2264': 'LE',
    }

    cut_variables = {}
    for CUT_SET in (MUONCUTS, DIMUONCUTS, XCUTS):
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
    Analyzer.PARSER.add_argument('--minLxy',
            dest='LXYMIN',
            type=float,
            default=None)
    Analyzer.PARSER.add_argument('--maxLxy',
            dest='LXYMAX',
            type=float,
            default=None)

    ARGS = Analyzer.PARSER.parse_args()
    LXYMIN = ARGS.LXYMIN
    LXYMAX = ARGS.LXYMAX

    Analyzer.setSample(ARGS)

    for METHOD in ('declareHistograms', 'analyze'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])
    
    analyzer = Analyzer.Analyzer(
            ARGS = ARGS,
            BRANCHKEYS = ('GEN', 'DSAMUON', 'RSAMUON', 'TRIGGER'),
    )

    LXYMIN_str = '_LxyGT{}'.format(int(LXYMIN) if LXYMIN is not None else '0')
    LXYMAX_str = '_LxyLT{}'.format(int(LXYMAX) if LXYMAX is not None else 'Inf')

    outputname = parse_filename(
            path='roots/testing/',
            prefix='temp_STEplots',
            suffix=(LXYMIN_str+LXYMAX_str))
    analyzer.writeHistograms(outputname)
