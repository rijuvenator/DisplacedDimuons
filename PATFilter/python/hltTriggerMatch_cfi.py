import FWCore.ParameterSet.Config as cms

muonTriggerMatchHLTMuons = cms.EDProducer('PATTriggerMatcherDRLessByR',
                                          src = cms.InputTag('cleanPatMuons'),
                                          matched = cms.InputTag('patTrigger'),
                                          matchedCuts = cms.string('type("TriggerMuon") && (path("HLT_L2DoubleMu28_NoVertex_2Cha_Angle2p5_Mass10*",1,0))'),
                                          maxDPtRel   = cms.double(1e6),
                                          maxDeltaR   = cms.double(0.2),
                                          resolveAmbiguities    = cms.bool(True),
                                          resolveByMatchQuality = cms.bool(True)
                                          )
