import FWCore.ParameterSet.Config as cms

#########################
##### CONFIGURATION #####
#########################

import DisplacedDimuons.Tupler.Utilities.CFGParser as CFGParser
CONFIG = CFGParser.getConfiguration()

###############################
##### BASIC CONFIGURATION #####
###############################

# just to make the module declarations a bit cleaner
MODULES = 'DisplacedDimuons.Tupler.Modules.'

# declare the cms.Process
process = cms.Process('NTUPLER')

# declare the maxEvents PSet
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(CONFIG.MAXEVENTS))

# load process.MessageLogger with reporting every 1000
process.load(MODULES+'MessageLogger_cfi')

# declare process.source
# Simple NTupler expects this to be a PAT Tupler created by the PATFilter package
# GenOnly NTupler expects this to be an EDM file with genParticles and GenEventInfoProduct
process.source = cms.Source(
	'PoolSource',
	fileNames = cms.untracked.vstring(*CONFIG.INPUTFILES)
)

###################
##### NTUPLER #####
###################

# load process.SimpleNTupler, the simple nTupler, and process.TFileService, or
# load process.GenOnlyNTupler, the simple nTupler for Gen branches only, and process.TFileService
process.load(MODULES+CONFIG.PLUGIN+'_cfi')
process.TFileService.fileName = cms.string(CONFIG.OUTPUTFILE)

if CONFIG.PLUGIN == 'SimpleNTupler':
	process.GlobalTag.globaltag = '92X_upgrade2017_realistic_v12'

# declare final path
process.nTuplerPath = cms.Path(getattr(process, CONFIG.PLUGIN))
