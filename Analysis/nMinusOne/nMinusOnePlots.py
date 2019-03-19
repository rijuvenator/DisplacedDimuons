import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedDimuons
import DisplacedDimuons.Analysis.Selector as Selector

CUTS = ('NS', 'NH', 'FPTE', 'HLT', 'REP', 'PQ1', 'PT', 'PC', 'LXYE', 'M', 'CHI2')

#### CLASS AND FUNCTION DEFINITIONS ####
# setup function for Analyzer class
def begin(self, PARAMS=None):
    self.omitCounts = {'none':0}
    self.seqCounts  = {'none':0}
    for c in CUTS:
        self.omitCounts[c] = 0
        self.seqCounts [c] = 0

# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    self.HistInit('NM1', ';;Counts', len(CUTS)+1, 0., len(CUTS)+1.)
    self.HistInit('SEQ', ';;Counts', len(CUTS)+1, 0., len(CUTS)+1.)

# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    if self.TRIGGER and self.SP is not None:
        if not Selections.passedTrigger(E): return
    DSAmuons = E.getPrimitives('DSAMUON')
    PATmuons = E.getPrimitives('PATMUON')
    Dimuons3 = E.getPrimitives('DIMUON')
    Event    = E.getPrimitives('EVENT')

    eventWeight = 1.
    try:
        eventWeight = 1. if Event.weight > 0. else -1.
    except:
        pass

    selectedDimuons, selectedDSAmuons, selectedPATmuons = Selector.SelectObjects(E, '_Combined', Dimuons3, DSAmuons, PATmuons)
    if selectedDimuons is not None:
        self.seqCounts['none'] += 1
        self.HISTS['SEQ'].Fill(0., eventWeight)

    for idx, omit in enumerate(CUTS):
        CUTSTRING = '_Combined_' + '_'.join([c for c in CUTS if c != omit])
        selectedDimuons, selectedDSAmuons, selectedPATmuons = Selector.SelectObjects(E, CUTSTRING, Dimuons3, DSAmuons, PATmuons)
        if selectedDimuons is not None:
            self.omitCounts[omit] += 1
            self.HISTS['NM1'].Fill(idx+1., eventWeight)

    for idx in range(len(CUTS)):
        CUTSTRING = '_Combined_' + '_'.join(CUTS[:idx+1])
        selectedDimuons, selectedDSAmuons, selectedPATmuons = Selector.SelectObjects(E, CUTSTRING, Dimuons3, DSAmuons, PATmuons)
        if selectedDimuons is not None:
            self.seqCounts[CUTS[idx]] += 1
            self.HISTS['SEQ'].Fill(idx+1., eventWeight)
            if idx == len(CUTS)-1:
                self.omitCounts['none'] += 1
                self.HISTS['NM1'].Fill(0., eventWeight)

# cleanup function for Analyzer class
def end(self, PARAMS=None):
    fieldWidth = '5'
    nPlusC = ('none',) + CUTS
    fstring = '{:19s}     '
    for c in nPlusC:
        fstring += '{:>' + fieldWidth + 's} '
    print fstring.format('Heading', *nPlusC)
    if self.SP is None:
        fname = '{:19s}'.format(self.NAME)
    else:
        fname = '{:5s} {:4d} {:3d} {:4d}'.format('2Mu2J' if '2Mu2J' in self.NAME else '4Mu', *self.SP.SP)
    for key, hname in zip(('NM1', 'SEQ'), ('omitCounts', 'seqCounts')):
        fstring = fname + ' ' + key + ' '
        for c in nPlusC:
            fstring += '{' + c + ':' + fieldWidth + 'd} '
        print fstring.format(**getattr(self, hname))

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
        BRANCHKEYS  = ('DIMUON', 'PATMUON', 'DSAMUON', 'TRIGGER', 'GEN', 'EVENT'),
    )

    # write plots
    analyzer.writeHistograms('../analyzers/roots/mcbg/NM1Plots{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else ''))
