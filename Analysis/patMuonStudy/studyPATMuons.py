import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedDimuons, matchedTrigger, applyPairingCriteria, replaceDSADimuons
import DisplacedDimuons.Analysis.Selector as Selector

QUANTITIES = {
    'Lxy'     : {'AXES':(800 ,      0., 800.   ), 'LAMBDA': lambda dim: dim.Lxy()                         , 'PRETTY':'L_{xy} [cm]'           },
    'LxySig'  : {'AXES':(5000,      0., 5000.  ), 'LAMBDA': lambda dim: dim.LxySig()                      , 'PRETTY':'L_{xy}/#sigma_{L_{xy}}'},
#   'LxyErr'  : {'AXES':(1000,      0., 100.   ), 'LAMBDA': lambda dim: dim.LxyErr()                      , 'PRETTY':'#sigma_{L_{xy}} [cm]'  },
    'vtxChi2' : {'AXES':(2000,      0., 1000.  ), 'LAMBDA': lambda dim: dim.normChi2                      , 'PRETTY':'vtx #chi^{2}/dof'      },
}

CONFIG = {
    'DSA-Lxy'     : {'QKEY':'Lxy'    },
    'DSA-LxySig'  : {'QKEY':'LxySig' },
#   'DSA-LxyErr'  : {'QKEY':'LxyErr' },
    'DSA-vtxChi2' : {'QKEY':'vtxChi2'},
    'PAT-Lxy'     : {'QKEY':'Lxy'    },
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

    self.HistInit('PAT-LxyRes', ';reco PAT L_{xy} #minus gen L_{xy} [cm];Counts', 1000, -.05 , .05)
    self.HistInit('DSA-LxyRes', ';reco DSA L_{xy} #minus gen L_{xy} [cm];Counts', 1000, -50. , 50.)

    self.HistInit('PAT-genLxy', ';gen L_{xy} [cm];Counts', 800, 0., 800.)
    self.HistInit('DSA-genLxy', ';gen L_{xy} [cm];Counts', 800, 0., 800.)

    self.HistInit('PAT-LxyResVSgenLxy', ';gen L_{xy} [cm];reco PAT L_{xy} #minus gen L_{xy} [cm];Counts', 800, 0., 800., 1000, -.05 , .05)
    self.HistInit('DSA-LxyResVSgenLxy', ';gen L_{xy} [cm];reco DSA L_{xy} #minus gen L_{xy} [cm];Counts', 800, 0., 800., 1000, -50. , 50.)

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

    Dimuons = [dim for dim in Dimuons3 if sum(dim.ID) < 999]

    selectedDimuons, selectedDSAmuons = Selector.SelectObjects(E, self.CUTS, Dimuons, DSAmuons)
    if selectedDimuons is None: return

    selectedIDs = [dim.ID for dim in selectedDimuons]
    replacedDimuons, wasReplaced = replaceDSADimuons(Dimuons3, DSAmuons, mode='PAT')
    replacedIDs = {dim.ID:rdim for dim, rdim, isReplaced in zip(Dimuons, replacedDimuons, wasReplaced) if isReplaced}

    for KEY in CONFIG:
        QKEY = KEY[4:]
        if 'DSA' in KEY:
            for dim in selectedDimuons:
                self.HISTS[KEY].Fill(QUANTITIES[QKEY]['LAMBDA'](dim), eventWeight)
        else:
            for dim in selectedDimuons:
                if dim.ID in replacedIDs:
                    rdim = replacedIDs[dim.ID]
                    if KEY != 'PAT-Lxy':
                        self.HISTS[KEY].Fill(QUANTITIES[QKEY]['LAMBDA'](rdim), eventWeight)
                    else:
                        self.HISTS[KEY].Fill(QUANTITIES[QKEY]['LAMBDA']( dim), eventWeight)
                    for attr in ('Tracker', 'Global'):
                        for idx in ('1', '2'):
                            if getattr(PATmuons[getattr(rdim, 'idx'+idx)-1000], 'is'+attr):
                                self.COUNTS[attr.lower()+idx] += 1

    self.COUNTS['selected'] += len(selectedIDs)
    self.COUNTS['replaced'] += len([ID for ID in selectedIDs if ID in replacedIDs])

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
            self.HISTS['DSA-genLxy'].Fill(genMuon.Lxy(), eventWeight)
            if dim.ID in replacedIDs:
                rdim = replacedIDs[dim.ID]
                self.HISTS['PAT-genLxy'].Fill(genMuon.Lxy(), eventWeight)
                #print '{:d} {:7d} {:9d} ::: {} ==> {} ::: {:9.4f} ==> {:9.4f} ::: {:8.4f} ==> {:8.4f} ::: {:8.2f} ==> {:8.2f} ::: {:7.3f} ==> {:7.3f}'.format(
                #    Event.run, Event.lumi, Event.event,
                #    dim.ID, rdim.ID,
                #    dim.LxySig(), rdim.LxySig(),
                #    dim.Lxy(), rdim.Lxy(),
                #    dim.normChi2, rdim.normChi2,
                #    genMuon.Lxy()-dim.Lxy(), genMuon.Lxy()-rdim.Lxy(),
                #    )
                if rdim.normChi2 < 50.:
                    self.HISTS['DSA-LxyRes'].Fill( dim.Lxy()-genMuon.Lxy(), eventWeight)
                    self.HISTS['PAT-LxyRes'].Fill(rdim.Lxy()-genMuon.Lxy(), eventWeight)

                    self.HISTS['DSA-LxyResVSgenLxy'].Fill(genMuon.Lxy(),  dim.Lxy()-genMuon.Lxy(), eventWeight)
                    self.HISTS['PAT-LxyResVSgenLxy'].Fill(genMuon.Lxy(), rdim.Lxy()-genMuon.Lxy(), eventWeight)


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
