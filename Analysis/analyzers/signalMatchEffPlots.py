import math
import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedMuons

# CONFIG stores the title and axis tuple so that the histograms can be declared in a loop
CONFIG = {
        'pT'  : {'XTITLE':'p_{T} [GeV]', 'AXES':(1000,       0.,    500.), 'LAMBDA':lambda muon: muon.pt   },
        'eta' : {'XTITLE':'#eta'       , 'AXES':(1000,      -3.,      3.), 'LAMBDA':lambda muon: muon.eta  },
        'phi' : {'XTITLE':'#phi'       , 'AXES':(1000, -math.pi, math.pi), 'LAMBDA':lambda muon: muon.phi  },
        'Lxy' : {'XTITLE':'L_{xy} [cm]', 'AXES':(1000,       0.,    500.), 'LAMBDA':lambda muon: muon.Lxy()},
}

#### CLASS AND FUNCTION DEFINITIONS ####
# declare histograms for Analyzer class
def declareHistograms(self):
    for KEY in CONFIG:
        # one Eff, ChargeEff, and ChargeDen plot for each of DSA and RSA
        for MUON in ('DSA', 'RSA'):
            TITLE = ';'+CONFIG[KEY]['XTITLE']+';'+MUON+' Match Efficiency'
            self.HistInit(MUON+'_'+KEY+'Eff'      , TITLE, *CONFIG[KEY]['AXES'])
            TITLE = TITLE.replace('Match', 'Charge Match')
            self.HistInit(MUON+'_'+KEY+'ChargeEff', TITLE, *CONFIG[KEY]['AXES'])
            self.HistInit(MUON+'_'+KEY+'ChargeDen', ''   , *CONFIG[KEY]['AXES'])

        # "extra" and gen denominator plots, can reuse the axes
        self.HistInit(KEY+'Den'        , '', *CONFIG[KEY]['AXES'])
        self.HistInit(KEY+'Extra'      , '', *CONFIG[KEY]['AXES'])

# internal loop function for Analyzer class
def analyze(self, E):
    mu11, mu12, mu21, mu22, X1, X2, H, P = E.getPrimitives('GEN')
    DSAmuons = E.getPrimitives('DSAMUON')
    RSAmuons = E.getPrimitives('RSAMUON')

    DSASelections = [Selections.MuonSelection(muon) for muon in DSAmuons]
    RSASelections = [Selections.MuonSelection(muon) for muon in RSAmuons]

    # loop over genMuons and fill histograms based on matches
    for genMuon in (mu11, mu12, mu21, mu22):
        # cut genMuons outside the detector acceptance
        genMuonSelection = Selections.MuonSelection(genMuon, cutList='MuonAcceptanceCutList')
        if not genMuonSelection: continue

        # fill the gen denominator histograms
        for KEY in CONFIG:
            self.HISTS[KEY+'Den'].Fill(CONFIG[KEY]['LAMBDA'](genMuon))

        # find closest matched reco muon for DSA and RSA
        foundDSA = False
        for PREFIX, recoMuons in (('DSA', DSAmuons), ('RSA', RSAmuons)):
            matches = matchedMuons(genMuon, recoMuons)
            if len(matches) != 0:
                # take the closest match
                closestRecoMuon = recoMuons[matches[0]['idx']]
                # fill all the quantities
                # also fill the charge denominator histograms: denominator is +1 for each dR match
                for KEY in CONFIG:
                    self.HISTS[PREFIX+'_'+KEY+'Eff'      ].Fill(CONFIG[KEY]['LAMBDA'](genMuon))
                    self.HISTS[PREFIX+'_'+KEY+'ChargeDen'].Fill(CONFIG[KEY]['LAMBDA'](genMuon))

                    # THEN if the charges are the same, fill. Should be flat and close to 1.
                    if genMuon.charge == closestRecoMuon.charge:
                        self.HISTS[PREFIX+'_'+KEY+'ChargeEff'].Fill(CONFIG[KEY]['LAMBDA'](genMuon))

                if PREFIX == 'DSA':
                    foundDSA = True

                if PREFIX == 'RSA' and not foundDSA:
                    for KEY in CONFIG:
                        self.HISTS[KEY+'Extra'].Fill(CONFIG[KEY]['LAMBDA'](genMuon))

#### RUN ANALYSIS ####
if __name__ == '__main__':
    ARGS = Analyzer.PARSER.parse_args()
    for METHOD in ('declareHistograms', 'analyze'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])
    analyzer = Analyzer.Analyzer(
        NAME        = ARGS.NAME,
        SIGNALPOINT = Utilities.SignalPoint(ARGS.SIGNALPOINT),
        BRANCHKEYS  = ('GEN', 'DSAMUON', 'RSAMUON'),
        TEST        = ARGS.TEST,
        SPLITTING   = ARGS.SPLITTING
    )
    analyzer.writeHistograms('roots/SignalMatchEffPlots_{}.root')
