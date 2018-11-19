import os
import math
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
from DisplacedDimuons.Analysis.AnalysisTools import findDimuon, matchedMuons

# CONFIG stores the axis and function information so that histograms can be filled and declared in a loop
CONFIG = {
    # 'pT'      : {'AXES':( 1000, 0., 500.   ), 'LAMBDA': lambda dimuon: dimuon.pt      , 'PRETTY':'p_{T} [GeV]'    },
    # 'eta'     : {'AXES':( 1000, -3., 3.     ), 'LAMBDA': lambda dimuon: dimuon.eta     , 'PRETTY':None             },
    # 'Lxy'     : {'AXES':( 1000, 0., 800.   ), 'LAMBDA': lambda dimuon: dimuon.Lxy()   , 'PRETTY':'L_{xy} [cm]'    },
    # 'LxySig'  : {'AXES':( 1000, 0., 20.    ), 'LAMBDA': lambda dimuon: dimuon.LxySig(), 'PRETTY':None             },
    # 'vtxChi2' : {'AXES':( 1000, 0., 5.     ), 'LAMBDA': lambda dimuon: dimuon.normChi2, 'PRETTY':None             },
    'deltaR'  : {'AXES':( 1000, 0., 5.     ), 'LAMBDA': lambda (m1,m2): m1.p4.DeltaR(m2.p4), 'PRETTY':'#DeltaR(#mu#mu)'},
    'mass'    : {'AXES':( 1000, 0., 500.   ), 'LAMBDA': lambda (m1,m2): (m1.p4+m2.p4).M(), 'PRETTY':'M(#mu#mu) [GeV]'},
    # 'deltaPhi': {'AXES':( 1000, 0., math.pi), 'LAMBDA': lambda dimuon: dimuon.deltaPhi, 'PRETTY':None             },
    # 'cosAlpha': {'AXES':( 1000, -1., 1.     ), 'LAMBDA': lambda dimuon: dimuon.cosAlpha, 'PRETTY':None             },
    'cosAlpha': {'AXES':( 1000, -1., 1.     ), 'LAMBDA': lambda (m1,m2): m1.p4.Vect().Dot(m2.p4.Vect())/m1.p4.P()/m2.p4.P(), 'PRETTY':None             },
}

#### CLASS AND FUNCTION DEFINITIONS ####
# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    for MUONTYPE in ('DSA',):  # 'RSA'):
        for KEY in CONFIG:

            # the pretty strings are mostly in the cut dictionary
            # so use it if it's None
            # but use the string given if not
            XTIT = Selections.PrettyTitles[KEY] if CONFIG[KEY]['PRETTY'] is None else CONFIG[KEY]['PRETTY']

            self.HistInit(MUONTYPE+'Dim_Den_'+KEY, ';'+XTIT+';Counts', *CONFIG[KEY]['AXES'])
            self.HistInit(MUONTYPE+'Dim_Num_'+KEY, ';'+XTIT+';Counts', *CONFIG[KEY]['AXES'])

# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    DSAmuons = E.getPrimitives('DSAMUON')
    # RSAmuons = E.getPrimitives('RSAMUON')
    Dimuons  = E.getPrimitives('DIMUON' )
    HLTPaths, HLTMuons, L1TMuons = E.getPrimitives('TRIGGER')

    if '4Mu' in self.NAME:
        mu11, mu12, mu21, mu22, X1, X2, H, P, extramu = E.getPrimitives('GEN')
        genMuons = (mu11, mu12, mu21, mu22)
        genMuonPairs = ((mu11, mu12), (mu21, mu22))
    elif '2Mu2J' in self.NAME:
        mu1, mu2, j1, j2, X, XP, H, P, extramu = E.getPrimitives('GEN')
        genMuons = (mu1, mu2)
        genMuonPairs = ((mu1, mu2),)
    else:
        raise RuntimeError('Error accessing GEN information. Is this a signal sample?')


    for MUONTYPE, RECOMUONS in (('DSA', DSAmuons),):  # ('RSA', RSAmuons)):
        for genMuonPair in genMuonPairs:
            PTMIN = 30
            if Selections.CUTS['pT'].expr(genMuonPair[0]) < PTMIN or \
                    Selections.CUTS['pT'].expr(genMuonPair[1]) < PTMIN:
                continue

            ETAMAX = 2.0
            if abs(Selections.CUTS['eta'].expr(genMuonPair[0])) > ETAMAX or \
                    abs(Selections.CUTS['eta'].expr(genMuonPair[1])) > ETAMAX:
                continue

            MASSMIN = 15
            if CONFIG['mass']['LAMBDA'](genMuonPair) < MASSMIN:
                continue

            COSALPHAMIN = -0.8
            if CONFIG['cosAlpha']['LAMBDA'](genMuonPair) < COSALPHAMIN:
                continue

            for KEY in CONFIG:
                self.HISTS[MUONTYPE+'Dim_Den_'+KEY].Fill(CONFIG[KEY]['LAMBDA'](genMuonPair))

            if len(HLTMuons) >= 2:
                for KEY in CONFIG:
                    self.HISTS[MUONTYPE+'Dim_Num_'+KEY].Fill(CONFIG[KEY]['LAMBDA'](genMuonPair))


#### RUN ANALYSIS ####
if __name__ == '__main__':
    ARGS = Analyzer.PARSER.parse_args()
    Analyzer.setSample(ARGS)
    for METHOD in ('declareHistograms', 'analyze'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])

    analyzer = Analyzer.Analyzer(
        ARGS        = ARGS,
        BRANCHKEYS  = ('GEN', 'DSAMUON', 'RSAMUON', 'DIMUON', 'TRIGGER'),
        # MAX_EVENTS  = 500
    )
    analyzer.writeHistograms('roots/TriggerDimuonPlots_pTGT30_etaLT2.0_massGT15_cosAlphaGT-0.8_simple_{}.root')
