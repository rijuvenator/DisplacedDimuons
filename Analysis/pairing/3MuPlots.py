import ROOT as R
import numpy as np
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedMuons, matchedDimuons, matchedDimuonPairs

#### CLASS AND FUNCTION DEFINITIONS ####
# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    self.HistInit('counters', ';Categories;Counts' , 8  , 0., 8.  )
    self.HistInit('GLxy_MSD', ';L_{xy} [cm];Counts', 330, 0., 330.)
    self.HistInit('GLxy_LCD', ';L_{xy} [cm];Counts', 330, 0., 330.)
    self.HistInit('RLxy_MSD', ';L_{xy} [cm];Counts', 330, 0., 330.)
    self.HistInit('RLxy_LCD', ';L_{xy} [cm];Counts', 330, 0., 330.)

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
    GOODMATCH  = 7.

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

        indices = [mu.idx for mu in selectedMuons]
        HPDs    = [dim for dim in selectedDimuons if dim.idx1 in indices and dim.idx2 in indices]
        HPDIDs  = {(dim.idx1, dim.idx2):dim for dim in HPDs}

        if len(HPDs) > 0:
            # find LCD
            sortedDimuons = sorted(HPDs, key=lambda dim: dim.normChi2)
            LCD   = sortedDimuons[0]
            LCDID = (LCD.idx1, LCD.idx2)

            # find best non-overlapping matches for both pairs
            realMatches, dimuonMatches, muon0Matches, muon1Matches = matchedDimuonPairs(genMuonPairs, selectedDimuons)

            # keep track of how often there are 0 matches
            if len(realMatches) == 0:
                self.HISTS['counters'].Fill(MATCH0)

            # there should be at most 1 match
            elif len(realMatches) == 1:
                self.HISTS['counters'].Fill(MATCH1)
                MSD = realMatches[realMatches.keys()[0]]['dim']
                MSDID = (MSD.idx1, MSD.idx2)

                # if there's a signal match, fill a denominator histogram
                self.HISTS['GLxy_MSD'].Fill(genMuonPairs[realMatches.keys()[0]][0].Lxy())
                self.HISTS['RLxy_MSD'].Fill(MSD.Lxy())

                # if LCD = MSD, fill a numberator histogram
                if MSDID == LCDID:
                    self.HISTS['counters'].Fill(GOODMATCH)
                    self.HISTS['GLxy_LCD'].Fill(genMuonPairs[realMatches.keys()[0]][0].Lxy())
                    self.HISTS['RLxy_LCD'].Fill(MSD.Lxy())

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
