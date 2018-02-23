import FWCore.ParameterSet.Config as cms

from DisplacedDimuons.Tupler.main_PATTupler_cfg import process

process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(1))
process.MessageLogger.cerr.FwkReport.reportEvery = 1
process.out.fileName = cms.untracked.string('allBranches.root')
process.out.outputCommands = cms.untracked.vstring('keep *')
