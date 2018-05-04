import FWCore.ParameterSet.Config as cms

TFileService = cms.Service('TFileService', fileName = cms.string('output_ntuple.root'))

# Assumes that this module is run on the output of PATFilter module.
SimpleNTupler = cms.EDAnalyzer('SimpleNTupler',
	cms.untracked.PSet(

####################
#### PARAMETERS ####
####################

		isMC           = cms.bool(True),

#######################
#### TRIGGER BLOCK ####
#######################
		triggerEvent   = cms.InputTag('patTriggerEvent'),
		prescales      = cms.InputTag('patTrigger', 'l1max', 'PAT'),

		# Versions to be checked for other data sets
		ddmHLTPaths    = cms.vstring(
			"HLT_L2DoubleMu28_NoVertex_2Cha_Angle2p5_Mass10_v4", # 2016D data
			"HLT_L2DoubleMu28_NoVertex_2Cha_Angle2p5_Mass10_v6"  # MC
		),
#		triggerResults = cms.InputTag('TriggerResults', '', 'PAT'), # this contains the results of "good data" filters
		triggerResults = cms.InputTag('TriggerResults', '', 'HLT'),

##############################
#### ANALYSIS COLLECTIONS ####
##############################

		patMet         = cms.InputTag('patMETs'),
		beamspot       = cms.InputTag('offlineBeamSpot'),
		vertices       = cms.InputTag('offlinePrimaryVertices'),
		muons          = cms.InputTag('cleanPatMuons'),
#		muons          = cms.InputTag('selectedPatMuons'),
		gens           = cms.InputTag('prunedGenParticles', '', 'PAT'),
#		gens           = cms.InputTag('genParticles'),
		GEIP           = cms.InputTag('generator'),
		dsaMuons       = cms.InputTag('displacedStandAloneMuons'),
		rsaMuons       = cms.InputTag('refittedStandAloneMuons'),
	)
)

# add transient track builder
from TrackingTools.TransientTrack.TransientTrackBuilder_cfi import *
# from Configuration.Geometry.GeometryIdeal_cff import *
from Configuration.Geometry.GeometryRecoDB_cff import *
from Configuration.StandardSequences.MagneticField_cff import *
from Configuration.StandardSequences.FrontierConditions_GlobalTag_cff import *
