import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedDimuons
import DisplacedDimuons.Analysis.Selector as Selector

CUTS = ['NS_NH', 'FPTE', 'HLT', 'PT', 'DCA', 'LXYE', 'MASS', 'CHI2', 'VTX', 'COSA_NPP', 'LXYSIG', 'TRK', 'NDT', 'DPHI']

#### CLASS AND FUNCTION DEFINITIONS ####
# setup function for Analyzer class
def begin(self, PARAMS=None):
    if self.SP is None and self.ARGS.IDPHI:
        CUTS[-1] = 'IDPHI'

    self.omitCounts = {'none':0}
    self.seqCounts  = {'none':0}
    for c in CUTS:
        self.omitCounts[c] = 0
        self.seqCounts [c] = 0

    self.DSAomitCounts = {'none':0}
    self.DSAseqCounts  = {'none':0}
    for c in CUTS:
        self.DSAomitCounts[c] = 0
        self.DSAseqCounts [c] = 0

# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    self.HistInit('NM1', ';;Counts', len(CUTS)+1, 0., len(CUTS)+1.)
    self.HistInit('SEQ', ';;Counts', len(CUTS)+1, 0., len(CUTS)+1.)

    self.HistInit('DSA-NM1', ';;Counts', len(CUTS)+1, 0., len(CUTS)+1.)
    self.HistInit('DSA-SEQ', ';;Counts', len(CUTS)+1, 0., len(CUTS)+1.)

# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    if self.TRIGGER and self.SP is not None:
        if not Selections.passedTrigger(E): return

    Event = E.getPrimitives('EVENT')

    # take 10% of data: event numbers ending in 7
    if 'DoubleMuon' in self.NAME and not self.ARGS.IDPHI:
        if Event.event % 10 != 7: return

    DSAmuons = E.getPrimitives('DSAMUON')
    PATmuons = E.getPrimitives('PATMUON')
    Dimuons3 = E.getPrimitives('DIMUON')

    BASECUTS = '_Combined_REP_PC'

    eventWeight = 1.
    try:
        eventWeight = 1. if Event.weight > 0. else -1.
    except:
        pass

    def nDSA(selDims):
        return len([d for d in selDims if d.composition == 'DSA'])

    selectedDimuons, selectedDSAmuons, selectedPATmuons = Selector.SelectObjects(E, BASECUTS, Dimuons3, DSAmuons, PATmuons, bumpFPTE=self.ARGS.BUMPFPTE)
    if selectedDimuons is not None:

        self.seqCounts['none'] += 1
        self.HISTS['SEQ'].Fill(0., eventWeight)

        self.DSAseqCounts['none'] += nDSA(selectedDimuons)
        self.HISTS['DSA-SEQ'].Fill(0., eventWeight*nDSA(selectedDimuons))

    for idx, omit in enumerate(CUTS):
        CUTSTRING = BASECUTS + '_' + '_'.join([c for c in CUTS if c != omit])
        selectedDimuons, selectedDSAmuons, selectedPATmuons = Selector.SelectObjects(E, CUTSTRING, Dimuons3, DSAmuons, PATmuons, bumpFPTE=self.ARGS.BUMPFPTE)
        if selectedDimuons is not None:
            self.omitCounts[omit] += 1
            self.HISTS['NM1'].Fill(idx+1., eventWeight)

            self.DSAomitCounts[omit] += nDSA(selectedDimuons)
            self.HISTS['DSA-NM1'].Fill(idx+1., eventWeight*nDSA(selectedDimuons))

    for idx in range(len(CUTS)):
        CUTSTRING = BASECUTS + '_' + '_'.join(CUTS[:idx+1])
        selectedDimuons, selectedDSAmuons, selectedPATmuons = Selector.SelectObjects(E, CUTSTRING, Dimuons3, DSAmuons, PATmuons, bumpFPTE=self.ARGS.BUMPFPTE)
        if selectedDimuons is not None:
            self.seqCounts[CUTS[idx]] += 1
            self.HISTS['SEQ'].Fill(idx+1., eventWeight)

            self.DSAseqCounts[CUTS[idx]] += nDSA(selectedDimuons)
            self.HISTS['DSA-SEQ'].Fill(idx+1., eventWeight*nDSA(selectedDimuons))

            if idx == len(CUTS)-1:
                self.omitCounts['none'] += 1
                self.HISTS['NM1'].Fill(0., eventWeight)

                self.DSAomitCounts['none'] += nDSA(selectedDimuons)
                self.HISTS['DSA-NM1'].Fill(0., eventWeight*nDSA(selectedDimuons))

# cleanup function for Analyzer class
def end(self, PARAMS=None):
    def modifiedName(name):
        if 'DoubleMuon' in name:
            return 'Data'+name[17]
        if 'QCD' in name:
            return 'QCD'
        return name

    fieldWidth = '8'
    nPlusC = ['none'] + CUTS
    fstring = '{:19s}     '
    for c in nPlusC:
        fstring += '{:>' + fieldWidth + 's} '
    print fstring.format('Heading', *nPlusC)
    if self.SP is None:
        fname = '{:19s}'.format(modifiedName(self.NAME))
    else:
        fname = '{:5s} {:4d} {:3d} {:4d}'.format('2Mu2J' if '2Mu2J' in self.NAME else '4Mu', *self.SP.SP)
    for key, hname in zip(('NM1', 'SEQ'), ('omitCounts', 'seqCounts')):
        fstring = fname + ' ' + key + ' '
        for c in nPlusC:
            fstring += '{' + c + ':' + fieldWidth + 'd} '
        print fstring.format(**getattr(self, hname))

    for key, hname in zip(('NM1', 'SEQ'), ('DSAomitCounts', 'DSAseqCounts')):
        fstring = fname + ' ' + key + ' '
        for c in nPlusC:
            fstring += '{' + c + ':' + fieldWidth + 'd} '
        print fstring.format(**getattr(self, hname))

#### RUN ANALYSIS ####
if __name__ == '__main__':
    # get arguments
    Analyzer.PARSER.add_argument('--bump', dest='BUMPFPTE', action='store_true')
    Analyzer.PARSER.add_argument('--idphi', dest='IDPHI', action='store_true')
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

    # write plots
    analyzer.writeHistograms('roots/mcbg/NM1Plots{}{}{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else '', '_Bump' if ARGS.BUMPFPTE else '', '' if not ARGS.IDPHI else '_IDPHI'))
