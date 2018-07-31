import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities

CONFIG = {
        'pT' : {'AXES':(20,  0., 500.), 'PRETTY':'p_{T} [GeV]', 'LAMBDA': lambda mu : mu.pt    },
        'eta': {'AXES':(20, -3.,   3.), 'PRETTY':'#eta'       , 'LAMBDA': lambda mu : mu.eta   },
        'd0' : {'AXES':(20,  0., 200.), 'PRETTY':'d_{0} [cm]' , 'LAMBDA': lambda mu : mu.d0()  },
        'Lxy': {'AXES':(20,  0., 800.), 'PRETTY':'L_{xy} [cm]', 'LAMBDA': lambda dim: dim.Lxy()},
}

#### CLASS AND FUNCTION DEFINITIONS ####
# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    def TITLE(CUT, QUANTITY):
        return ';' + CONFIG[QUANTITY]['PRETTY'] + ';' + Selections.PrettyTitles[CUT] + ' Cut N#minus1 Efficiency'

    for CUT in Selections.CutLists['MuonCutList'] + Selections.CutLists['DimuonCutList']:
        for QUANTITY in CONFIG:
            self.HistInit(CUT+'EffVS'+QUANTITY, TITLE(CUT, QUANTITY), *CONFIG[QUANTITY]['AXES'])
            self.HistInit(CUT+'DenVS'+QUANTITY, ''                  , *CONFIG[QUANTITY]['AXES'])

# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    if self.SP is not None and not Selections.passedTrigger(E): return
    Event    = E.getPrimitives('EVENT')
    DSAmuons = E.getPrimitives('DSAMUON')
    Dimuons  = E.getPrimitives('DIMUON' )

    eventWeight = 1.
    try:
        eventWeight = 1. if Event.weight > 0. else -1.
    except:
        pass

    # whether to BLIND. Could depend on Analyzer parameters, which is why it's here.
    BLIND = True if self.SP is None else False

    DSASelections = [Selections.MuonSelection(muon) for muon in DSAmuons]

    # loop over DSAmuons and select
    for muon, muonSelection in zip(DSAmuons,DSASelections):
        # data blinding!
        if BLIND:
            if muon.d0Sig() > 3.: continue

        for CUT in Selections.CutLists['MuonCutList']:
            for Q in ('pT', 'eta', 'd0'):
                F = CONFIG[Q]['LAMBDA']
                if muonSelection.allExcept(CUT):
                    self.HISTS[CUT+'DenVS'+Q].Fill(F(muon), eventWeight)
                if muonSelection:
                    self.HISTS[CUT+'EffVS'+Q].Fill(F(muon), eventWeight)

    # loop over dimuons and select
    for dimuon in Dimuons:
        # data blinding!
        if BLIND:
            if dimuon.LxySig() > 3. or dimuon.mu1.d0Sig() > 3. or dimuon.mu2.d0Sig() > 3.:
                continue
        muon1Selection = DSASelections[dimuon.idx1]
        muon2Selection = DSASelections[dimuon.idx2]
        if muon1Selection and muon2Selection:

            dimuonSelection = Selections.DimuonSelection(dimuon)

            for CUT in Selections.CutLists['DimuonCutList']:
                for Q in ('Lxy',):
                    F = CONFIG[Q]['LAMBDA']
                    if dimuonSelection.allExcept(CUT):
                        self.HISTS[CUT+'DenVS'+Q].Fill(F(dimuon), eventWeight)
                    if dimuonSelection:
                        self.HISTS[CUT+'EffVS'+Q].Fill(F(dimuon), eventWeight)

#### RUN ANALYSIS ####
if __name__ == '__main__':
    ARGS = Analyzer.PARSER.parse_args()
    Analyzer.setSample(ARGS)
    for METHOD in ('declareHistograms', 'analyze'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])
    analyzer = Analyzer.Analyzer(
        ARGS        = ARGS,
        BRANCHKEYS  = ('EVENT', 'DIMUON', 'DSAMUON', 'TRIGGER'),
    )
    analyzer.writeHistograms('roots/nMinusOneEffPlots_{}.root')
