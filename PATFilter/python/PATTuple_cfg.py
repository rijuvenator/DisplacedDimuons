#!/usr/bin/env python

import FWCore.ParameterSet.Config as cms

process = cms.Process('PAT')
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(-1))
# Print tables of the results of module/path execution and timing info.
process.options = cms.untracked.PSet(wantSummary = cms.untracked.bool(True))
process.source = cms.Source('PoolSource',
                            fileNames = cms.untracked.vstring('file:PlaceHolder.root'))

# Load services needed to run the PAT.
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag.globaltag = cms.string('auto:run2_mc')

# Configure the MessageLogger ~sanely. Also direct it to let the PAT
# summary tables be reported -- nice to see how many events had no
# muons, how many had no "selected"/"clean" muons, etc.
process.load('FWCore.MessageLogger.MessageLogger_cfi')
# Make MessageLogger print a message every Nth event with (run, lumi,
# event) numbers.
process.MessageLogger.cerr.FwkReport.reportEvery = 5000
#process.MessageLogger.cerr.FwkReport.reportEvery = 1
process.MessageLogger.cerr.threshold = 'INFO'
process.MessageLogger.categories.append('PATSummaryTables')
process.MessageLogger.cerr.PATSummaryTables = cms.untracked.PSet(limit = cms.untracked.int32(-1))

# Run in "uncheduled" mode (default starting from CMSSW_9_1_X)
process.options.allowUnscheduled = cms.untracked.bool(True)

# Default PAT sequence
process.load('PhysicsTools.PatAlgos.patSequences_cff')
process.p = cms.Path(process.patDefaultSequence)

# Define the output file with the output commands defining the
# branches we want to have in our PAT tuple.
process.out = cms.OutputModule(
    'PoolOutputModule',
    fileName = cms.untracked.string('pat.root'),
    # If your path in your top-level config is not called 'p', you'll need
    # to change the next line.
    SelectEvents   = cms.untracked.PSet(SelectEvents = cms.vstring('p')),
    outputCommands = cms.untracked.vstring(
        'drop *',
        'keep *_displacedStandAloneMuons_*_*',
        'keep *_displacedGlobalMuons_*_*',
        'keep *_displacedTracks_*_*',
        'keep *_refittedStandAloneMuons_*_*',
        'drop *_refittedStandAloneMuons_UpdatedAtVtx_*',
#- needed for PV refit
#        'keep recoTracks_generalTracks*_*_*',
#- if decide to drop TrackExtras and TrackingRecHits collections
#        'keep recoTracks_displacedStandAloneMuons_*_*',
#        'keep recoTracks_displacedGlobalMuons_*_*',
#        'keep recoTracks_displacedTracks_*_*',
#        'keep recoTracks_refittedStandAloneMuons_*_*',
#        'drop recoTracks_refittedStandAloneMuons_UpdatedAtVtx_*',
        'keep patMuons_cleanPatMuons__*',
        'keep patMETs_patMETs__PAT',
#        'keep recoGenParticles_*_*_SIM',               # full genParticles collection
        'keep recoGenParticles_prunedGenParticles_*_*', # genParticles after pruning
        'keep GenEventInfoProduct_*_*_*',
        'keep *_offlineBeamSpot_*_*',
        'keep *_offlinePrimaryVertices_*_*',
        'keep *_offlinePrimaryVerticesWithBS_*_*',      # w/ BS contraint in the vtx fit
        'keep edmTriggerResults_TriggerResults__HLT*',
##        'keep L1GlobalTriggerObjectMaps_l1L1GtObjectMap_*_*', # no longer exists
#        'keep L1GlobalTriggerReadoutRecord_gtDigis__RECO', # superseded by pat::Trigger
#        'keep *_hltTriggerSummaryAOD__HLT*',               # superseded by pat::Trigger
        'keep edmTriggerResults_TriggerResults__PAT',   # for post-tuple filtering on the goodData paths
        'keep PileupSummaryInfos_addPileupInfo_*_*',    # needed for pile-up reweighting?
#        'keep *_cleanPatMuonsTriggerMatch_*_*',        # if embed trigger match
        'keep *_patTrigger_*_*', 
        'keep *_patTriggerEvent_*_*'
        )
)

# PAT muons 
# Embed the tracker tracks (by default, every other track is already
# embedded).
process.patMuons.embedTrack = True

# Drop out-of-time photons, which break PAT (for CMSSW_9_2_X)
# process.patCandidatesTask.remove(process.makePatOOTPhotonsTask)
# process.selectedPatCandidatesTask.remove(process.selectedPatOOTPhotons)

# PAT trigger info
process.load('DisplacedDimuons.PATFilter.hltTriggerMatch_cfi')
from PhysicsTools.PatAlgos.tools.trigTools import switchOnTrigger, switchOnTriggerMatchEmbedding
switchOnTrigger(process, outputModule = '')
# matching is probably useless for us since it works only for PAT objects
# switchOnTriggerMatchEmbedding(process,
#                               triggerProducer = 'patTrigger', # this is already the default setting
#                               triggerMatchers = [ 'muonTriggerMatchHLTMuons' ],
#                               outputModule = ''
#                               )
# This line is only needed in the "scheduled" mode
# process.patDefaultSequence = cms.Sequence(process.patDefaultSequence._seq * process.patTrigger * process.patTriggerEvent)
# Input for cleanPatMuonsTriggerMatch not found; not sure why
# process.patDefaultSequence = cms.Sequence(process.patDefaultSequence._seq * process.patTrigger * process.patTriggerEvent * process.cleanPatMuonsTriggerMatch)
# Possible alternative to the above: standalone trigger objects.  Saves ~20 kB/event in data.
# from PhysicsTools.PatAlgos.tools.trigTools import switchOnTriggerStandAlone
# switchOnTriggerStandAlone(process, outputModule = '')
# process.patDefaultSequence = cms.Sequence(process.patDefaultSequence._seq * process.patTrigger)

# PAT MET
# Type-1-corrected MET is the PAT default in CMSSW_8_0_X, so this part below is not needed
# from PhysicsTools.PatAlgos.tools.metTools import addMETCollection 
# addMETCollection(process, labelName='patMETsPF', metSource='pfMetT1')
# Again this is only needed in the "scheduled" mode
# process.patDefaultSequence = cms.Sequence(process.patDefaultSequence._seq * process.patMETsPF)

# MET filters, see https://twiki.cern.ch/twiki/bin/view/CMS/MissingETOptionalFiltersRun2
process.load("PhysicsTools.PatAlgos.slimming.metFilterPaths_cff")
process.goodDataHBHENoiseFilter           = cms.Path(process.HBHENoiseFilter)
process.goodDataHBHEIsoNoiseFilter        = cms.Path(process.HBHENoiseIsoFilter)
process.goodDataCSCTightHaloFilter        = cms.Path(process.globalTightHalo2016Filter)
process.goodDataEcalTPFilter              = cms.Path(process.EcalDeadCellTriggerPrimitiveFilter)
process.goodDataEeBadScFilter             = cms.Path(process.eeBadScFilter)             # not recommended for MC, check later
process.goodDataBadPFMuonFilter           = cms.Path(process.BadPFMuonFilter)           # new, to be checked
process.goodDataBadChargedCandidateFilter = cms.Path(process.BadChargedCandidateFilter) # new, to be checked

# We want just to tag the event: define a path
process.goodDataMETFilter = cms.Path(process.HBHENoiseFilter *
                                     process.HBHENoiseIsoFilter *  
                                     process.globalTightHalo2016Filter * 
                                     process.EcalDeadCellTriggerPrimitiveFilter * 
                                     process.eeBadScFilter *
                                     process.BadPFMuonFilter *
                                     process.BadChargedCandidateFilter
                                     )

process.load('DisplacedDimuons.PATFilter.goodData_cff')
process.goodDataHLTPhysicsDeclared = cms.Path(process.hltPhysicsDeclared)
process.goodDataPrimaryVertexFilter = cms.Path(process.primaryVertex)
process.goodDataAll = cms.Path(process.hltPhysicsDeclared * process.primaryVertex)

process.outpath = cms.EndPath(process.out) 
