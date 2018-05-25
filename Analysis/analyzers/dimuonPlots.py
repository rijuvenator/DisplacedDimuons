import math
import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedMuons, pTRes

#### CLASS AND FUNCTION DEFINITIONS ####
# declare histograms for Analyzer class
def declareHistograms(self):
    # dimuon plots
    try:
        MassUpper = self.SP.mX*2
    except:
        MassUpper = 20.

    self.HistInit('Dim_vtxChi2' , ';vtx #chi^{2}/dof;Counts'                   , 1000,   0., 5.           )
    self.HistInit('Dim_deltaR'  , ';#DeltaR;Counts'                            , 1000,   0., 5.           )
    self.HistInit('Dim_mass'    , ';M(#mu#mu);Counts'                          , 1000,   0., MassUpper    )
    self.HistInit('Dim_deltaPhi', ';|#Delta#Phi|;Counts'                       , 1000,   0., math.pi      )
    self.HistInit('Dim_cosAlpha', ';cos(#alpha);Counts'                        , 1000,  -1., 1.           )

# internal loop function for Analyzer class
def analyze(self, E):
    DSAmuons = E.getPrimitives('DSAMUON')
    RSAmuons = E.getPrimitives('RSAMUON')
    Dimuons  = E.getPrimitives('DIMUON' )

    DSASelections = [Selections.MuonSelection(muon) for muon in DSAmuons]
    RSASelections = [Selections.MuonSelection(muon) for muon in RSAmuons]

    for dimuon in Dimuons:
        if DSASelections[dimuon.idx1] and DSASelections[dimuon.idx2] and Selections.DimuonSelection(dimuon):
            self.HISTS['Dim_vtxChi2' ].Fill(dimuon.normChi2)
            self.HISTS['Dim_deltaR'  ].Fill(dimuon.deltaR  )
            self.HISTS['Dim_mass'    ].Fill(dimuon.mass    )
            self.HISTS['Dim_deltaPhi'].Fill(dimuon.deltaPhi)
            self.HISTS['Dim_cosAlpha'].Fill(dimuon.cosAlpha)
            #dimuonSelection = Selections.DimuonSelection(dimuon)

#### RUN ANALYSIS ####
if __name__ == '__main__':
    ARGS = Analyzer.PARSER.parse_args()
    Analyzer.setFNAME(ARGS)
    for METHOD in ('declareHistograms', 'analyze'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])
    analyzer = Analyzer.Analyzer(
        NAME        = ARGS.NAME,
        SIGNALPOINT = Utilities.SignalPoint(ARGS.SIGNALPOINT),
        BRANCHKEYS  = ('DSAMUON', 'RSAMUON', 'DIMUON'),
        TEST        = ARGS.TEST,
        SPLITTING   = ARGS.SPLITTING,
        FILE        = ARGS.FNAME
    )
    analyzer.writeHistograms('roots/DimuonPlots_{}.root')
