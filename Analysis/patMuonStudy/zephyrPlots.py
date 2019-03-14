import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedDimuons
import DisplacedDimuons.Analysis.Selector as Selector

QUANTITIES = {
    'Lxy'     : {'LAMBDA': lambda dim: dim.Lxy()                           , 'PRETTY':'L_{xy} [cm]'           },
    'LxySig'  : {'LAMBDA': lambda dim: dim.LxySig()                        , 'PRETTY':'L_{xy}/#sigma_{L_{xy}}'},
    'LxyErr'  : {'LAMBDA': lambda dim: dim.LxyErr()                        , 'PRETTY':'#sigma_{L_{xy}} [cm]'  },
    'vtxChi2' : {'LAMBDA': lambda dim: dim.normChi2                        , 'PRETTY':'vtx #chi^{2}/dof'      },
    'd0Sig'   : {'LAMBDA': lambda dim: min(dim.mu1.d0Sig(),dim.mu2.d0Sig()), 'PRETTY':'|d_{0}|/#sigma_{d_{0}}'},
}

AXES = {
    'DSA' : {
        'Lxy'     : (1600,   0.  , 800.   ), # 0.5  cm bins
        'LxySig'  : ( 600,   0.  , 300.   ), # 0.5     bins
        'LxyErr'  : (1000,   0.  ,  50.   ), # 0.05 cm bins
        'vtxChi2' : (1000,   0.  ,  50.   ), # 0.05    bins
        'd0Sig'   : ( 800,   0.  ,  80.   ), # 0.1     bins
        'LxyRes'  : (1000, -50.  ,  50.   ), # 0.1  cm bins
    },
    'PAT' : {
        'Lxy'     : ( 140,   0.  ,   70.  ),
        'LxySig'  : (1000,   0.  ,  500.  ),
        'LxyErr'  : (1000,   0.  ,     .1 ), # 1e-4 cm bins
        'vtxChi2' : (1000,   0.  ,   50.  ),
        'd0Sig'   : (2000,   0.  ,  200.  ),
        'LxyRes'  : (1000,   -.05,     .05), # 1e-4 cm bins
    },
    'HYB' : {
        'Lxy'     : ( 140,   0.  ,  70.   ),
        'LxySig'  : ( 600,   0.  , 300.   ),
        'LxyErr'  : (1000,   0.  ,  25.   ), # 0.05 cm bins
        'vtxChi2' : (1000,   0.  ,  50.   ),
        'd0Sig'   : ( 800,   0.  ,  80.   ),
        'LxyRes'  : (1000, -25.  ,  25.   ), # 0.05 cm bins
    },
}

MCQUANTITIES = {
        'normChi2'            : {'AXES':(1000, 0., 100.), 'LAMBDA': lambda mu: mu.normChi2            , 'PRETTY':'trk #chi^{2}/dof'         },
        'nTrkLay'             : {'AXES':(  20, 0.,  20.), 'LAMBDA': lambda mu: mu.nTrackerLayers      , 'PRETTY':'N(tracker layers)'        },
        'nPxlHit'             : {'AXES':(   5, 0.,   5.), 'LAMBDA': lambda mu: mu.nPixelHits          , 'PRETTY':'N(pixel hits)'            },
        'highPurity'          : {'AXES':(   2, 0.,   2.), 'LAMBDA': lambda mu: mu.highPurity          , 'PRETTY':'high purity'              },
        'isGlobal'            : {'AXES':(   2, 0.,   2.), 'LAMBDA': lambda mu: mu.isGlobal            , 'PRETTY':'is global'                },
        'isMedium'            : {'AXES':(   2, 0.,   2.), 'LAMBDA': lambda mu: mu.isMedium            , 'PRETTY':'is medium'                },
        'hitsBeforeVtx'       : {'AXES':(  10, 0.,  10.), 'LAMBDA': lambda mu: mu.hitsBeforeVtx       , 'PRETTY':'N(hits before vtx)'       },
        'missingHitsAfterVtx' : {'AXES':(  10, 0.,  10.), 'LAMBDA': lambda mu: mu.missingHitsAfterVtx , 'PRETTY':'N(missing hits after vtx)'},
}

#### CLASS AND FUNCTION DEFINITIONS ####
# setup function for Analyzer class
def begin(self, PARAMS=None):
    pass

# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    for QKEY in QUANTITIES:
        XTIT = QUANTITIES[QKEY]['PRETTY']
        for RTYPE in ('DSA', 'PAT', 'HYB'):
            self.HistInit(RTYPE+'-'+QKEY, ';'+XTIT+';Counts', *AXES[RTYPE][QKEY])

    for QKEY in MCQUANTITIES:
        TIT = MCQUANTITIES[QKEY]['PRETTY']
        A = MCQUANTITIES[QKEY]['AXES']
        self.HistInit('PAT-12-'+QKEY, ';#mu_{{1}} {};#mu_{{2}} {};Counts'.format(TIT, TIT), *(A+A))

    LxyPull = (1000, -10., 10. )
    GenLxy  = (1600,   0., 800.)

    if self.SP is not None:
        for RTYPE in ('DSA', 'PAT', 'HYB'):
            AR = AXES[RTYPE]
            self.HistInit('{R}-LxyRes'            .format(R=RTYPE),  ';reco {R} L_{{xy}} #minus gen L_{{xy}} [cm];Counts'                                     .format(R=RTYPE), *AR['LxyRes']               )
            self.HistInit('{R}-LxyPull'           .format(R=RTYPE), ';(reco {R} L_{{xy}} #minus gen L_{{xy}})/#sigma_{{L_{{xy}}}};Counts'                     .format(R=RTYPE), *LxyPull                    )
            self.HistInit('GEN-Lxy-{R}'           .format(R=RTYPE), ';gen L_{xy} [cm];Counts'                                                                                 , *GenLxy                     )
            self.HistInit('{R}-LxyResVSGEN-Lxy'   .format(R=RTYPE), ';gen L_{{xy}} [cm];reco {R} L_{{xy}} #minus gen L_{{xy}} [cm];Counts'                    .format(R=RTYPE), *(GenLxy+AR['LxyRes'])      )
            self.HistInit('{R}-LxyResVS{R}-LxyErr'.format(R=RTYPE), ';reco {R} #sigma_{{L_{{xy}}}} [cm];reco {R} L_{{xy}} #minus gen L_{{xy}} [cm];Counts'    .format(R=RTYPE), *(AR['LxyErr']+AR['LxyRes']))

        self.HistInit('GEN-Lxy', ';gen L_{xy} [cm];Counts', 1600, 0., 800.)

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

    selectedDimuons, selectedDSAmuons, selectedPATmuons = Selector.SelectObjects(E, self.CUTS, Dimuons3, DSAmuons, PATmuons)
    if selectedDimuons is None: return

    for dim in selectedDimuons:
        RTYPE = dim.composition[:3]
        for QKEY in QUANTITIES:
            KEY = RTYPE+'-'+QKEY
            self.HISTS[KEY].Fill(QUANTITIES[QKEY]['LAMBDA'](dim), eventWeight)

        if self.SP is None and dim.LxySig() > 50.:
            if dim.composition == 'PAT':
                mu1, mu2 = PATmuons[dim.idx1], PATmuons[dim.idx2]

                for QKEY in MCQUANTITIES:
                    KEY = 'PAT-12-'+QKEY
                    F = MCQUANTITIES[QKEY]['LAMBDA']
                    if QKEY in ('hitsBeforeVtx', 'missingHitsAfterVtx'):
                        self.HISTS[KEY].Fill(F(dim.mu1), F(dim.mu2), eventWeight)
                    else:
                        self.HISTS[KEY].Fill(F(mu1), F(mu2), eventWeight)

                print '{:13s} {:d} {:7d} {:10d} ::: {:3s} {:2d} {:2d} ::: {:6.2f} {:2d} {:1d} {:1d} {:1d} {:1d} {:6.2f} {:2d} {:1d} {:1d} {:1d} {:1d} ::: {:9.4f} {:8.4f} {:10.2f} {:6.2f}'.format(
                        self.NAME, Event.run, Event.lumi, Event.event,
                        dim.composition[:3], dim.idx1, dim.idx2,
                        mu1.normChi2, mu1.nTrackerLayers, mu1.nPixelHits, int(mu1.highPurity), int(mu1.isGlobal), int(mu1.isMedium),
                        mu2.normChi2, mu2.nTrackerLayers, mu2.nPixelHits, int(mu2.highPurity), int(mu2.isGlobal), int(mu2.isMedium),
                        dim.LxySig(), dim.Lxy(), dim.normChi2, min(dim.mu1.d0Sig(),dim.mu2.d0Sig())
                )
            elif dim.composition == 'DSA':
                mu1, mu2 = DSAmuons[dim.idx1], DSAmuons[dim.idx2]
                print '{:13s} {:d} {:7d} {:10d} ::: {:3s} {:2d} {:2d} ::: {:6.2f} {:2s} {:1s} {:1s} {:1s} {:1s} {:6.2f} {:2s} {:1s} {:1s} {:1s} {:1s} ::: {:9.4f} {:8.4f} {:10.2f} {:6.2f}'.format(
                        self.NAME, Event.run, Event.lumi, Event.event,
                        dim.composition[:3], dim.idx1, dim.idx2,
                        mu1.normChi2, '-', '-', '-', '-', '-',
                        mu2.normChi2, '-', '-', '-', '-', '-',
                        dim.LxySig(), dim.Lxy(), dim.normChi2, min(dim.mu1.d0Sig(),dim.mu2.d0Sig())
                )
            else:
                mu1, mu2 = DSAmuons[dim.idx1], PATmuons[dim.idx2]
                print '{:13s} {:d} {:7d} {:10d} ::: {:3s} {:2d} {:2d} ::: {:6.2f} {:2s} {:1s} {:1s} {:1s} {:1s} {:6.2f} {:2d} {:1d} {:1d} {:1d} {:1d} ::: {:9.4f} {:8.4f} {:10.2f} {:6.2f}'.format(
                        self.NAME, Event.run, Event.lumi, Event.event,
                        dim.composition[:3], dim.idx1, dim.idx2,
                        mu1.normChi2, '-', '-', '-', '-', '-',
                        mu2.normChi2, mu2.nTrackerLayers, mu2.nPixelHits, int(mu2.highPurity), int(mu2.isGlobal), int(mu2.isMedium),
                        dim.LxySig(), dim.Lxy(), dim.normChi2, min(dim.mu1.d0Sig(),dim.mu2.d0Sig())
                )

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

            RTYPE = dim.composition[:3]
            KEY = 'GEN-Lxy-'+RTYPE
            self.HISTS[KEY].Fill(genMuon.Lxy(), eventWeight)

            KEY = RTYPE + '-' + 'LxyRes'
            self.HISTS[KEY].Fill(dim.Lxy()-genMuon.Lxy(), eventWeight)

            KEY = RTYPE + '-' + 'LxyRes' + 'VSGEN-Lxy'
            self.HISTS[KEY].Fill(genMuon.Lxy(), dim.Lxy()-genMuon.Lxy(), eventWeight)

            KEY = RTYPE + '-' + 'LxyPull'
            self.HISTS[KEY].Fill((dim.Lxy()-genMuon.Lxy())/dim.LxyErr(), eventWeight)

            KEY = RTYPE + '-' + 'LxyRes' + 'VS' + RTYPE + '-' + 'LxyErr'
            self.HISTS[KEY].Fill(dim.LxyErr(), dim.Lxy()-genMuon.Lxy(), eventWeight)

            if RTYPE != 'PAT': continue
            mu1, mu2 = PATmuons[dim.idx1], PATmuons[dim.idx2]
            for QKEY in MCQUANTITIES:
                KEY = RTYPE + '-' + '12' + '-' + QKEY
                F = MCQUANTITIES[QKEY]['LAMBDA']
                if QKEY in ('hitsBeforeVtx', 'missingHitsAfterVtx'):
                    self.HISTS[KEY].Fill(F(dim.mu1), F(dim.mu2), eventWeight)
                else:
                    self.HISTS[KEY].Fill(F(mu1), F(mu2), eventWeight)


# cleanup function for Analyzer class
def end(self, PARAMS=None):
    pass
    #if self.SP is not None:
    #    print '{:5s} {:4d} {:3d} {:4d}'.format('4Mu' if '4Mu' in self.NAME else '2Mu2J', self.SP.mH, self.SP.mX, self.SP.cTau),
    #else:
    #    print '{:s}'.format(self.NAME),

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
    #analyzer.writeHistograms('../analyzers/roots/ZephyrPlots{}{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else '', ARGS.CUTS))
    analyzer.writeHistograms('../analyzers/roots/mcbg/ZephyrPlots{}{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else '', ARGS.CUTS))
