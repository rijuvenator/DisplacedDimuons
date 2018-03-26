import FWCore.ParameterSet.Config as cms

##### Batch cmsRun from command line arguments
# get signal point as 3 numbers
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('mH'  , type=int)
parser.add_argument('mX'  , type=int)
parser.add_argument('cTau', type=int)
args = parser.parse_args(sys.argv[2:])
signalPoint = (args.mH, args.mX, args.cTau)
DIR_WS = '/afs/cern.ch/work/a/adasgupt/DisplacedDimuons/'
DIR_EOS = '/eos/cms/store/user/adasgupt/DisplacedDimuons/'
INPUTFILES = ['file:' + DIR_EOS + 'PATTuple_' + '_'.join(map(str,signalPoint)) + '.root']
#OUTPUTFILE = DIR_WS + 'simple_ntuple_' + '_'.join(map(str,signalPoint)) + '.root'
OUTPUTFILE = './simple_ntuple_' + '_'.join(map(str,signalPoint)) + '.root'
#####

# parameters and constants
MAXEVENTS   = 10

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
process.load("TrackingTools/TransientTrack/TransientTrackBuilder_cfi")
process.load("Configuration.Geometry.GeometryIdeal_cff")
process.load("Configuration.StandardSequences.MagneticField_cff")
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
process.GlobalTag.globaltag = 'auto:run2_mc'

# declare final path
process.nTuplerPath = cms.Path(process.SimpleNTupler)
