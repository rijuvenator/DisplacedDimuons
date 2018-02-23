import FWCore.ParameterSet.Config as cms

TFileService = cms.Service('TFileService', fileName = cms.string('output_ntuple.root'))

SimpleNTupler = cms.EDAnalyzer('SimpleNTupler',
	cms.untracked.PSet(
		triggerResults = cms.InputTag('TriggerResults', '', 'PAT'),
		beamspot = cms.InputTag('offlineBeamSpot'),
		vertices = cms.InputTag('offlinePrimaryVertices'),
		muons = cms.InputTag('selectedPatMuons'),
		gens = cms.InputTag('genParticles'),
		GEIP = cms.InputTag('generator'),
	)
)
