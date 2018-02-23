import FWCore.ParameterSet.Config as cms

process = cms.Process('PAT')

process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(-1))

process.load('FWCore.MessageService.MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = 1000

process.MessageLogger.categories.append('patCandidates|PATSummaryTables')

hacky = {'patCandidates|PATSummaryTables' : cms.untracked.PSet(limit = cms.untracked.int32(100000000))}

process.MessageLogger.cout = cms.untracked.PSet(
	threshold = cms.untracked.string('INFO'),
	default = cms.untracked.PSet(limit = cms.untracked.int32(0)),
	**hacky
)
