import FWCore.ParameterSet.Config as cms

##### Batch cmsRun from command line arguments
# get signal point as 3 numbers
import sys, os, argparse
import DisplacedDimuons.Tupler.Utilities.dataHandler as DH
from DisplacedDimuons.Common.Constants import DIR_WS_RIJU, DIR_EOS_RIJU
from DisplacedDimuons.Common.Utilities import SPStr

parser = argparse.ArgumentParser()
parser.add_argument('signalpoint', dest='SIGNALPOINT', type=int, nargs=3)
args = parser.parse_args(sys.argv[2:])
signalPoint = tuple(args.SIGNALPOINT)
HTo2XTo4MuSamples = DH.getHTo2XTo4MuSamples()
for data in HTo2XTo4MuSamples:
	if data.signalPoint() == signalPoint:
	INPUTFILES = ['file:{}PAT_{}_{}.root'.format(DIR_EOS_RIJU, 'HTo2XTo4Mu', SPStr(signalPoint))]
	OUTPUTFILE = '{}ntuple_{}_{}.root'.format(DIR_WS_RIJU, 'HTo2XTo4Mu', SPStr(signalPoint))
	break
else:
	print '\n\nNo sample found; exiting now\n\n'
	exit()
#####

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
	fileNames = cms.untracked.vstring(*INPUTFILES)
)

##########################
##### SIMPLE NTUPLER #####
##########################

# load process.SimpleNTupler, the simple nTupler, and process.TFileService
process.load(MODULES+'SimpleNTupler_cfi')
process.TFileService.fileName = cms.string(OUTPUTFILE)

# add transient track builder
process.load("TrackingTools.TransientTrack.TransientTrackBuilder_cfi")
#process.load("Configuration.Geometry.GeometryIdeal_cff")
process.load("Configuration.Geometry.GeometryRecoDB_cff")
process.load("Configuration.StandardSequences.MagneticField_cff")
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
process.GlobalTag.globaltag = '92X_upgrade2017_realistic_v12'

# declare final path
process.nTuplerPath = cms.Path(process.SimpleNTupler)
