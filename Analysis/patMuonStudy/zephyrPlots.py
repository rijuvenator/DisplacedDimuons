import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedDimuons
import DisplacedDimuons.Analysis.Selector as Selector

DIMQUANTITIES = {
    'Lxy'     : {'LAMBDA': lambda dim: dim.Lxy()                     , 'PRETTY':'L_{xy} [cm]'               },
    'LxySig'  : {'LAMBDA': lambda dim: dim.LxySig()                  , 'PRETTY':'L_{xy}/#sigma_{L_{xy}}'    },
    'LxyErr'  : {'LAMBDA': lambda dim: dim.LxyErr()                  , 'PRETTY':'#sigma_{L_{xy}} [cm]'      },
    'vtxChi2' : {'LAMBDA': lambda dim: dim.normChi2                  , 'PRETTY':'vtx #chi^{2}/dof'          },
    'mass'    : {'LAMBDA': lambda dim: dim.mass                      , 'PRETTY':'M(#mu#mu) [GeV]'           },
    'deltaPhi': {'LAMBDA': lambda dim: dim.deltaPhi                  , 'PRETTY':'|#Delta#Phi|'              },
    'mind0Sig': {'LAMBDA': lambda m1, m2: min(m1.d0Sig(),m2.d0Sig()) , 'PRETTY':'min |d_{0}|/#sigma_{d_{0}}'},
}

DSAQUANTITIES = {
    'pT'       : {'LAMBDA': lambda mu: mu.pt                         , 'PRETTY':'p_{T} [GeV]'           },
    'eta'      : {'LAMBDA': lambda mu: mu.eta                        , 'PRETTY':'#eta'                  },
    'phi'      : {'LAMBDA': lambda mu: mu.phi                        , 'PRETTY':'#phi'                  },
    'FPTE'     : {'LAMBDA': lambda mu: mu.ptError/mu.pt              , 'PRETTY':'#sigma_{p_{T}}/p_{T}'  },
    'd0Sig'    : {'LAMBDA': lambda mu: mu.d0Sig()                    , 'PRETTY':'|d_{0}|/#sigma_{d_{0}}'},
    'trkChi2'  : {'LAMBDA': lambda mu: mu.normChi2                   , 'PRETTY':'trk #chi^{2}/dof'      },
    'nStations': {'LAMBDA': lambda mu: mu.nCSCStations+mu.nDTStations, 'PRETTY':'N(CSC+DT Stations)'    },
}

PATQUANTITIES = {
    'pT'        : {'LAMBDA': lambda mu: mu.pt             , 'PRETTY':'p_{T} [GeV]'           },
    'eta'       : {'LAMBDA': lambda mu: mu.eta            , 'PRETTY':'#eta'                  },
    'phi'       : {'LAMBDA': lambda mu: mu.phi            , 'PRETTY':'#phi'                  },
    'relTrkIso' : {'LAMBDA': lambda mu: mu.trackIso/mu.pt , 'PRETTY':'rel. track iso.'       },
    'd0Sig'     : {'LAMBDA': lambda mu: mu.d0Sig()        , 'PRETTY':'|d_{0}|/#sigma_{d_{0}}'},
    'trkChi2'   : {'LAMBDA': lambda mu: mu.normChi2       , 'PRETTY':'trk #chi^{2}/dof'      },
}

PI = R.TMath.Pi()

AXES = {
    'DSA' : {
        'Lxy'      : (1600,   0.  ,  800.   ), # 0.5  cm bins
        'LxySig'   : ( 100,   0.  ,   50.   ), # 0.5     bins
        'LxyErr'   : (1000,   0.  ,   50.   ), # 0.05 cm bins
        'vtxChi2'  : (1000,   0.  ,   50.   ), # 0.05    bins
        'mass'     : (1000,   0.  , 1000.   ), # 1   GeV bins
        'mind0Sig' : ( 500,   0.  ,   50.   ), # 0.1     bins
        'deltaPhi' : ( 100,   0.  ,   PI    ), # pi/100  bins
        'LxyRes'   : (1000, -50.  ,   50.   ), # 0.1  cm bins

        'pT'       : (1000,   0.  , 1000.   ), # 1 GeV   bins
        'eta'      : ( 600,  -3.  ,    3.   ), # 0.01    bins
        'phi'      : ( 200, -PI   ,   PI    ), # pi/100  bins
        'FPTE'     : (1000,   0.  ,    1.   ), # 1e-3    bins
        'd0Sig'    : ( 800,   0.  ,   80.   ), # 0.1     bins
        'trkChi2'  : ( 500,   0.  ,   50.   ), # 0.1     bins
        'nStations': (  15,   0.  ,   15.   ),
    },
    'PAT' : {
        'Lxy'      : ( 140,   0.  ,   70.   ),
        'LxySig'   : ( 500,   0.  ,  250.   ),
        'LxyErr'   : (1000,   0.  ,     .1  ), # 1e-4 cm bins
        'vtxChi2'  : (1000,   0.  ,   50.   ),
        'mass'     : (1000,   0.  , 1000.   ),
        'deltaPhi' : ( 100,   0.  ,   PI    ), # pi/100  bins
        'mind0Sig' : ( 500,   0.  ,   50.   ),
        'LxyRes'   : (1000,   -.05,     .05 ), # 1e-4 cm bins

        'pT'       : (1000,   0.  , 1000.   ),
        'eta'      : ( 600,  -3.  ,    3.   ),
        'phi'      : ( 200, -PI   ,   PI    ),
        'relTrkIso': (1000,   0.  ,     .5  ), # 5e-4    bins
        'd0Sig'    : (2000,   0.  ,  200.   ),
        'trkChi2'  : ( 500,   0.  ,   50.   ),
    },
    'HYB' : {
        'Lxy'      : ( 140,   0.  ,   70.   ),
        'LxySig'   : ( 300,   0.  ,  150.   ),
        'LxyErr'   : (1000,   0.  ,   25.   ), # 0.05 cm bins
        'vtxChi2'  : (1000,   0.  ,   50.   ),
        'mass'     : (1000,   0.  , 1000.   ),
        'deltaPhi' : ( 100,   0.  ,   PI    ), # pi/100  bins
        'mind0Sig' : ( 500,   0.  ,   50.   ),
        'LxyRes'   : (1000, -25.  ,   25.   ), # 0.05 cm bins
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
    for QKEY in DIMQUANTITIES:
        XTIT = DIMQUANTITIES[QKEY]['PRETTY']
        for RTYPE in ('DSA', 'PAT', 'HYB'):
            self.HistInit(RTYPE+'-'+QKEY, ';'+XTIT+';Counts', *AXES[RTYPE][QKEY])

    for QKEY in DSAQUANTITIES:
        XTIT = DSAQUANTITIES[QKEY]['PRETTY']
        for RTYPE in ('DSA',):
            self.HistInit(RTYPE+'-'+QKEY, ';'+XTIT+';Counts', *AXES[RTYPE][QKEY])

    for QKEY in PATQUANTITIES:
        XTIT = PATQUANTITIES[QKEY]['PRETTY']
        for RTYPE in ('PAT',):
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

    selectedDimuons, selectedDSAmuons, selectedPATmuons = Selector.SelectObjects(E, self.CUTS, Dimuons3, DSAmuons, PATmuons, self.ARGS.DSAPROXMATCH, self.ARGS.DSAVETOTRACKER)
    if selectedDimuons is None: return

    def getOriginalMuons(dim):
        if dim.composition == 'PAT':
            return PATmuons[dim.idx1], PATmuons[dim.idx2]
        elif dim.composition == 'DSA':
            return DSAmuons[dim.idx1], DSAmuons[dim.idx2]
        else:
            return DSAmuons[dim.idx1], PATmuons[dim.idx2]

    for dim in selectedDimuons:
        RTYPE = dim.composition[:3]
        for QKEY in DIMQUANTITIES:
            KEY = RTYPE+'-'+QKEY
            if QKEY != 'mind0Sig':
                self.HISTS[KEY].Fill(DIMQUANTITIES[QKEY]['LAMBDA'](dim), eventWeight)
            else:
                self.HISTS[KEY].Fill(DIMQUANTITIES[QKEY]['LAMBDA'](*getOriginalMuons(dim)), eventWeight,) # ew

        if RTYPE == 'DSA':
            for QKEY in DSAQUANTITIES:
                KEY = RTYPE+'-'+QKEY
                for mu in getOriginalMuons(dim):
                    self.HISTS[KEY].Fill(DSAQUANTITIES[QKEY]['LAMBDA'](mu), eventWeight)

        if RTYPE == 'PAT':
            for QKEY in PATQUANTITIES:
                KEY = RTYPE+'-'+QKEY
                for mu in getOriginalMuons(dim):
                    self.HISTS[KEY].Fill(PATQUANTITIES[QKEY]['LAMBDA'](mu), eventWeight)

        if RTYPE == 'HYB':
            DSAmu, PATmu = getOriginalMuons(dim)

            for QKEY in DSAQUANTITIES:
                KEY = 'DSA'+'-'+QKEY
                self.HISTS[KEY].Fill(DSAQUANTITIES[QKEY]['LAMBDA'](DSAmu), eventWeight)

            for QKEY in PATQUANTITIES:
                KEY = 'PAT'+'-'+QKEY
                self.HISTS[KEY].Fill(PATQUANTITIES[QKEY]['LAMBDA'](PATmu), eventWeight)

        if self.SP is None and dim.LxySig() > 20.:
            mu1, mu2 = getOriginalMuons(dim)
            if dim.composition == 'PAT':
                for QKEY in MCQUANTITIES:
                    KEY = 'PAT-12-'+QKEY
                    F = MCQUANTITIES[QKEY]['LAMBDA']
                    if QKEY in ('hitsBeforeVtx', 'missingHitsAfterVtx'):
                        self.HISTS[KEY].Fill(F(dim.mu1), F(dim.mu2), eventWeight)
                    else:
                        self.HISTS[KEY].Fill(F(mu1), F(mu2), eventWeight)

                print '{:13s} {:d} {:7d} {:10d} ::: {:3s} {:2d} {:2d} ::: {:6.2f} {:2d} {:1d} {:1d} {:1d} {:1d} {:6.2f} {:2d} {:1d} {:1d} {:1d} {:1d} ::: {:9.4f} {:8.4f} {:10.2f} {:6.2f} {:6.2f}'.format(
                        self.NAME, Event.run, Event.lumi, Event.event,
                        dim.composition[:3], dim.idx1, dim.idx2,
                        mu1.normChi2, mu1.nTrackerLayers, mu1.nPixelHits, int(mu1.highPurity), int(mu1.isGlobal), int(mu1.isMedium),
                        mu2.normChi2, mu2.nTrackerLayers, mu2.nPixelHits, int(mu2.highPurity), int(mu2.isGlobal), int(mu2.isMedium),
                        dim.LxySig(), dim.Lxy(), dim.normChi2, mu1.d0Sig(), mu2.d0Sig()
                )
            elif dim.composition == 'DSA':
                print '{:13s} {:d} {:7d} {:10d} ::: {:3s} {:2d} {:2d} ::: {:6.2f} {:2s} {:1s} {:1s} {:1s} {:1s} {:6.2f} {:2s} {:1s} {:1s} {:1s} {:1s} ::: {:9.4f} {:8.4f} {:10.2f} {:6.2f} {:6.2f}'.format(
                        self.NAME, Event.run, Event.lumi, Event.event,
                        dim.composition[:3], dim.idx1, dim.idx2,
                        mu1.normChi2, '-', '-', '-', '-', '-',
                        mu2.normChi2, '-', '-', '-', '-', '-',
                        dim.LxySig(), dim.Lxy(), dim.normChi2, mu1.d0Sig(), mu2.d0Sig()
                )
            else:
                print '{:13s} {:d} {:7d} {:10d} ::: {:3s} {:2d} {:2d} ::: {:6.2f} {:2s} {:1s} {:1s} {:1s} {:1s} {:6.2f} {:2d} {:1d} {:1d} {:1d} {:1d} ::: {:9.4f} {:8.4f} {:10.2f} {:6.2f} {:6.2f}'.format(
                        self.NAME, Event.run, Event.lumi, Event.event,
                        dim.composition[:3], dim.idx1, dim.idx2,
                        mu1.normChi2, '-', '-', '-', '-', '-',
                        mu2.normChi2, mu2.nTrackerLayers, mu2.nPixelHits, int(mu2.highPurity), int(mu2.isGlobal), int(mu2.isMedium),
                        dim.LxySig(), dim.Lxy(), dim.normChi2, mu1.d0Sig(), mu2.d0Sig()
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
    Analyzer.PARSER.add_argument('--dsaproxmatch', dest='DSAPROXMATCH', action='store_true')
    Analyzer.PARSER.add_argument('--dsavetotracker', dest='DSAVETOTRACKER', action='store_false')
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
