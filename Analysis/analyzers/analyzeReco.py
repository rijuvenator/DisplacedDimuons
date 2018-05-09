import math
import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedMuons, pTRes

#### CLASS AND FUNCTION DEFINITIONS ####
# declare histograms for Analyzer class
def declareHistograms(self):
    # DSA and RSA specific plots
    # CONFIG stores the title and axis tuple so that the histograms can be declared in a loop
    CONFIG = {
            'pTRes'      : {'TITLE':';(*** p_{T} #minus gen p_{T})/gen p_{T};Counts', 'AXES':(1000,  -1., 3.  )},
            'pTEff'      : {'TITLE':';p_{T} [GeV];*** Match Efficiency'             , 'AXES':(1000,   0., 500.)},
            'LxyEff'     : {'TITLE':';L_{xy} [cm];*** Match Efficiency'             , 'AXES':(1000,   0., 500.)},
            'd0Dif'      : {'TITLE':';*** d_{0} #minus gen d_{0};Counts'            , 'AXES':(1000, -10., 10. )},
            'nMuon'      : {'TITLE':';*** Muon Multiplicity;Counts'                 , 'AXES':(11  ,   0., 11. )},
    }
    CONFIG['pTResVSLxy'] = {'TITLE':';L_{xy} [cm];*** p_{T} Res;Counts'             , 'AXES':(1000, 0., 10. , 1000, -1., 1.  )}
    CONFIG['pTResVSpT' ] = {'TITLE':';p_{T} [GeV];*** p_{T} Res;Counts'             , 'AXES':(1000, 0., 500., 1000, -1., 1.  )}
    CONFIG['pTResVSdR' ] = {'TITLE':';#DeltaR;*** p_{T} Res;Counts'                 , 'AXES':(1000, 0., 5.  , 1000, -1., 1.  )}
    CONFIG['pTVSpT'    ] = {'TITLE':';gen p_{T} [GeV];*** p_{T} [GeV];Counts'       , 'AXES':(1000, 0., 500., 1000,  0., 500.)}
    for MUON in ('DSA', 'RSA'):
        for KEY in CONFIG:
            self.HistInit(MUON+'_'+KEY, CONFIG[KEY]['TITLE'].replace('***',MUON), *CONFIG[KEY]['AXES'])

    # "extra" and denominator plots, can reuse the axes
    self.HistInit('ExtraPt'     , CONFIG['pTEff' ]['TITLE'].replace('*** ','') , *CONFIG['pTEff' ]['AXES'])
    self.HistInit('ExtraLxy'    , CONFIG['LxyEff']['TITLE'].replace('*** ','') , *CONFIG['LxyEff']['AXES'])

    self.HistInit('pTDen'       , ''                                           , *CONFIG['pTEff' ]['AXES'])
    self.HistInit('LxyDen'      , ''                                           , *CONFIG['LxyEff']['AXES'])

    # dimuon plots
    self.HistInit('Dim_vtxChi2' , ';vtx #chi^{2}/dof;Counts'                   , 1000,   0., 5.           )
    self.HistInit('Dim_deltaR'  , ';#DeltaR;Counts'                            , 1000,   0., 5.           )
    self.HistInit('Dim_mass'    , ';M(#mu#mu);Counts'                          , 1000,   0., self.SP.mX*2 )
    self.HistInit('Dim_deltaPhi', ';|#Delta#Phi|;Counts'                       , 1000,   0., math.pi      )
    self.HistInit('Dim_cosAlpha', ';cos(#alpha);Counts'                        , 1000,  -1., 1.           )

# internal loop function for Analyzer class
def analyze(self, E):
    mu11, mu12, mu21, mu22, X1, X2, H, P = E.getPrimitives('GEN')
    DSAmuons = E.getPrimitives('DSAMUON')
    RSAmuons = E.getPrimitives('RSAMUON')
    Dimuons  = E.getPrimitives('DIMUON' )

    DSASelections = [Selections.MuonSelection(muon) for muon in DSAmuons]
    RSASelections = [Selections.MuonSelection(muon) for muon in RSAmuons]

    nDSA, nRSA = 0, 0
    for sel in DSASelections:
        if sel.passesAcceptance():
            nDSA += 1
    for sel in RSASelections:
        if sel.passesAcceptance():
            nRSA += 1
    self.HISTS['DSA_nMuon'].Fill(nDSA)
    self.HISTS['RSA_nMuon'].Fill(nRSA)

    # loop over genMuons and fill histograms based on matches
    for genMuon in (mu11, mu12, mu21, mu22):
        # cut genMuons outside the detector acceptance
        genMuonSelection = Selections.MuonSelection(genMuon, cutList='MuonAcceptanceCutList')
        if not genMuonSelection: continue

        genMuonLxy = genMuon.Lxy()
        self.HISTS['LxyDen'].Fill(genMuonLxy)
        self.HISTS['pTDen' ].Fill(genMuon.pt)

        PREFIX = 'DSA'
        foundDSA = False
        for recoMuons in (DSAmuons, RSAmuons):
            matches = matchedMuons(genMuon, recoMuons)
            if len(matches) != 0:
                closestRecoMuon = recoMuons[matches[0]['idx']]
                if pTRes(closestRecoMuon, genMuon) < -0.5:
                    pass
                    #print 'GEN: {:9.4f} {:7.4f} {:7.4f}'.format(genMuon.pt, genMuon.eta, genMuon.phi)
                    #print '{}: {:9.4f} {:7.4f} {:7.4f}'.format(PREFIX, closestRecoMuon.pt, closestRecoMuon.eta, closestRecoMuon.phi)
                    #print ''
                self.HISTS[PREFIX+'_pTRes'     ].Fill(pTRes(closestRecoMuon, genMuon))
                self.HISTS[PREFIX+'_d0Dif'     ].Fill((closestRecoMuon.d0 - genMuon.d0))
                self.HISTS[PREFIX+'_LxyEff'    ].Fill(genMuonLxy)
                self.HISTS[PREFIX+'_pTEff'     ].Fill(genMuon.pt)
                self.HISTS[PREFIX+'_pTResVSLxy'].Fill(genMuonLxy,pTRes(closestRecoMuon, genMuon))
                self.HISTS[PREFIX+'_pTResVSpT' ].Fill(genMuon.pt,pTRes(closestRecoMuon, genMuon))
                self.HISTS[PREFIX+'_pTResVSdR' ].Fill(genMuon.pairDeltaR,pTRes(closestRecoMuon, genMuon))
                self.HISTS[PREFIX+'_pTVSpT'    ].Fill(genMuon.pt,closestRecoMuon.pt)

                if PREFIX == 'DSA':
                    foundDSA = True

                if PREFIX == 'RSA' and not foundDSA:
                    self.HISTS['ExtraLxy'].Fill(genMuonLxy)
                    self.HISTS['ExtraPt' ].Fill(genMuon.pt)
            PREFIX = 'RSA'

    for dimuon in Dimuons:
        if DSASelections[dimuon.idx1].passesAcceptance() and DSASelections[dimuon.idx2].passesAcceptance():
            self.HISTS['Dim_vtxChi2' ].Fill(dimuon.normChi2)
            self.HISTS['Dim_deltaR'  ].Fill(dimuon.deltaR  )
            self.HISTS['Dim_mass'    ].Fill(dimuon.mass    )
            self.HISTS['Dim_deltaPhi'].Fill(dimuon.deltaPhi)
            self.HISTS['Dim_cosAlpha'].Fill(dimuon.cosAlpha)
            #dimuonSelection = Selections.DimuonSelection(dimuon)

#### RUN ANALYSIS ####
if __name__ == '__main__':
    ARGS = Analyzer.PARSER.parse_args()
    for METHOD in ('declareHistograms', 'analyze'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])
    analyzer = Analyzer.Analyzer(
        NAME        = ARGS.NAME,
        SIGNALPOINT = Utilities.SignalPoint(ARGS.SIGNALPOINT),
        BRANCHKEYS  = ('GEN', 'DSAMUON', 'RSAMUON', 'DIMUON'),
        TEST        = ARGS.TEST,
        SPLITTING   = ARGS.SPLITTING
    )
    analyzer.writeHistograms('roots/RecoPlots_{}.root')
