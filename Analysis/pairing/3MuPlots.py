import ROOT as R
import numpy as np
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedMuons, matchedDimuons, matchedDimuonPairs

#### CLASS AND FUNCTION DEFINITIONS ####
# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    self.HistInit('counters', ';Categories;Counts' , 11 , 0., 11. )

    QUANTITIES = (
        ('chi2', (';vtx #chi^{2}/dof;Counts', 200, 0., 5.  )),
        ('Lxy' , (';L_{xy} [cm];Counts'     , 330, 0., 330.)),
    )

    # "correctly identified", "matched signal", "least chi^2", and "un matched"
    for tag in ('CID', 'MSD', 'LCD', 'UMD'):
        for quantity, args in QUANTITIES:
            for criteria in ('LCD', 'LCD-OC', 'HPD', 'HPD-OC'):
                self.HistInit(quantity+'_'+criteria+'_'+tag, *args)

# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    if self.SP is None:
        raise Exception('[ANALYZER ERROR]: This script runs on signal only.')

    if self.TRIGGER:
        if not Selections.passedTrigger(E): return

    if '4Mu' in self.NAME:
        mu11, mu12, mu21, mu22, X1, X2, H, P, extramu = E.getPrimitives('GEN')
        genMuons = (mu11, mu12, mu21, mu22)
        genMuonPairs = ((mu11, mu12), (mu21, mu22))
    elif '2Mu2J' in self.NAME:
        mu1, mu2, j1, j2, X, XP, H, P, extramu = E.getPrimitives('GEN')
        genMuons = (mu1, mu2)
        genMuonPairs = ((mu1, mu2),)
    Event   = E.getPrimitives('EVENT'  )
    dimuons = E.getPrimitives('DIMUON' )
    muons   = E.getPrimitives('DSAMUON')

    # bin constants
    EVENTS     = 0.
    MU4        = 1.
    MU3        = 2.
    MU4TO3_PT5 = 3.
    MU3TO3_PT5 = 4.
    MATCH0     = 5.
    MATCH1     = 6.
    GOODMATCH  = {
            'LCD'   :7.,
            'HPD'   :8.,
            'LCD-OC':9.,
            'HPD-OC':10.,
    }

    self.HISTS['counters'].Fill(EVENTS)

    baseMuons = [mu for mu in muons if mu.nDTStations+mu.nCSCStations>1 and mu.nCSCHits+mu.nDTHits>12 and mu.ptError/mu.pt<1.]
    if len(baseMuons) == 4: self.HISTS['counters'].Fill(MU4)
    if len(baseMuons) == 3: self.HISTS['counters'].Fill(MU3)

    selectedMuons    = [mu for mu in baseMuons if mu.pt>5.]
    selectedOIndices = [mu.idx for mu in selectedMuons]
    selectedDimuons  = [dim for dim in dimuons if dim.idx1 in selectedOIndices and dim.idx2 in selectedOIndices]

    if len(selectedMuons) == 3:
        if len(baseMuons) == 4:
            self.HISTS['counters'].Fill(MU4TO3_PT5)
        else:
            self.HISTS['counters'].Fill(MU3TO3_PT5)

        indices  = [mu.idx for mu in selectedMuons]
        HPDs     = [dim for dim in selectedDimuons if dim.idx1 in indices and dim.idx2 in indices]
        HPDIDs   = {dim.ID:dim for dim in HPDs}
        HPDOCs   = [dim for dim in HPDs if dim.isOC(muons)]
        HPDOCIDs = {dim.ID:dim for dim in HPDOCs}

        if len(HPDs) > 0:
            bestDimuon = {}

            # find LCD
            sortedDimuons = sorted(HPDs, key=lambda dim: dim.normChi2)
            bestDimuon['LCD'] = sortedDimuons[0]

            # find HPD
            sortedMuons = sorted(selectedMuons, key=lambda mu:mu.pt, reverse=True)
            highestMuIDs = (sortedMuons[0].idx, sortedMuons[1].idx)
            bestDimuon['HPD'] = None
            for dim in HPDs:
                if dim.idx1 in highestMuIDs and dim.idx2 in highestMuIDs:
                    bestDimuon['HPD'] = dim
                    break

            if len(HPDOCs) > 0:
                # find LCD-OC and HPD-OC
                sortedOCDimuons = sorted(HPDOCs, key=lambda dim: dim.normChi2)
                bestDimuon['LCD-OC'] = sortedOCDimuons[0]
                bestDimuon['HPD-OC'] = None
                for dim in HPDOCs:
                    if dim.idx1 in highestMuIDs and dim.idx2 in highestMuIDs:
                        bestDimuon['HPD-OC'] = dim
                        break
            else:
                sortedOCDimuons = []
                bestDimuon['LCD-OC'] = None
                bestDimuon['HPD-OC'] = None

            # find best non-overlapping matches for both pairs
            realMatches, dimuonMatches, muon0Matches, muon1Matches = matchedDimuonPairs(genMuonPairs, selectedDimuons)

            # keep track of how often there are 0 matches
            if len(realMatches) == 0:
                self.HISTS['counters'].Fill(MATCH0)

            # there should be at most 1 match
            elif len(realMatches) == 1:
                self.HISTS['counters'].Fill(MATCH1)
                bestDimuon['MSD'] = realMatches[realMatches.keys()[0]]['dim']
                MSD_ID = bestDimuon['MSD'].ID

                funcs = {
                    'chi2':lambda dim:dim.normChi2,
                    'Lxy' :lambda dim:dim.Lxy()
                }

                # fill some chi^2 histograms and Lxy
                for crit in ('LCD', 'HPD', 'LCD-OC', 'HPD-OC'):
                    if bestDimuon[crit] is not None and MSD_ID == bestDimuon[crit].ID:
                        self.HISTS['counters'].Fill(GOODMATCH[crit])
                        for Q in funcs:
                            self.HISTS['{}_{}_{}'.format(Q, crit, 'CID')].Fill(funcs[Q](bestDimuon['MSD']))
                    else:
                        for Q in funcs:
                            self.HISTS['{}_{}_{}'.format(Q, crit, 'MSD')].Fill(funcs[Q](bestDimuon['MSD']))
                            self.HISTS['{}_{}_{}'.format(Q, crit, 'LCD')].Fill(funcs[Q](bestDimuon['LCD']))
                    dimList = sortedDimuons if '-OC' not in crit else sortedOCDimuons
                    for dim in dimList:
                        if dim.ID != MSD_ID and bestDimuon[crit] is not None and dim.ID != bestDimuon[crit].ID:
                            for Q in funcs:
                                self.HISTS['{}_{}_{}'.format(Q, crit, 'UMD')].Fill(funcs[Q](dim))

            # if there were 2 matches, something's wrong
            else:
                print 'Something is terribly wrong!'

#### RUN ANALYSIS ####
if __name__ == '__main__':
    # get arguments
    ARGS = Analyzer.PARSER.parse_args()

    # set sample object based on arguments
    Analyzer.setSample(ARGS)

    # define Analyzer methods
    for METHOD in ('analyze', 'declareHistograms'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])

    # declare analyzer
    analyzer = Analyzer.Analyzer(
        ARGS        = ARGS,
        BRANCHKEYS  = ('DSAMUON', 'EVENT', 'GEN', 'DIMUON', 'TRIGGER'),
    )
    analyzer.writeHistograms('roots/3MuPlots{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else ''))
