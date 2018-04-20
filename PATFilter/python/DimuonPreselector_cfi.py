import FWCore.ParameterSet.Config as cms

dimuonPreselector = cms.EDFilter("DimuonPreselector",
                                 dsa_src = cms.InputTag("displacedStandAloneMuons"),
                                 dgl_src = cms.InputTag("displacedGlobalMuons"),
                                 min_pt1_dsa = cms.double(10.),
                                 min_pt2_dsa = cms.double(10.),
                                 min_pt1_dgl = cms.double(10.),
                                 min_pt2_dgl = cms.double(10.),
                                 filter_on_DSAMuons = cms.bool(True),
                                 filter_on_DGLMuons = cms.bool(True)
                                 )
