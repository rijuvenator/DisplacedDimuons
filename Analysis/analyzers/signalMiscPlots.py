import math
import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedMuons, pTRes

#### CLASS AND FUNCTION DEFINITIONS ####
# declare histograms for Analyzer class
def declareHistograms(self):
    # DSA and RSA specific plots
    # CONFIG stores the title and axis tuple so that the histograms can be declared in a loop
    CONFIG = {
            'd0Dif'      : {'TITLE':';*** d_{0} #minus gen d_{0};Counts'            , 'AXES':(1000, -10., 10. )},
            'nMuon'      : {'TITLE':';*** Muon Multiplicity;Counts'                 , 'AXES':(11  ,   0., 11. )},
    }
    for MUON in ('DSA', 'RSA'):
        for KEY in CONFIG:
            self.HistInit(MUON+'_'+KEY, CONFIG[KEY]['TITLE'].replace('***',MUON), *CONFIG[KEY]['AXES'])

# internal loop function for Analyzer class
def analyze(self, E):
    if self.SP is None:
        raise Exception('[ANALYZER ERROR]: This script runs on signal only.')
    if '4Mu' in self.NAME:
        mu11, mu12, mu21, mu22, X1, X2, H, P = E.getPrimitives('GEN', 'HTo2XTo4Mu')
        genMuons = (mu11, mu12, mu21, mu22)
    elif '2Mu2J' in self.NAME:
        mu1, mu2, j1, j2, X, XP, H, P = E.getPrimitives('GEN', 'HTo2XTo2Mu2J')
        genMuons = (mu1, mu2)
    DSAmuons = E.getPrimitives('DSAMUON')
    RSAmuons = E.getPrimitives('RSAMUON')

    DSASelections = [Selections.MuonSelection(muon) for muon in DSAmuons]
    RSASelections = [Selections.MuonSelection(muon) for muon in RSAmuons]

    selectedDSAmuons = [mu  for idx,mu  in enumerate(DSAmuons) if DSASelections   [idx]]
    selectedRSAmuons = [mu  for idx,mu  in enumerate(RSAmuons) if RSASelections   [idx]]

    self.HISTS['DSA_nMuon'].Fill(len(selectedDSAmuons))
    self.HISTS['RSA_nMuon'].Fill(len(selectedRSAmuons))

    # loop over genMuons and fill histograms based on matches
    for genMuon in genMuons:
        # cut genMuons outside the detector acceptance
        genMuonSelection = Selections.AcceptanceSelection(genMuon)
        if not genMuonSelection: continue

        genMuonLxy = genMuon.Lxy()
        foundDSA = False
        for MUON, recoMuons in (('DSA', selectedDSAmuons), ('RSA', selectedRSAmuons)):
            matches = matchedMuons(genMuon, recoMuons)
            if len(matches) != 0:
                closestRecoMuon = recoMuons[matches[0]['idx']]
                if pTRes(closestRecoMuon, genMuon) < -0.5:
                    pass
                    #print 'GEN: {:9.4f} {:7.4f} {:7.4f}'.format(genMuon.pt, genMuon.eta, genMuon.phi)
                    #print '{}: {:9.4f} {:7.4f} {:7.4f}'.format(MUON, closestRecoMuon.pt, closestRecoMuon.eta, closestRecoMuon.phi)
                    #print ''
                self.HISTS[MUON+'_d0Dif'     ].Fill((closestRecoMuon.d0() - genMuon.d0))

#### RUN ANALYSIS ####
if __name__ == '__main__':
    ARGS = Analyzer.PARSER.parse_args()
    Analyzer.setFNAME(ARGS)
    for METHOD in ('declareHistograms', 'analyze'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])
    analyzer = Analyzer.Analyzer(
        NAME        = ARGS.NAME,
        SIGNALPOINT = Utilities.SignalPoint(ARGS.SIGNALPOINT),
        BRANCHKEYS  = ('GEN', 'DSAMUON', 'RSAMUON'),
        TEST        = ARGS.TEST,
        SPLITTING   = ARGS.SPLITTING,
        FILE        = ARGS.FNAME
    )
    analyzer.writeHistograms('roots/SignalMiscPlots_{}.root')
