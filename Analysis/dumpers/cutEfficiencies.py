import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedMuons, pTRes

#### CLASS AND FUNCTION DEFINITIONS ####
# setup function for Analyzer class
def begin(self, PARAMS=None):
    self.COUNTERS = {
        'MUON'   : {'TOTAL' : 0, 'IND' : {}, 'SEQ' : {}, 'NM1' : {}},
        'DIMUON' : {'TOTAL' : 0, 'IND' : {}, 'SEQ' : {}, 'NM1' : {}}
    }
    for OBJECT in ('MUON', 'DIMUON'):
        for DTYPE, EXTRA in zip(('IND', 'SEQ', 'NM1'), ('PlusAll', 'PlusNone', '')):
            CutListName = OBJECT.title() + 'CutList' + EXTRA
            self.COUNTERS[OBJECT][DTYPE] = {key:0 for key in Selections.CutLists[CutListName]}

# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    DSAmuons = E.getPrimitives('DSAMUON')
    Dimuons  = E.getPrimitives('DIMUON' )

    DSASelections = [Selections.MuonSelection(muon) for muon in DSAmuons]

    # loop over DSAmuons and select
    for muon, muonSelection in zip(DSAmuons,DSASelections):

        self.COUNTERS['MUON']['TOTAL'] += 1

        muonSelection.IndividualIncrement(self.COUNTERS['MUON']['IND'])
        muonSelection.SequentialIncrement(self.COUNTERS['MUON']['SEQ'])
        muonSelection. NMinusOneIncrement(self.COUNTERS['MUON']['NM1'])

    # loop over dimuons and select
    for dimuon in Dimuons:
        muon1Selection = DSASelections[dimuon.idx1]
        muon2Selection = DSASelections[dimuon.idx2]
        if muon1Selection and muon2Selection:

            self.COUNTERS['DIMUON']['TOTAL'] += 1

            dimuonSelection = Selections.DimuonSelection(dimuon)
            dimuonSelection.IndividualIncrement(self.COUNTERS['DIMUON']['IND'])
            dimuonSelection.SequentialIncrement(self.COUNTERS['DIMUON']['SEQ'])
            dimuonSelection. NMinusOneIncrement(self.COUNTERS['DIMUON']['NM1'])

# cleanup function for Analyzer class
def end(self, PARAMS=None):
    COLMAX = max(max([len(s) for s in self.COUNTERS['MUON'  ]['IND']]),
                 max([len(s) for s in self.COUNTERS['DIMUON']['IND']]))

    if self.NAME.startswith('HTo2X'):
        sampleTitleFString = '{FS:<5s} {mH:<4s} {mX:<3s} {cTau:<4s} '
        sampleDataFString  = '{FS:<5s} {mH:<4d} {mX:<3d} {cTau:<4d} '
        FS                 = '4Mu' if '4Mu' in self.NAME else '2Mu2J'
        SAMPLE             = ''
    else:
        sampleTitleFString = '{SAM:<19s} '
        sampleDataFString  = '{SAM:<19s} '
        FS                 = ''
        SAMPLE             = self.NAME

    for OBJECT in ('MUON', 'DIMUON'):
        SHORT = OBJECT[:3]
        for DTYPE, EXTRA in zip(('IND', 'SEQ', 'NM1'), ('PlusAll', 'PlusNone', '')):
            CutListName = OBJECT.title() + 'CutList' + EXTRA

            if True:
                fstring = '{SHORT:3s} {DTYPE:3s}: ' + sampleTitleFString
                fstring += ' '.join(['{'+KEY+':<{COLMAX}s}}'.format(COLMAX=COLMAX) for KEY in Selections.CutLists[CutListName]])
                print fstring.format(
                    SHORT=SHORT,
                    DTYPE=DTYPE,
                    SAM='Sample',
                    FS='FS',
                    mH='mH',
                    mX='mX',
                    cTau='cTau',
                    **{KEY:KEY for KEY in Selections.CutLists[CutListName]}
                )

            if DTYPE in ('IND', 'SEQ'):
                TOTAL = float(self.COUNTERS[OBJECT]['TOTAL'])
                fstring = '{SHORT:3s} {DTYPE:3s}: ' + sampleDataFString
                fstring += ' '.join(['{'+KEY+':<{COLMAX}.3f}}'.format(COLMAX=COLMAX) for KEY in Selections.CutLists[CutListName]])
                print fstring.format(
                    SHORT=SHORT,
                    DTYPE=DTYPE,
                    SAM=SAMPLE,
                    FS=FS,
                    mH=self.SP.mH if self.SP is not None else 0,
                    mX=self.SP.mX if self.SP is not None else 0,
                    cTau=self.SP.cTau if self.SP is not None else 0,
                    **{KEY:(VAL/TOTAL if TOTAL != 0 else 0.) for KEY, VAL in self.COUNTERS[OBJECT][DTYPE].iteritems()}
                )

            elif DTYPE == 'NM1':
                TOTAL = float(self.COUNTERS[OBJECT]['IND']['all'])
                fstring = '{SHORT:3s} {DTYPE:3s}: ' + sampleDataFString
                fstring += ' '.join(['{'+KEY+':<{COLMAX}.3f}}'.format(COLMAX=COLMAX) for KEY in Selections.CutLists[CutListName]])
                print fstring.format(
                    SHORT=SHORT,
                    DTYPE=DTYPE,
                    SAM=SAMPLE,
                    FS=FS,
                    mH=self.SP.mH if self.SP is not None else 0,
                    mX=self.SP.mX if self.SP is not None else 0,
                    cTau=self.SP.cTau if self.SP is not None else 0,
                    **{KEY:(TOTAL/VAL if VAL != 0 else 0.) for KEY, VAL in self.COUNTERS[OBJECT][DTYPE].iteritems()}
                )


#### RUN ANALYSIS ####
if __name__ == '__main__':
    ARGS = Analyzer.PARSER.parse_args()
    Analyzer.setFNAME(ARGS)
    for METHOD in ('analyze','begin','end'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])
    analyzer = Analyzer.Analyzer(
        NAME        = ARGS.NAME,
        SIGNALPOINT = Utilities.SignalPoint(ARGS.SIGNALPOINT),
        BRANCHKEYS  = ('DSAMUON', 'DIMUON'),
        TEST        = ARGS.TEST,
        SPLITTING   = ARGS.SPLITTING,
        FILE        = ARGS.FNAME
    )
