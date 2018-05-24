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
    mu11, mu12, mu21, mu22, X1, X2, H, P = E.getPrimitives('GEN', 'HTo2XTo4Mu')
    DSAmuons = E.getPrimitives('DSAMUON')
    RSAmuons = E.getPrimitives('RSAMUON')

    DSASelections = [Selections.MuonSelection(muon) for muon in DSAmuons]
    RSASelections = [Selections.MuonSelection(muon) for muon in RSAmuons]

    nDSA, nRSA = 0, 0
    for sel in DSASelections:
        if sel['pt'] and sel['eta']:
            nDSA += 1
    for sel in RSASelections:
        if sel['pt'] and sel['eta']:
            nRSA += 1
    self.HISTS['DSA_nMuon'].Fill(nDSA)
    self.HISTS['RSA_nMuon'].Fill(nRSA)

    # loop over genMuons and fill histograms based on matches
    for genMuon in (mu11, mu12, mu21, mu22):
        # cut genMuons outside the detector acceptance
        genMuonSelection = Selections.AcceptanceSelection(genMuon)
        if not genMuonSelection: continue

        genMuonLxy = genMuon.LXY()
        PREFIX = 'DSA'
        foundDSA = False
        for recoMuons in (DSAmuons, RSAmuons):
            matches = matchedMuons(genMuon, recoMuons)
            if len(matches) != 0:
                closestRecoMuon = recoMuons[matches[0]['idx']]
                if pTRes(closestRecoMuon, genMuon) < -0.5:
                    pass
                    #print 'GEN: {:9.4f} {:7.4f} {:7.4f}'.format(genMuon.pt, genMuon.eta, genMuon.phi)
                    #print '{}: {:9.4f} {:7.4f} {:7.4f}'.format(PREFIX, closestRecoMuon.pt, closestRecoMuon.eta, closestRecoMuon.phi)
                    #print ''
                self.HISTS[PREFIX+'_d0Dif'     ].Fill((closestRecoMuon.d0() - genMuon.d0))
            PREFIX = 'RSA'

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
        SPLITTING   = ARGS.SPLITTING,
        FILE        = Analyzer.F_AOD_NTUPLE
    )
    analyzer.writeHistograms('roots/SignalMiscPlots_{}.root')
