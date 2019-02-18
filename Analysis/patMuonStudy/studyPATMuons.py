import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedDimuons, matchedTrigger, applyPairingCriteria, replaceDSADimuons
import DisplacedDimuons.Analysis.Selector as Selector

QUANTITIES = {
#   'Lxy'     : {'AXES':(1000,      0., 800.   ), 'LAMBDA': lambda dim: dim.Lxy()                         , 'PRETTY':'L_{xy} [cm]'           },
    'LxySig'  : {'AXES':(5000,      0., 5000.  ), 'LAMBDA': lambda dim: dim.LxySig()                      , 'PRETTY':'L_{xy}/#sigma_{L_{xy}}'},
#   'LxyErr'  : {'AXES':(1000,      0., 100.   ), 'LAMBDA': lambda dim: dim.LxyErr()                      , 'PRETTY':'#sigma_{L_{xy}} [cm]'  },
    'vtxChi2' : {'AXES':(2000,      0., 1000.  ), 'LAMBDA': lambda dim: dim.normChi2                      , 'PRETTY':'vtx #chi^{2}/dof'      },
}

CONFIG = {
    'DSA-LxySig'  : {'QKEY':'LxySig' },
#   'DSA-LxyErr'  : {'QKEY':'LxyErr' },
    'DSA-vtxChi2' : {'QKEY':'vtxChi2'},
    'PAT-LxySig'  : {'QKEY':'LxySig' },
#   'PAT-LxyErr'  : {'QKEY':'LxyErr' },
    'PAT-vtxChi2' : {'QKEY':'vtxChi2'},
}

#### CLASS AND FUNCTION DEFINITIONS ####
# setup function for Analyzer class
def begin(self, PARAMS=None):
    self.COUNTS = {'selected':0, 'replaced':0, 'tracker1':0, 'tracker2':0, 'global1':0, 'global2':0}

# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    for KEY in CONFIG:
        XTIT = QUANTITIES[CONFIG[KEY]['QKEY']]['PRETTY']
        self.HistInit(KEY, ';'+XTIT+';Counts', *QUANTITIES[CONFIG[KEY]['QKEY']]['AXES'])

# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    if self.TRIGGER and self.SP is not None:
        if not Selections.passedTrigger(E): return
    DSAmuons = E.getPrimitives('DSAMUON')
    PATmuons = E.getPrimitives('PATMUON')
    Dimuons3 = E.getPrimitives('DIMUON')
    Event    = E.getPrimitives('EVENT')

    Dimuons = [dim for dim in Dimuons3 if sum(dim.ID) < 999]

    if self.SP is not None:
        if '4Mu' in self.NAME:
            mu11, mu12, mu21, mu22, X1, X2, H, P, extramu = E.getPrimitives('GEN')
            genMuons = (mu11, mu12, mu21, mu22)
            genMuonPairs = ((mu11, mu12), (mu21, mu22))
        elif '2Mu2J' in self.NAME:
            mu1, mu2, j1, j2, X, XP, H, P, extramu = E.getPrimitives('GEN')
            genMuons = (mu1, mu2)
            genMuonPairs = ((mu1, mu2),)

    eventWeight = 1.
    try:
        eventWeight = 1. if Event.weight > 0. else -1.
    except:
        pass

    selectedDimuons, selectedDSAmuons = Selector.SelectObjects(E, self.CUTS, Dimuons, DSAmuons)
    if selectedDimuons is None: return

    selectedIDs = [dim.ID for dim in selectedDimuons]
    replacedDimuons, wasReplaced = replaceDSADimuons(Dimuons3, DSAmuons, mode='PAT')
    replacedIDs = [dim.ID for dim,isReplaced in zip(Dimuons,wasReplaced) if isReplaced]

    for KEY in CONFIG:
        QKEY = KEY[4:]
        if 'DSA' in KEY:
            for dim in selectedDimuons:
                self.HISTS[KEY].Fill(QUANTITIES[QKEY]['LAMBDA'](dim), eventWeight)
        else:
            for dim, rdim, wasrep in zip(Dimuons, replacedDimuons, wasReplaced):
                if dim.ID in selectedIDs and wasrep:
                    self.HISTS[KEY].Fill(QUANTITIES[QKEY]['LAMBDA'](rdim), eventWeight)
                    if PATmuons[rdim.idx1-1000].isTracker:
                        self.COUNTS['tracker1'] += 1
                    if PATmuons[rdim.idx2-1000].isTracker:
                        self.COUNTS['tracker2'] += 1
                    if PATmuons[rdim.idx1-1000].isGlobal:
                        self.COUNTS['global1'] += 1
                    if PATmuons[rdim.idx2-1000].isGlobal:
                        self.COUNTS['global2'] += 1

    self.COUNTS['selected'] += len(selectedIDs)
    self.COUNTS['replaced'] += len([ID for ID in selectedIDs if ID in replacedIDs])


# cleanup function for Analyzer class
def end(self, PARAMS=None):
    if self.SP is not None:
        print '{:5s} {:4d} {:3d} {:4d} {:5d} {:5d} {:7.4f} {:5d} {:5d} {:5d} {:5d}'.format('4Mu' if '4Mu' in self.NAME else '2Mu2J', self.SP.mH, self.SP.mX, self.SP.cTau, self.COUNTS['selected'], self.COUNTS['replaced'], self.COUNTS['replaced']/float(self.COUNTS['selected'])*100., self.COUNTS['tracker1'], self.COUNTS['tracker2'], self.COUNTS['global1'], self.COUNTS['global2'])
    else:
        print '{:s} {:5d} {:5d} {:7.4f} {:5d} {:5d} {:5d} {:5d}'.format(self.NAME, self.COUNTS['selected'], self.COUNTS['replaced'], self.COUNTS['replaced']/float(self.COUNTS['selected'])*100., self.COUNTS['tracker1'], self.COUNTS['tracker2'], self.COUNTS['global1'], self.COUNTS['global2'])

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
    #analyzer.writeHistograms('roots/PATMuonStudyPlots{}{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else '', ARGS.CUTS))
    analyzer.writeHistograms('../analyzers/roots/mcbg/PATMuonStudyPlots{}{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else '', ARGS.CUTS))
