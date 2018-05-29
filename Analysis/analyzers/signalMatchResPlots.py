import math
import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedMuons, pTRes

def LXY(idx, dimuons):
    dmList = [dm for dm in dimuons if dm.idx1 == idx or dm.idx2 == idx]
    dmList.sort(key=lambda dm: dm.normChi2)
    return dmList[0].Lxy()

# CONFIG stores the title and axis tuple so that the histograms can be declared in a loop
HEADERS = ('XTITLE', 'AXES', 'LAMBDA', 'PRETTY')
VALUES  = (
    ('pT' , 'p_{T} [GeV]', (1000,       0.,    500.), lambda muon: muon.pt       , 'p_{T}'  ),
    ('eta', '#eta'       , (1000,      -3.,      3.), lambda muon: muon.eta      , '#eta'   ),
    ('phi', '#phi'       , (1000, -math.pi, math.pi), lambda muon: muon.phi      , '#phi'   ),
    ('Lxy', 'L_{xy} [cm]', (1000,       0.,    500.), lambda muon: muon.Lxy()    , 'L_{xy}' ),
    ('dR' , '#DeltaR'    , (1000,       0.,      5.), lambda gm  : gm.pairDeltaR , '#DeltaR'),
)
CONFIG = {}
for VAL in VALUES:
    KEY, VALS = VAL[0], VAL[1:]
    CONFIG[KEY] = dict(zip(HEADERS, VALS))

#### CLASS AND FUNCTION DEFINITIONS ####
# declare histograms for Analyzer class
def declareHistograms(self):
    def HTitle(KEY, MUON, MODE, KEY2=None):
        if MODE == 'Res':
            # X = <q> Resolution
            fstring = ';{M} {P} #minus gen {P} / gen {P};Counts'
        elif MODE == 'VS':
            # X = gen <q> ; Y = reco <q>
            fstring = ';gen {X};{M} {X};Counts'
        elif MODE== 'VSRes':
            # X = gen <q2> ; Y = <q> Resolution
            fstring = ';gen {X2};{M} {P} #minus gen {P} / gen {P};Counts'
        return fstring.format(
            X =CONFIG[KEY]['XTITLE'],
            M =MUON,
            P =CONFIG[KEY]['PRETTY'],
            X2=None if KEY2 is None else CONFIG[KEY2]['XTITLE']
        )
    for KEY in CONFIG:
        for MUON in ('DSA', 'RSA'):
            if KEY != 'dR':
                #if KEY == 'Lxy' and MUON == 'RSA': continue # can't compute Lxy for RSA muons
                for x in (0,):
                    self.HistInit(MUON+'_'+KEY+'Res'          , HTitle(KEY, MUON, 'Res'        ), *(1000, -1., 3.)                          )
                    self.HistInit(MUON+'_'+KEY+'VS'+KEY       , HTitle(KEY, MUON, 'VS'         ), *(CONFIG[KEY]['AXES']+CONFIG[KEY]['AXES']))
                for KEY2 in CONFIG:
                    self.HistInit(MUON+'_'+KEY+'Res'+'VS'+KEY2, HTitle(KEY, MUON, 'VSRes', KEY2), *(CONFIG[KEY2]['AXES']+(1000, -1., 3.)   ))

# internal loop function for Analyzer class
def analyze(self, E):
    if self.SP is None:
        raise Exception('[ANALYZER ERROR]: This script runs on signal only.')
    if '4Mu' not in self.NAME:
        raise Exception('[ANALYZER ERROR]: This script runs on HTo2XTo4Mu only, for now')
    mu11, mu12, mu21, mu22, X1, X2, H, P = E.getPrimitives('GEN', 'HTo2XTo4Mu')
    DSAmuons = E.getPrimitives('DSAMUON')
    RSAmuons = E.getPrimitives('RSAMUON')
    Dimuons  = E.getPrimitives('DIMUON' )

    DSASelections = [Selections.MuonSelection(muon) for muon in DSAmuons]
    RSASelections = [Selections.MuonSelection(muon) for muon in RSAmuons]

    # loop over genMuons and fill histograms based on matches
    for genMuon in (mu11, mu12, mu21, mu22):
        # cut genMuons outside the detector acceptance
        genMuonSelection = Selections.AcceptanceSelection(genMuon)
        if not genMuonSelection: continue

        # find closest matched reco muon for DSA and RSA
        genMuonLxy = genMuon.Lxy()
        foundDSA = False
        for MUON, recoMuons in (('DSA', DSAmuons), ('RSA', RSAmuons)):
            matches = matchedMuons(genMuon, recoMuons)
            if len(matches) != 0:
                # take the closest match
                closestRecoMuon = recoMuons[matches[0]['idx']]
                for KEY in CONFIG:
                    F = CONFIG[KEY]['LAMBDA']
                    if KEY not in ('dR', 'Lxy'):
                        for x in (0,):
                            self.HISTS[MUON+'_'+KEY+'Res'          ].Fill((F(closestRecoMuon)-F(genMuon))/F(genMuon))
                            self.HISTS[MUON+'_'+KEY+'VS'+KEY       ].Fill(F(genMuon), F(closestRecoMuon))
                        for KEY2 in CONFIG:
                            F2 = CONFIG[KEY2]['LAMBDA']
                            self.HISTS[MUON+'_'+KEY+'Res'+'VS'+KEY2].Fill(F2(genMuon), (F(closestRecoMuon)-F(genMuon))/F(genMuon))
                    # reco Lxy needs to be handled specially
                    #elif KEY == 'Lxy':
                    #    if MUON == 'RSA': continue
                    #    if len(Dimuons) == 0:
                    #        recoLxy = closestRecoMuon.pos.Perp()
                    #    else:
                    #        try:
                    #            recoLxy = LXY(matches[0]['idx'], Dimuons)
                    #        except:
                    #            recoLxy = 0.
                    #    for x in (0,):
                    #        self.HISTS[MUON+'_'+KEY+'Res'          ].Fill((recoLxy-F(genMuon))/F(genMuon))
                    #        self.HISTS[MUON+'_'+KEY+'VS'+KEY       ].Fill(F(genMuon), recoLxy)
                    #    for KEY2 in CONFIG:
                    #        F2 = CONFIG[KEY2]['LAMBDA']
                    #        self.HISTS[MUON+'_'+KEY+'Res'+'VS'+KEY2].Fill(F2(genMuon), (recoLxy-F(genMuon))/F(genMuon))

#### RUN ANALYSIS ####
if __name__ == '__main__':
    ARGS = Analyzer.PARSER.parse_args()
    Analyzer.setFNAME(ARGS)
    for METHOD in ('declareHistograms', 'analyze'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])
    analyzer = Analyzer.Analyzer(
        NAME        = ARGS.NAME,
        SIGNALPOINT = Utilities.SignalPoint(ARGS.SIGNALPOINT),
        BRANCHKEYS  = ('GEN', 'DSAMUON', 'RSAMUON', 'DIMUON'),
        TEST        = ARGS.TEST,
        SPLITTING   = ARGS.SPLITTING,
        FILE        = ARGS.FNAME
    )
    analyzer.writeHistograms('roots/SignalMatchResPlots_{}.root')
