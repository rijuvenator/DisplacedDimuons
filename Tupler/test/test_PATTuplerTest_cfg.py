import FWCore.ParameterSet.Config as cms

process = cms.Process('PAT')
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(-1))

process.load('FWCore.MessageService.MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = 100

process.source = cms.Source('PoolSource',
	fileNames = cms.untracked.vstring('/store/mc/RunIISummer17DRStdmix/ZToMuMu_NNPDF30_13TeV-powheg_M_120_200/AODSIM/NZSFlatPU28to62_92X_upgrade2017_realistic_v10-v1/150000/EC9BB6BB-76AA-E711-B691-0CC47A4C8E56.root')
)

process.load('Configuration.Geometry.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:run2_mc')

process.load('PhysicsTools.PatAlgos.patSequences_cff')

process.patDefaultPath = cms.Path(process.patDefaultSequence)

process.patCandidates.remove(process.patCandidateSummary)
process.patCandidatesTask.remove(process.makePatOOTPhotonsTask)
process.selectedPatCandidates.remove(process.selectedPatCandidateSummary)
process.selectedPatCandidatesTask.remove(process.selectedPatOOTPhotons)
process.cleanPatCandidates.remove(process.cleanPatCandidateSummary)

process.out = cms.OutputModule('PoolOutputModule',
	fileName = cms.untracked.string('PATTupleTest.root'),
	SelectEvents = cms.untracked.PSet(SelectEvents = cms.vstring('*')),
	outputCommands = cms.untracked.vstring(
		'drop *',
		'keep *_TriggerResults_*_*',
		'keep *_offlineBeamSpot_*_*',
		'keep *_offlinePrimaryVertices_*_*',
		'keep GenEventInfoProduct_generator_*_*',
		'keep *_genParticles_*_*',
		'keep *_displacedStandAloneMuons_*_*',
		'keep *_selectedPatMuons_*_*',
	)
)
process.outpath = cms.EndPath(process.out)

from PhysicsTools.PatAlgos.tools.trigTools import switchOnTrigger
switchOnTrigger(process)


