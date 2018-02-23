import FWCore.ParameterSet.Config as cms

# parameters and constants
MAXEVENTS   = -1

# just to make the module declarations a bit cleaner
MODULES = 'DisplacedDimuons.Tupler.Modules.'

###############################
##### BASIC CONFIGURATION #####
###############################

# declare the cms.Process
process = cms.Process('NTUPLER')

# declare the maxEvents PSet
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(MAXEVENTS))

# load process.MessageLogger with reporting every 1000
process.load(MODULES+'MessageLogger_cfi')

# declare process.source
# Simple NTupler expects this to be a PAT Tupler created by main_PATTupler_cfg.py
process.source = cms.Source(
	'PoolSource',
	fileNames = cms.untracked.vstring('file:../ntuples/PATTuple.root')
)

##########################
##### SIMPLE NTUPLER #####
##########################

# load process.SimpleNTupler, the simple nTupler, and process.TFileService
process.load(MODULES+'SimpleNTupler_cfi')

# declare final path
process.nTuplerPath = cms.Path(process.SimpleNTupler)
