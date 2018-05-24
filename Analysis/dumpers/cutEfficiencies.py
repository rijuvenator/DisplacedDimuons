import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedMuons, pTRes

#### CLASS AND FUNCTION DEFINITIONS ####
# setup function for Analyzer class
def begin(self):
    self.COUNTERS = {
        'MUON'   : {'TOTAL' : 0, 'IND' : {}, 'SEQ' : {}},
        'DIMUON' : {'TOTAL' : 0, 'IND' : {}, 'SEQ' : {}}
    }
    for OBJECT in ('MUON', 'DIMUON'):
        for DTYPE, EXTRA in zip(('IND', 'SEQ'), ('ALL', 'NONE')):
            CutListName = OBJECT.title() + 'CutListPlus' + EXTRA.title()
            self.COUNTERS[OBJECT][DTYPE] = {key:0 for key in Selections.CutLists[CutListName]}

# internal loop function for Analyzer class
def analyze(self, E):
    mu11, mu12, mu21, mu22, X1, X2, H, P = E.getPrimitives('GEN', 'HTo2XTo4Mu')
    DSAmuons = E.getPrimitives('DSAMUON')
    Dimuons  = E.getPrimitives('DIMUON' )

    DSASelections = [Selections.MuonSelection(muon) for muon in DSAmuons]

    # loop over genMuons and select
    for genMuon in (mu11, mu12, mu21, mu22):
        # cut genMuons outside the detector acceptance
        genMuonSelection = Selections.AcceptanceSelection(genMuon)
        if not genMuonSelection: continue

        self.COUNTERS['MUON']['TOTAL'] += 1

        matches = matchedMuons(genMuon, DSAmuons)
        if len(matches) != 0:
            closestRecoMuon          = DSAmuons     [matches[0]['idx']]
            closestRecoMuonSelection = DSASelections[matches[0]['idx']]

            closestRecoMuonSelection.IndividualIncrement(self.COUNTERS['MUON']['IND'])
            closestRecoMuonSelection.SequentialIncrement(self.COUNTERS['MUON']['SEQ'])

    # loop over dimuons and select
    for dimuon in Dimuons:
        muon1Selection = DSASelections[dimuon.idx1]
        muon2Selection = DSASelections[dimuon.idx2]
        if muon1Selection and muon2Selection:

            self.COUNTERS['DIMUON']['TOTAL'] += 1

            dimuonSelection = Selections.DimuonSelection(dimuon)
            dimuonSelection.IndividualIncrement(self.COUNTERS['DIMUON']['IND'])
            dimuonSelection.SequentialIncrement(self.COUNTERS['DIMUON']['SEQ'])

# cleanup function for Analyzer class
def end(self):
    COLMAX = max(max([len(s) for s in self.COUNTERS['MUON'  ]['IND']]),
                 max([len(s) for s in self.COUNTERS['DIMUON']['IND']]))
    for OBJECT in ('MUON', 'DIMUON'):
        SHORT = OBJECT[:3]
        for DTYPE, EXTRA in zip(('IND', 'SEQ'), ('ALL', 'NONE')):
            CutListName = OBJECT.title() + 'CutListPlus' + EXTRA.title()
            fstring = '{SHORT:3s} {DTYPE:3s}: {mH:<4s} {mX:<3s} {cTau:<4s} '
            fstring += ' '.join(['{'+KEY+':<{COLMAX}s}}'.format(COLMAX=COLMAX) for KEY in Selections.CutLists[CutListName]])
            print fstring.format(
                SHORT=SHORT,
                DTYPE=DTYPE,
                mH='mH',
                mX='mX',
                cTau='cTau',
                **{KEY:KEY for KEY in Selections.CutLists[CutListName]}
            )

            TOTAL = float(self.COUNTERS[OBJECT]['TOTAL'])
            fstring = '{SHORT:3s} {DTYPE:3s}: {mH:<4d} {mX:<3d} {cTau:<4d} '
            fstring += ' '.join(['{'+KEY+':<{COLMAX}.3f}}'.format(COLMAX=COLMAX) for KEY in Selections.CutLists[CutListName]])
            print fstring.format(
                SHORT=SHORT,
                DTYPE=DTYPE,
                mH=self.SP.mH,
                mX=self.SP.mX,
                cTau=self.SP.cTau,
                **{KEY:VAL/TOTAL for KEY, VAL in self.COUNTERS[OBJECT][DTYPE].iteritems()}
            )


#### RUN ANALYSIS ####
if __name__ == '__main__':
    ARGS = Analyzer.PARSER.parse_args()
    for METHOD in ('analyze','begin','end'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])
    analyzer = Analyzer.Analyzer(
        NAME        = ARGS.NAME,
        SIGNALPOINT = Utilities.SignalPoint(ARGS.SIGNALPOINT),
        BRANCHKEYS  = ('GEN', 'DSAMUON', 'DIMUON'),
        TEST        = ARGS.TEST,
        SPLITTING   = ARGS.SPLITTING,
        FILE        = Analyzer.F_AOD_NTUPLE
    )
