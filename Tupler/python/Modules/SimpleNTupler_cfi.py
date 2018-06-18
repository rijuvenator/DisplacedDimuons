import FWCore.ParameterSet.Config as cms

TFileService = cms.Service('TFileService', fileName = cms.string('output_ntuple.root'))

# The SimpleNTupler may be run on a PAT Tuple, AOD, or GEN-SIM
# set the source in NTupler_cfg to PAT, AOD, or GEN as appropriate
SimpleNTupler = cms.EDAnalyzer('SimpleNTupler',
    cms.untracked.PSet(

####################
#### PARAMETERS ####
####################

        isMC           = cms.bool(True),
        isSignal       = cms.bool(True),
        finalState     = cms.string("4Mu"),
        source         = cms.string("PAT"),

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
        triggerResults = cms.InputTag('TriggerResults', '', 'HLT'),

##############################
#### ANALYSIS COLLECTIONS ####
##############################

        patMet         = cms.InputTag('patMETs'),
        filters        = cms.InputTag('TriggerResults', '', 'PAT'),
        beamspot       = cms.InputTag('offlineBeamSpot'),
        vertices       = cms.InputTag('offlinePrimaryVerticesWithBS'),
#       vertices       = cms.InputTag('offlinePrimaryVertices'),
        muons          = cms.InputTag('cleanPatMuons'),
        gens           = cms.InputTag('prunedGenParticles', '', 'PAT'),
        GEIP           = cms.InputTag('generator'),
        dsaMuons       = cms.InputTag('displacedStandAloneMuons', '', 'RECO'),
        rsaMuons       = cms.InputTag('refittedStandAloneMuons', '', 'RECO'),
    )
)

# add transient track builder
from TrackingTools.TransientTrack.TransientTrackBuilder_cfi import *
from Configuration.Geometry.GeometryRecoDB_cff import *
from Configuration.StandardSequences.MagneticField_cff import *
from Configuration.StandardSequences.FrontierConditions_GlobalTag_cff import *
