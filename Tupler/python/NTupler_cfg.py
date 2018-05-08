import FWCore.ParameterSet.Config as cms

#########################
##### CONFIGURATION #####
#########################

# Note: runNTupler.py will look for the first instance of
# ^PARAMETER\s+= and set values accordingly, so
# please don't add any similar lines above these 5
MAXEVENTS  = -1
INPUTFILES = []
PLUGIN     = 'SimpleNTupler'
OUTPUTFILE = 'test.root'
ISMC       = False

###############################
##### BASIC CONFIGURATION #####
###############################

# just to make the module declarations a bit cleaner
MODULES = 'DisplacedDimuons.Tupler.Modules.'

# declare the cms.Process
process = cms.Process('NTUPLER')

# declare the maxEvents PSet
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(MAXEVENTS))

# load process.MessageLogger with reporting every 1000
process.load(MODULES+'MessageLogger_cfi')

# declare process.source
# Simple NTupler expects this to be a PAT Tupler created by the PATFilter package
# GenOnly NTupler expects this to be an EDM file with genParticles and GenEventInfoProduct
process.source = cms.Source(
	'PoolSource',
	fileNames = cms.untracked.vstring(*INPUTFILES)
)

###################
##### NTUPLER #####
###################

# load process.SimpleNTupler, the simple nTupler, and process.TFileService, or
# load process.GenOnlyNTupler, the simple nTupler for Gen branches only, and process.TFileService
process.load(MODULES+PLUGIN+'_cfi')
process.TFileService.fileName = cms.string(OUTPUTFILE)

if PLUGIN == 'SimpleNTupler':
	process.GlobalTag.globaltag = '92X_upgrade2017_realistic_v12'
	process.SimpleNTupler.isMC = cms.bool(ISMC)

# declare final path
process.nTuplerPath = cms.Path(getattr(process, PLUGIN))
