import FWCore.ParameterSet.Config as cms

# parameters and constants
MAXEVENTS   = -1
REPORTEVERY = 100

# just to make the module declarations a bit cleaner
MODULES = 'DisplacedDimuons.Tupler.Modules.'
FILTERS = 'DisplacedDimuons.Tupler.Filters.'

###############################
##### BASIC CONFIGURATION #####
###############################

# declare the cms.Process
process = cms.Process('PAT')

# declare the maxEvents PSet
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(MAXEVENTS))

# load process.MessageLogger with reporting every 1000
process.load(MODULES+'MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = REPORTEVERY

# declare process.source
# PAT Tupler expects this to be AOD
process.source = cms.Source('PoolSource',
	fileNames = cms.untracked.vstring('file:/afs/cern.ch/user/a/adasgupt/public/DD_AODReHLTv13v1_125_20_1300.root')
)

######################
##### PAT TUPLER #####
######################

# load process.out and process.outpath
process.load(MODULES+'Output_cfi')

# load process.PATTupler, the patDefaultSequence
process.load(MODULES+'PATTupler_cfi')

# enable PAT trigger paths
# switchOnTrigger expects an output module 'out'
from PhysicsTools.PatAlgos.tools.trigTools import switchOnTrigger
switchOnTrigger(process)

# load filter paths: hltPhysicsDeclaredFilter, primaryVertexFilter, METFilter
process.load(FILTERS+'goodData_cff')

# declare final path
process.PATTuplerPath = cms.Path(process.PATTupler)

