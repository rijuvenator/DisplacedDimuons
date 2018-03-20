import FWCore.ParameterSet.Config as cms

out = cms.OutputModule('PoolOutputModule',
	fileName = cms.untracked.string('../ntuples/PATTuple.root'),
	SelectEvents = cms.untracked.PSet(SelectEvents = cms.vstring('*')),
	outputCommands = cms.untracked.vstring(
		'drop *',
		'keep *_TriggerResults_*_*',
		'keep *_offlineBeamSpot_*_*',
		'keep *_offlinePrimaryVertices_*_*',
		'keep GenEventInfoProduct_generator_*_*',
		'keep *_genParticles_*_*',
		'keep *_displacedStandAloneMuons_*_*',
		'keep *_refittedStandAloneMuons_*_*',
		'keep recoTracks_*_*_*',
		'keep recoTrackExtras_*_*_*',
		'keep *_selectedPatMuons_*_*',
	)
)

outpath = cms.EndPath(out)
