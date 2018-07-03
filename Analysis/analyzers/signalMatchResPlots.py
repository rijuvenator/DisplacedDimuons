import math
import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedMuons, matchedDimuons

# CONFIG stores the title and axis tuple so that the histograms can be declared in a loop
HEADERS = ('XTITLE', 'AXES', 'RESAXES', 'LAMBDA', 'PRETTY', 'RESFUNC', 'DIF')
VALUES  = (
    ('pT' , 'p_{T} [GeV]' , (1000, 0., 500.), (1000, -1. , 1. ), lambda muon: muon.pt              , 'p_{T}' , lambda rq, gq: (rq-gq)/gq, False),
    ('Lxy', 'L_{xy} [cm]' , (1000, 0., 800.), (1000, -50., 50.), lambda dim : dim.Lxy()            , 'L_{xy}', lambda rq, gq: (rq-gq)   , True ),
    ('d0' , 'd_{0} [cm]'  , (1000, 0., 200.), (1000, -50., 50.), lambda muon: muon.d0()            , 'd_{0}' , lambda rq, gq: (rq-gq)   , True ),
    ('qm' , 'charge match', (2   , 0.,   2.), None             , lambda r, g: r.charge == g.charge , None    , None                     , None ),
)
CONFIG = {}
for VAL in VALUES:
    KEY, VALS = VAL[0], VAL[1:]
    CONFIG[KEY] = dict(zip(HEADERS, VALS))

#### CLASS AND FUNCTION DEFINITIONS ####
# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    def HTitle(KEY, MUON, MODE, KEY2=None):
        DenString = '' if CONFIG[KEY]['DIF'] else ' / gen {P}'
        if MODE == 'Res':
            # X = <q> Resolution/Dif
            fstring = ';{M} {P} #minus gen {P}'+DenString+';Counts'
        elif MODE == 'VS':
            # X = gen <q> ; Y = reco <q>
            fstring = ';gen {X};{M} {X};Counts'
        elif MODE== 'VSRes':
            # X = gen <q2> ; Y = <q> Resolution/Dif
            fstring = ';gen {X2};{M} {P} #minus gen {P}'+DenString+';Counts'
        return fstring.format(
            X =CONFIG[KEY]['XTITLE'],
            M =MUON,
            P =CONFIG[KEY]['PRETTY'],
            X2=None if KEY2 is None else CONFIG[KEY2]['XTITLE']
        )
    for KEY in CONFIG:
        if KEY == 'qm': continue
        for MUON in ('DSA', 'RSA'):
            if KEY == 'Lxy' and MUON == 'RSA': continue # can't compute Lxy for RSA muons
            for x in (0,):
                self.HistInit(MUON+'_'+KEY+'Res'          , HTitle(KEY, MUON, 'Res'        ), *CONFIG[KEY]['RESAXES']                       )
                self.HistInit(MUON+'_'+KEY+'VS'+KEY       , HTitle(KEY, MUON, 'VS'         ), *(CONFIG[KEY]['AXES']+CONFIG[KEY]['AXES']    ))
            for KEY2 in CONFIG:
                if KEY == 'Lxy' and KEY2 == 'qm': continue
                self.HistInit(MUON+'_'+KEY+'Res'+'VS'+KEY2, HTitle(KEY, MUON, 'VSRes', KEY2), *(CONFIG[KEY2]['AXES']+CONFIG[KEY]['RESAXES']))

# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    if self.SP is None:
        raise Exception('[ANALYZER ERROR]: This script runs on signal only.')
    if '4Mu' in self.NAME:
        mu11, mu12, mu21, mu22, X1, X2, H, P, extramu = E.getPrimitives('GEN', 'HTo2XTo4Mu')
        genMuons = (mu11, mu12, mu21, mu22)
        genMuonPairs = ((mu11, mu12), (mu21, mu22))
    elif '2Mu2J' in self.NAME:
        mu1, mu2, j1, j2, X, XP, H, P, extramu = E.getPrimitives('GEN', 'HTo2XTo2Mu2J')
        genMuons = (mu1, mu2)
        genMuonPairs = ((mu1, mu2),)
    DSAmuons = E.getPrimitives('DSAMUON')
    RSAmuons = E.getPrimitives('RSAMUON')
    Dimuons  = E.getPrimitives('DIMUON' )

    SelectDimuons = False
    SelectMuons   = False
    # require dimuons and muons to pass all selections
    if SelectDimuons and SelectMuons:
        DSASelections    = [Selections.MuonSelection  (muon)   for muon   in DSAmuons]
        RSASelections    = [Selections.MuonSelection  (muon)   for muon   in RSAmuons]
        DimuonSelections = [Selections.DimuonSelection(dimuon) for dimuon in Dimuons ]

        selectedDSAmuons = [mu  for idx,mu  in enumerate(DSAmuons) if DSASelections   [idx]]
        selectedRSAmuons = [mu  for idx,mu  in enumerate(RSAmuons) if RSASelections   [idx]]
        selectedDimuons  = [dim for idx,dim in enumerate(Dimuons ) if DimuonSelections[idx] and DSASelections[dim.idx1] and DSASelections[dim.idx2]]

    # don't require dimuons and muons to pass all selections
    else:
        selectedDSAmuons = DSAmuons
        selectedRSAmuons = RSAmuons
        selectedDimuons  = Dimuons

    # loop over genMuons and fill histograms based on matches
    for genMuon in genMuons:
        # cut genMuons outside the detector acceptance
        # no selection for now
        #genMuonSelection = Selections.AcceptanceSelection(genMuon)
        #if not genMuonSelection: continue

        # find closest matched reco muon for DSA and RSA
        foundDSA = False
        for MUON, recoMuons in (('DSA', selectedDSAmuons), ('RSA', selectedRSAmuons)):
            matches = matchedMuons(genMuon, recoMuons)
            if len(matches) != 0:
                # take the closest match
                closestRecoMuon = recoMuons[matches[0]['idx']]
                for KEY in ('pT', 'd0'):
                    F = CONFIG[KEY]['LAMBDA']
                    RF = CONFIG[KEY]['RESFUNC']
                    for x in (0,):
                        self.HISTS[MUON+'_'+KEY+'Res'          ].Fill(RF(F(closestRecoMuon), F(genMuon)))
                        self.HISTS[MUON+'_'+KEY+'VS'+KEY       ].Fill(F(genMuon), F(closestRecoMuon))
                    for KEY2 in CONFIG:
                        F2 = CONFIG[KEY2]['LAMBDA']
                        if KEY2 != 'qm':
                            self.HISTS[MUON+'_'+KEY+'Res'+'VS'+KEY2].Fill(F2(genMuon), RF(F(closestRecoMuon), F(genMuon)))
                        else:
                            self.HISTS[MUON+'_'+KEY+'Res'+'VS'+KEY2].Fill(F2(closestRecoMuon, genMuon), RF(F(closestRecoMuon), F(genMuon)))

    # loop over genMuonPairs and fill histograms based on matches
    for genMuonPair in genMuonPairs:
        # cut genMuons outside the detector acceptance
        # no selection for now
        #genMuonSelection = Selections.AcceptanceSelection(genMuonPair)
        #if not genMuonSelection: continue

        # find closest matched dimuon
        matches = matchedDimuons(genMuonPair, selectedDimuons)
        if len(matches) != 0:
            closestDimuon = selectedDimuons[matches[0]['idx']]
            for KEY in ('Lxy',):
                F = CONFIG[KEY]['LAMBDA']
                RF = CONFIG[KEY]['RESFUNC']
                if KEY in ('Lxy',):
                    for x in (0,):
                        self.HISTS['DSA_'+KEY+'Res'          ].Fill(RF(F(closestDimuon),F(genMuonPair[0])))
                        self.HISTS['DSA_'+KEY+'VS'+KEY       ].Fill(F(genMuonPair[0]), F(closestDimuon))
                    for KEY2 in CONFIG:
                        if KEY2 == 'qm': continue
                        F2 = CONFIG[KEY2]['LAMBDA']
                        self.HISTS['DSA_'+KEY+'Res'+'VS'+KEY2].Fill(F2(genMuonPair[0]), RF(F(closestDimuon),F(genMuonPair[0])))

#### RUN ANALYSIS ####
if __name__ == '__main__':
    ARGS = Analyzer.PARSER.parse_args()
    Analyzer.setSample(ARGS)
    for METHOD in ('declareHistograms', 'analyze'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])
    analyzer = Analyzer.Analyzer(
        ARGS        = ARGS,
        BRANCHKEYS  = ('GEN', 'DSAMUON', 'RSAMUON', 'DIMUON'),
    )
    analyzer.writeHistograms('roots/SignalMatchResPlots_{}.root')
