import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedDimuons, matchedTrigger, applyPairingCriteria, replaceDSADimuons
import DisplacedDimuons.Analysis.Selector as Selector

QUANTITIES = {
    'Lxy'     : {'AXES':(1600,      0., 800.   ), 'LAMBDA': lambda dim: dim.Lxy()                         , 'PRETTY':'L_{xy} [cm]'           },
    'LxySig'  : {'AXES':(5000,      0., 5000.  ), 'LAMBDA': lambda dim: dim.LxySig()                      , 'PRETTY':'L_{xy}/#sigma_{L_{xy}}'},
    'LxyErr'  : {'AXES':(1000,      0., 100.   ), 'LAMBDA': lambda dim: dim.LxyErr()                      , 'PRETTY':'#sigma_{L_{xy}} [cm]'  },
    'vtxChi2' : {'AXES':(2000,      0., 1000.  ), 'LAMBDA': lambda dim: dim.normChi2                      , 'PRETTY':'vtx #chi^{2}/dof'      },
}

#### CLASS AND FUNCTION DEFINITIONS ####
# setup function for Analyzer class
def begin(self, PARAMS=None):
    self.COUNTS = {'events':0, 'debug_PC':0}

# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    for QKEY in QUANTITIES:
        if QKEY == 'LxyErr': continue
        XTIT = QUANTITIES[QKEY]['PRETTY']
        for RTYPE in ('DSA', 'PAT'):
            self.HistInit(RTYPE+'-'+QKEY, ';'+XTIT+';Counts', *QUANTITIES[QKEY]['AXES'])

    if True:
        self.HistInit('PAT-LxyErr', ';'+QUANTITIES['LxyErr']['PRETTY']+';Counts', 1000, 0., .1 )
        self.HistInit('DSA-LxyErr', ';'+QUANTITIES['LxyErr']['PRETTY']+';Counts', 1000, 0., 50.)

        self.HistInit('PAT-LxyResVSPAT-LxyErr', ';reco PAT #sigma_{L_{xy}} [cm];reco PAT L_{xy} #minus gen L_{xy} [cm];Counts', 1000, 0., .1 , 1000, -.05 , .05)
        self.HistInit('DSA-LxyResVSDSA-LxyErr', ';reco DSA #sigma_{L_{xy}} [cm];reco DSA L_{xy} #minus gen L_{xy} [cm];Counts', 1000, 0., 50., 1000, -50. , 50.)

    if self.SP is not None:
        self.HistInit('PAT-LxyRes', ';reco PAT L_{xy} #minus gen L_{xy} [cm];Counts', 1000, -.05 , .05)
        self.HistInit('DSA-LxyRes', ';reco DSA L_{xy} #minus gen L_{xy} [cm];Counts', 1000, -50. , 50.)

        self.HistInit('PAT-LxyPull', ';(reco PAT L_{xy} #minus gen L_{xy})/#sigma_{L_{xy}};Counts', 1000, -10., 10.)
        self.HistInit('DSA-LxyPull', ';(reco DSA L_{xy} #minus gen L_{xy})/#sigma_{L_{xy}};Counts', 1000, -10., 10.)

        self.HistInit('GEN-Lxy', ';gen L_{xy} [cm];Counts', 1600, 0., 800.)

        self.HistInit('PAT-LxyResVSGEN-Lxy', ';gen L_{xy} [cm];reco PAT L_{xy} #minus gen L_{xy} [cm];Counts', 1600, 0., 800., 1000, -.05 , .05)
        self.HistInit('DSA-LxyResVSGEN-Lxy', ';gen L_{xy} [cm];reco DSA L_{xy} #minus gen L_{xy} [cm];Counts', 1600, 0., 800., 1000, -50. , 50.)

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

    selectedDimuons, selectedDSAmuons, selectedPATmuons, debug_PC = Selector.SelectObjectsReordered(E, self.CUTS, Dimuons3, DSAmuons, PATmuons)
    if selectedDimuons is None: return

    self.COUNTS['events'] += 1
    self.COUNTS['debug_PC'] += debug_PC

    for dim in selectedDimuons:
        RTYPE = dim.composition
        for QKEY in QUANTITIES:
            KEY = RTYPE+'-'+QKEY
            self.HISTS[KEY].Fill(QUANTITIES[QKEY]['LAMBDA'](dim), eventWeight)

    if self.SP is not None:
        if '4Mu' in self.NAME:
            mu11, mu12, mu21, mu22, X1, X2, H, P, extramu = E.getPrimitives('GEN')
            genMuons = (mu11, mu12, mu21, mu22)
            genMuonPairs = ((mu11, mu12), (mu21, mu22))
        elif '2Mu2J' in self.NAME:
            mu1, mu2, j1, j2, X, XP, H, P, extramu = E.getPrimitives('GEN')
            genMuons = (mu1, mu2)
            genMuonPairs = ((mu1, mu2),)

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

        for pairIndex in realMatches:
            genMuon = genMuonPairs[pairIndex][0]
            dim = realMatches[pairIndex]['dim']
            self.HISTS['GEN-Lxy'].Fill(genMuon.Lxy(), eventWeight)
            RTYPE = dim.composition

            KEY = RTYPE + '-' + 'LxyRes'
            self.HISTS[KEY].Fill(dim.Lxy()-genMuon.Lxy(), eventWeight)

            KEY = RTYPE + '-' + 'LxyRes' + 'VSGEN-Lxy'
            self.HISTS[KEY].Fill(genMuon.Lxy(), dim.Lxy()-genMuon.Lxy(), eventWeight)

            KEY = RTYPE + '-' + 'LxyPull'
            self.HISTS[KEY].Fill((dim.Lxy()-genMuon.Lxy())/dim.LxyErr(), eventWeight)

            KEY = RTYPE + '-' + 'LxyRes' + 'VS' + RTYPE + '-' + 'LxyErr'
            self.HISTS[KEY].Fill(dim.LxyErr(), dim.Lxy()-genMuon.Lxy(), eventWeight)


# cleanup function for Analyzer class
def end(self, PARAMS=None):
    if self.SP is not None:
        print '{:5s} {:4d} {:3d} {:4d}'.format('4Mu' if '4Mu' in self.NAME else '2Mu2J', self.SP.mH, self.SP.mX, self.SP.cTau),
    else:
        print '{:s}'.format(self.NAME),
    print '{:5d} {:5d}'.format(self.COUNTS['events'], self.COUNTS['debug_PC'])

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
    #analyzer.writeHistograms('roots/ZephyrPlots{}{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else '', ARGS.CUTS))
    analyzer.writeHistograms('../analyzers/roots/mcbg/ZephyrPlots{}{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else '', ARGS.CUTS))
