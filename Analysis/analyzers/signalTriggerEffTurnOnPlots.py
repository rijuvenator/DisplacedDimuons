import math
import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedMuons


HEADERS = ('XTITLE', 'AXES', 'LAMBDA', 'PRETTY')
VALUES  = (
    ('pT' , 'p_{T} [GeV]', (1000,       0.,    500.), lambda muon: muon.pt       , 'p_{T}' ), 
    ('eta', '#eta'       , (1000,      -3.,      3.), lambda muon: muon.eta      , '#eta'  ),
    ('phi', '#phi'       , (1000, -math.pi, math.pi), lambda muon: muon.phi      , '#phi'  ),
    ('Lxy', 'L_{xy}^{gen} [cm]', (1000, 0.,    500.), lambda muon: muon.Lxy()    , 'L_{xy}'),
    ('d0' , 'd_{0} [cm]' , (1000,     -10.,     10.), lambda muon: muon.d0()     , 'd_{0}' ),
)
CONFIG = {}
for VAL in VALUES:
    KEY, VALS = VAL[0], VAL[1:]
    CONFIG[KEY] = dict(zip(HEADERS, VALS))


#### CLASS AND FUNCTION DEFINITIONS ####

# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    for KEY in CONFIG:
        # one Eff plot for each of DSA and RSA
        for MUON in ('GEN','DSA','RSA'):
            TITLE = ';'+CONFIG[KEY]['XTITLE']+';'+MUON+' Trigger Efficiency'
            self.HistInit(MUON+'_'+KEY+'Eff'      , TITLE, *CONFIG[KEY]['AXES'])

            # gen denominator plots, can reuse the axes
            self.HistInit(MUON+'_'+KEY+'Den'      , ''   , *CONFIG[KEY]['AXES'])
            # self.HistInit(MUON+'_'+KEY+'FullDen'    , '', *CONFIG[KEY]['AXES'])


# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    if self.SP is None:
        raise RuntimeError('[ANALYZER ERROR]: This script runs on signal only.')
    if '4Mu' in self.NAME:
        mu11, mu12, mu21, mu22, X1, X2, H, P, extramu = E.getPrimitives('GEN')
        GENmuons  = (mu11, mu12, mu21, mu22)
    elif '2Mu2J' in self.NAME:
        mu1, mu2, j1, j2, X, XP, H, P, extramu = E.getPrimitives('GEN')
        GENmuons = (mu1, mu2)

    HLTPaths, HLTMuons, L1TMuons = E.getPrimitives('TRIGGER')

    DSAmuons = E.getPrimitives('DSAMUON')
    RSAmuons = E.getPrimitives('RSAMUON')

    # define which muon type the "denominator muons" should be matched with
    matchWith_den = {
        'GEN': None,
        'DSA': GENmuons,
        'RSA': GENmuons,
    }

    # define which muon type the "numerator muons" should be matched with (in
    # addition to the matching of the "denominator muons"
    matchWith_num = {
        'GEN': HLTMuons,
        'DSA': HLTMuons,
        'RSA': HLTMuons,
    }

    for MUONTYPE, MUONS in (('GEN', GENmuons), ('DSA', DSAmuons),
            ('RSA', RSAmuons)):

        # loop over the entire event and collect the selected muons, for the
        # denominator and the numerator separately
        accepted_muons_den = []
        accepted_muons_num = []
        for muon in MUONS:
            # apply selections
            if not Selections.CUTS['eta'].apply(muon): continue
            if MUONTYPE != 'GEN' and \
                    Selections.CUTS['nStations'].expr(muon) <= 1: continue

            # match the current muon if it is supposed to be matched for the
            # denominator
            if matchWith_den[MUONTYPE] is not None:
                muonMatches_den = matchedMuons(muon, matchWith_den[MUONTYPE])
                if len(muonMatches_den) != 0:
                    # collect the matched muon for the denominator
                    accepted_muons_den.append(muon)

                    # match the current muon if it is supposed to be matched for
                    # the numerator
                    if matchWith_num[MUONTYPE] is not None:
                        matchedMuons_den_num = matchedMuons(muon,
                                matchWith_num[MUONTYPE])
                        if len(matchedMuons_den_num) != 0:
                            # collect the matched muon for the numerator
                            accepted_muons_num.append(muon)

                    # just collect the muon if it is not supposed to be matched
                    # for the numerator
                    else:
                        accepted_muons_num.append(muon)

            # just collect the muon if it is not supposed to be matched for the
            # denominator
            else:
                accepted_muons_den.append(muon)

                # match the current muon if it is supposed to be matched for the
                # numerator
                if matchWith_num[MUONTYPE] is not None:
                    matchedMuons_den_num = matchedMuons(muon,
                            matchWith_num[MUONTYPE])
                    if len(matchedMuons_den_num) != 0:
                        # collect the matched muon for the numerator
                        accepted_muons_num.append(muon)

                # just collect the muon if it is not supposed to be matched for
                # the numerator
                else:
                    accepted_muons_num.append(muon)

        # sort collected muons according to their pT (in descending order)
        accepted_muons_den.sort(key=lambda m: m.pt, reverse=True)
        # accepted_muons_num.sort(key=lambda m: m.pt, reverse=True)

        # skip the event if not enough muons pass the selection for the
        # denominator
        if len(accepted_muons_den) < 2: continue

        # select the subleading denominator muon for further processing
        muon_den = accepted_muons_den[1]

        # if existing, select the same muon for the numerator
        muon_num = None
        for m in accepted_muons_num:
            if m == muon_den:
                muon_num = m
            else:
                pass

        # fill the histograms
        for KEY in CONFIG:
            F = CONFIG[KEY]['LAMBDA']
            if MUONTYPE in ['DSA', 'RSA'] and KEY == 'Lxy':
                Lxy = getMuonGenLxy(muon_den, GENmuons)
                if Lxy is not None:
                    self.HISTS[MUONTYPE+'_'+KEY+'Den'].Fill(Lxy)
                if muon_num is not None and len(accepted_muons_num) >= 2 and \
                        Lxy is not None:
                    # muon_den and muon_num are the same object at this point,
                    # so they have the same Lxy
                    self.HISTS[MUONTYPE+'_'+KEY+'Eff'].Fill(Lxy)

            else:
                self.HISTS[MUONTYPE+'_'+KEY+'Den'].Fill(F(muon_den))

                # fill the numerator only if there are at least two muons in the
                # event that satisfy the "numerator (matching) requirement"
                if muon_num is not None and len(accepted_muons_num) >= 2:
                    self.HISTS[MUONTYPE+'_'+KEY+'Eff'].Fill(F(muon_num))


def getMuonGenLxy(muon, genMuons):
    try:
        Lxy = muon.Lxy()
    except:
        matchedGenMuons = matchedMuons(muon, genMuons)
        if len(matchedGenMuons) == 0:
            return None
        closestGenMuon = genMuons[matchedGenMuons[0]['idx']]
        Lxy = closestGenMuon.Lxy()
    return Lxy


#### RUN ANALYSIS ####
if __name__ == '__main__':
    ARGS = Analyzer.PARSER.parse_args()
    Analyzer.setSample(ARGS)
    for METHOD in ('declareHistograms', 'analyze'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])
    
    analyzer = Analyzer.Analyzer(
            ARGS = ARGS,
            BRANCHKEYS = ('GEN', 'DSAMUON', 'RSAMUON', 'TRIGGER'),
    )
    analyzer.writeHistograms('roots/SignalTriggerEffTurnOnPlots_{}.root')
