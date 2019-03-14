import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedDimuons, matchedTrigger, applyPairingCriteria, replaceDSADimuons
import DisplacedDimuons.Analysis.Selector as Selector

# see commit from Mar 5 2019 for the patch required to run studyPTCut.py

QUANTITIES = {
    'Lxy'     : {'AXES':(1600,      0., 800.   ), 'LAMBDA': lambda dim: dim.Lxy()                         , 'PRETTY':'L_{xy} [cm]'           },
    'LxySig'  : {'AXES':(5000,      0., 5000.  ), 'LAMBDA': lambda dim: dim.LxySig()                      , 'PRETTY':'L_{xy}/#sigma_{L_{xy}}'},
    'LxyErr'  : {'AXES':(1000,      0., 100.   ), 'LAMBDA': lambda dim: dim.LxyErr()                      , 'PRETTY':'#sigma_{L_{xy}} [cm]'  },
    'vtxChi2' : {'AXES':(2000,      0., 1000.  ), 'LAMBDA': lambda dim: dim.normChi2                      , 'PRETTY':'vtx #chi^{2}/dof'      },
}

MCQUANTITIES = {
        'chi2'       : {'AXES':(1000, 0., 500.), 'LAMBDA': lambda mu: mu.chi2                  , 'PRETTY':'trk #chi^{2}'     },
        'nTrkLay'    : {'AXES':(  20, 0.,  20.), 'LAMBDA': lambda mu: float(mu.nTrackerLayers) , 'PRETTY':'N(tracker layers)'},
        'nPxlHit'    : {'AXES':(   5, 0.,   5.), 'LAMBDA': lambda mu: float(mu.nPixelHits    ) , 'PRETTY':'N(pixel hits)'    },
        'highPurity' : {'AXES':(   2, 0.,   2.), 'LAMBDA': lambda mu: float(mu.highPurity    ) , 'PRETTY':'high purity'      },
        'isGlobal'   : {'AXES':(   2, 0.,   2.), 'LAMBDA': lambda mu: float(mu.isGlobal      ) , 'PRETTY':'is global'        },
}

#### CLASS AND FUNCTION DEFINITIONS ####
# setup function for Analyzer class
def begin(self, PARAMS=None):
    pass

# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    self.HistInit('nMatches', ';p_{T} Cut [GeV];Events with matched gen dimuons', 31, 0., 31.)

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

    if self.SP is not None:
        if '4Mu' in self.NAME:
            mu11, mu12, mu21, mu22, X1, X2, H, P, extramu = E.getPrimitives('GEN')
            genMuons = (mu11, mu12, mu21, mu22)
            genMuonPairs = ((mu11, mu12), (mu21, mu22))
        elif '2Mu2J' in self.NAME:
            mu1, mu2, j1, j2, X, XP, H, P, extramu = E.getPrimitives('GEN')
            genMuons = (mu1, mu2)
            genMuonPairs = ((mu1, mu2),)

        for pTCut in xrange(31):

            selectedDimuons, selectedDSAmuons, selectedPATmuons = Selector.SelectObjectsReordered(E, self.CUTS, Dimuons3, DSAmuons, PATmuons, keepHybrids=True, option=3, pTCut=float(pTCut))
            if selectedDimuons is None: continue

            # do the signal matching
            if len(genMuonPairs) == 1:
                genMuonPair = genMuonPairs[0]
                dimuonMatches, muonMatches, exitcode = matchedDimuons(genMuonPair, selectedDimuons)
                if len(dimuonMatches) > 0:
                    realMatches = {0:dimuonMatches[0]}
                else:
                    realMatches = {}
            else:
                realMatches, dimuonMatches, muon0Matches, muon1Matches = matchedDimuonPairs(genMuonPairs, selectedDimuons)

            if len(realMatches) > 0:
                self.HISTS['nMatches'].Fill(float(pTCut), eventWeight)


# cleanup function for Analyzer class
def end(self, PARAMS=None):
    pass

#### RUN ANALYSIS ####
if __name__ == '__main__':
    Analyzer.PARSER.add_argument('--pcoption', dest='PCOPTION', type=int , default=3)
    Analyzer.PARSER.add_argument('--hybrids' , dest='HYBRIDS' , action='store_true')
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
    analyzer.writeHistograms('../analyzers/roots/mcbg/PTCutPlots_{}.root')
