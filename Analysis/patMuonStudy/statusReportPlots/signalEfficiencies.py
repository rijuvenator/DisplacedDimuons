import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedDimuons
import DisplacedDimuons.Analysis.Selector as Selector
import DisplacedDimuons.Analysis.PrimitivesPrinter as Printer

Printer.COLORON = True

#### CLASS AND FUNCTION DEFINITIONS ####
# setup function for Analyzer class
def begin(self, PARAMS=None):
    self.COUNTS = {float('inf'):0, R.TMath.Pi()/2.:0}
    self.MATCH  = {float('inf'):0, R.TMath.Pi()/2.:0}

# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    for z in range(16):
        b = '{:>04s}'.format(str(bin(z))[2:])
        self.HistInit('Lxy-Trig{}-Acc{}-Reco{}-Sel{}'.format(*b), ';gen L_{xy} [cm];Counts', 800, 0., 800.)

# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):

    Event = E.getPrimitives('EVENT')

    # take 10% of data: event numbers ending in 7
    if 'DoubleMuon' in self.NAME:
        if Event.event % 10 != 7: return

    DSAmuons = E.getPrimitives('DSAMUON')
    PATmuons = E.getPrimitives('PATMUON')
    Dimuons3 = E.getPrimitives('DIMUON')

    if '4Mu' in self.NAME:
        mu11, mu12, mu21, mu22, X1, X2, H, P, extramu = E.getPrimitives('GEN')
        genMuons = (mu11, mu12, mu21, mu22)
        genMuonPairs = ((mu11, mu12), (mu21, mu22))
    elif '2Mu2J' in self.NAME:
        mu1, mu2, j1, j2, X, XP, H, P, extramu = E.getPrimitives('GEN')
        genMuons = (mu1, mu2)
        genMuonPairs = ((mu1, mu2),)

    genMuonPair = genMuonPairs[0]
    genLxy = genMuonPair[0].Lxy()

    TRIG = Selections.passedTrigger(E)

    ACC = Selections.AcceptanceSelection(genMuonPair)

    RECO = False
    dimuonMatches, muonMatches, exitcode = matchedDimuons(genMuonPair, Dimuons3, DSAmuons, vertex='BS', doDimuons=False)
    genMuonMatches = exitcode.getBestGenMuonMatches(muonMatches)
    if genMuonMatches[0] is not None and genMuonMatches[1] is not None:
        RECO = True

    SEL = False
    CUTS = '_Combined_NS_NH_FPTE_HLT_REP_PT_DCA_PC_LXYE_MASS_CHI2_VTX_COSA_NPP_LXYSIG_TRK_NDT_DPHI'
    selectedDimuons, selectedDSAmuons, selectedPATmuons = Selector.SelectObjects(E, CUTS, Dimuons3, DSAmuons, PATmuons)
    if selectedDimuons is not None:

        selectedDimuons = [dim for dim in selectedDimuons if dim.composition == 'DSA']

        dimuonMatches, muonMatches, exitcode = matchedDimuons(genMuonPair, selectedDimuons)
        if len(dimuonMatches) > 0:
            realMatches = {0:dimuonMatches[0]}
        else:
            realMatches = {}

        if len(realMatches) > 0:
            SEL = True

    KEY = 'Trig{}-Acc{}-Reco{}-Sel{}'.format(*[int(bool(x)) for x in (TRIG, ACC, RECO, SEL)])

    genLxy = genMuonPair[0].Lxy()
    self.HISTS['Lxy-'+KEY].Fill(genLxy)

# cleanup function for Analyzer class
def end(self, PARAMS=None):
    ACRO = 'TARS'

    print '{:4d} {:3d} {:4d}'.format(*self.SP.SP),
    for z in range(16):
        b = '{:>04s}'.format(str(bin(z))[2:])
        i = '{}{}{}{}'.format(*[ACRO[x] if b[x]=='1' else '' for x in range(len(b))])
        print '{:>5s}'.format(i if i != '' else 'X'),
    print ''

    print '{:4d} {:3d} {:4d}'.format(*self.SP.SP),
    for z in range(16):
        b = '{:>04s}'.format(str(bin(z))[2:])
        print '{:5d}'.format(int(self.HISTS['Lxy-Trig{}-Acc{}-Reco{}-Sel{}'.format(*b)].GetEntries())),
    print ''

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
        BRANCHKEYS  = ('DIMUON', 'PATMUON', 'DSAMUON', 'TRIGGER', 'GEN', 'EVENT', 'FILTER'),
    )

    analyzer.writeHistograms('roots/mcbg/SignalEfficiencies_{}.root')
