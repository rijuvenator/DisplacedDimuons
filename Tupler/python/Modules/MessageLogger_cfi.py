import FWCore.ParameterSet.Config as cms

from FWCore.MessageService.MessageLogger_cfi import MessageLogger

MessageLogger.cerr.FwkReport.reportEvery = 1000

MessageLogger.categories.append('TSCPBuilderNoMaterial')
MessageLogger.cerr.TSCPBuilderNoMaterial = cms.untracked.PSet(limit = cms.untracked.int32(10))
