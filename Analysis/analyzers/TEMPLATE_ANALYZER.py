import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities

#### CLASS AND FUNCTION DEFINITIONS ####
# setup function for Analyzer class
def begin(self, PARAMS=None):
    pass

# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    self.HistInit('pT', ';p_{T} [GeV];Counts', 100, 0., 500.)

# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    # get dimuons
    Dimuons = E.getPrimitives('DIMUON')

    # loop over dimuons and fill if they pass their selection
    for dimuon in Dimuons:
        if Selections.DimuonSelection(dimuon):
            self.HISTS['pT'].Fill(dimuon.pt)

# cleanup function for Analyzer class
def end(self, PARAMS=None):
    pass

#### RUN ANALYSIS ####
if __name__ == '__main__':
    # get arguments
    ARGS = Analyzer.PARSER.parse_args()

    # set sample object based on arguments
    Analyzer.setSample(ARGS)

    # define Analyzer methods
    for METHOD in ('begin', 'declareHistograms', 'analyze', 'end'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])

    # declare analyzer
    analyzer = Analyzer.Analyzer(
        ARGS        = ARGS,
        BRANCHKEYS  = ('DIMUON',),
    )

    # write plots
    analyzer.writeHistograms('roots/test_{}.root')
