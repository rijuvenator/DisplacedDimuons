import math
import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities

# set up a configuration dictionary with the same cut keys as in Selections
CUTKEYS = {
    'pT'       : {'AXES':(100,  0.,500.)},
    'eta'      : {'AXES':(100, -3.,  3.)},
    'normChi2' : {'AXES':(100,  0.,  5.)},
    'nMuonHits': {'AXES':(50 ,  0., 50.)},
    'nStations': {'AXES':(10 ,  0., 10.)},
    'd0Sig'    : {'AXES':(100,  0.,  5.)},

    'vtxChi2'  : {'AXES':(100,  0.,  5.)},
    'deltaR'   : {'AXES':(100,  0.,  5.)},
    'mass'     : {'AXES':(100,  0., 50.)},
    'cosAlpha' : {'AXES':(100, -1.,  1.)},
    'LxySig'   : {'AXES':(100,  0., 12.)},
}
for KEY in CUTKEYS:
    # the title is ;XTITLE;Counts
    CUTKEYS[KEY]['TITLE'] = ';' + Selections.PrettyTitles[KEY] + ';Counts'
MUONCUTKEYS   = [KEY for KEY in CUTKEYS if KEY in Selections.CutLists['MuonCutList'  ]]
DIMUONCUTKEYS = [KEY for KEY in CUTKEYS if KEY in Selections.CutLists['DimuonCutList']]

# function for writing KEY_Less or KEY_More
def NAME(KEY, DeltaPhiRegion):
    return KEY + '_' +  DeltaPhiRegion

# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    for KEY in CUTKEYS:
        for DeltaPhiRegion in ('Less', 'More'):
            self.HistInit(NAME(KEY, DeltaPhiRegion), CUTKEYS[KEY]['TITLE'], *CUTKEYS[KEY]['AXES'])

# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    DSAmuons = E.getPrimitives('DSAMUON')
    Dimuons  = E.getPrimitives('DIMUON')

    DSASelections = [Selections.MuonSelection(muon) for muon in DSAmuons]
    DimuonSelections = [Selections.DimuonSelection(dimuon) for dimuon in Dimuons]

    for dimSel, dimuon in zip(DimuonSelections, Dimuons):
        DeltaPhiRegion = 'Less' if dimSel['deltaPhi'] else 'More'
        mu1, mu2 = DSAmuons[dimuon.idx1], DSAmuons[dimuon.idx2]
        mu1Sel, mu2Sel = DSASelections[dimuon.idx1], DSASelections[dimuon.idx2]

        for KEY in DIMUONCUTKEYS:
            # require muons   to pass their full selection
            # require dimuons to pass their full selection except KEY
            # (and deltaPhi of course)
            if all((
                    dimSel.allExcept('deltaPhi', KEY),
                    mu1Sel,
                    mu2Sel
                )):
                # reminder: expr is the lambda performed on object to get the value on which the cut is applied
                # e.g. Selections.CUTS['nStations'].expr(mu) == mu.nDTStations + mu.nCSCStations
                thisCut = Selections.CUTS[KEY]
                fillValue = thisCut.expr(dimuon)
                self.HISTS[NAME(KEY, DeltaPhiRegion)].Fill(fillValue)

        for KEY in MUONCUTKEYS:
            # require dimuons to pass their full selection
            # require muons   to pass their full selection except KEY
            # (and deltaPhi of course)
            if all((
                    dimSel.allExcept('deltaPhi'),
                    mu1Sel.allExcept(KEY),
                    mu2Sel.allExcept(KEY)
                )):
                # reminder: expr is the lambda performed on object to get the value on which the cut is applied
                # e.g. Selections.CUTS['nStations'].expr(mu) == mu.nDTStations + mu.nCSCStations
                # mfunc is max if cut is < or <=; mfunc is min if cut is > or >=
                thisCut = Selections.CUTS[KEY]
                fillValue = thisCut.mfunc(thisCut.expr(mu1), thisCut.expr(mu2))
                self.HISTS[NAME(KEY, DeltaPhiRegion)].Fill(fillValue)

#### RUN ANALYSIS ####
if __name__ == '__main__':
    ARGS = Analyzer.PARSER.parse_args()
    Analyzer.setSample(ARGS)
    for METHOD in ('declareHistograms', 'analyze'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])
    analyzer = Analyzer.Analyzer(
        ARGS        = ARGS,
        BRANCHKEYS  = ('DSAMUON', 'DIMUON'),
    )
    analyzer.writeHistograms('roots/nMinusOnePlots_{}.root')
