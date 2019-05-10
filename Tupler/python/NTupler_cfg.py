import FWCore.ParameterSet.Config as cms

#########################
##### CONFIGURATION #####
#########################

# Note: runNTupler.py will look for the first instance of
# ^PARAMETER\s+= and set values accordingly, so
# please don't add any similar lines above these 8
MAXEVENTS  = -1
INPUTFILES = ['file:/eos/cms/store/user/valuev/DisplacedDimuons/PATFilter/MC2016_Hto2Xto2mu2j_1000_150_1000_07May19.root']
OUTPUTFILE = 'test.root'
ISMC       = False
ISSIGNAL   = False
FINALSTATE = '4Mu'
GENS_TAG   = ('prunedGenParticles', '', 'PAT')
SOURCE     = 'PAT'

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
# if source == PAT, this should be a PAT Tuple created by the PATFilter package
# if source == AOD, this should be an EDM file marked AOD; the PAT collections will not be filled
# if source == GEN, this should be an EDM file with genParticles and GenEventInfoProduct
process.source = cms.Source(
    'PoolSource',
    fileNames = cms.untracked.vstring(*INPUTFILES)
)

###################
##### NTUPLER #####
###################

# load process.SimpleNTupler, the simple nTupler, and process.TFileService
process.load(MODULES+'SimpleNTupler_cfi')
process.TFileService.fileName = cms.string(OUTPUTFILE)

process.SimpleNTupler.isMC       = cms.bool(ISMC)
process.SimpleNTupler.isSignal   = cms.bool(ISSIGNAL)
process.SimpleNTupler.finalState = cms.string(FINALSTATE)
process.SimpleNTupler.gens       = cms.InputTag(*GENS_TAG)
process.SimpleNTupler.source     = cms.string(SOURCE)

if process.SimpleNTupler.isMC:
    # RunIISummer16DR80Premix (aka "Moriond17") campaign, CMSSW_8_0_X
    process.GlobalTag.globaltag = '80X_mcRun2_asymptotic_2016_TrancheIV_v6'
    # CMSSW_9_2_X
    # process.GlobalTag.globaltag = '92X_upgrade2017_realistic_v12'
else:
    # 2016 data
    process.GlobalTag.globaltag = '80X_dataRun2_2016LegacyRepro_v4'

# declare final path
process.nTuplerPath = cms.Path(process.SimpleNTupler)
