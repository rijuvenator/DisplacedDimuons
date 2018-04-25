import FWCore.ParameterSet.Config as cms

##### Batch cmsRun from command line arguments
# get signal point as 3 numbers
import sys
import argparse
import DisplacedDimuons.Tupler.Utilities.dataHandler as DH

parser = argparse.ArgumentParser()
parser.add_argument('signalpoint', dest='SIGNALPOINT', type=int, nargs=3)
args = parser.parse_args(sys.argv[2:])
signalPoint = tuple(args.SIGNALPOINT)
HTo2XTo4MuSamples = DH.getHTo2XTo4MuSamples()
for data in HTo2XTo4MuSamples:
	if data.signalPoint() == signalPoint and data.process == 'AODSIM-ReHLT_V37-v1':
		INPUTFILES = data.getFiles(prefix=DH.ROOT_PREFIX)
		#OUTPUTFILE = '/afs/cern.ch/work/a/adasgupt/DisplacedDimuons/PATTuple_' + '_'.join(map(str,signalPoint)) + '.root'
		OUTPUTFILE = '/eos/cms/store/user/adasgupt/DisplacedDimuons/PATTuple_' + '_'.join(map(str,signalPoint)) + '.root'
		print '\n\nWill run over', len(INPUTFILES), 'files and attempt to create', OUTPUTFILE, '\n\n'
		break
else:
	print '\n\nNo sample found; exiting now\n\n'
	exit()
#####

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
	fileNames = cms.untracked.vstring(*INPUTFILES)
)

######################
##### PAT TUPLER #####
######################

# load process.out and process.outpath
process.load(MODULES+'Output_cfi')
process.out.fileName = cms.untracked.string(OUTPUTFILE)

# load patDefaultSequence
process.load(MODULES+'PATTupler_cfi')

# remove the OOT Photons tasks and modules
process.patCandidates.remove(process.patCandidateSummary)
process.patCandidatesTask.remove(process.makePatOOTPhotonsTask)
process.selectedPatCandidates.remove(process.selectedPatCandidateSummary)
process.selectedPatCandidatesTask.remove(process.selectedPatOOTPhotons)
process.cleanPatCandidates.remove(process.cleanPatCandidateSummary)

# enable PAT trigger paths
# switchOnTrigger expects an output module 'out'
from PhysicsTools.PatAlgos.tools.trigTools import switchOnTrigger
switchOnTrigger(process)

# load filter paths: hltPhysicsDeclaredFilter, primaryVertexFilter, METFilter
process.load(FILTERS+'goodData_cff')

# declare final path
process.PATTuplerPath = cms.Path(process.patDefaultSequence)

