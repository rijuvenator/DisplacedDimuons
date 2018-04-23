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
H2X4Mdata = DH.get_H2X4M_Datasets()
for data in H2X4Mdata:
	if data.signalPoint() == signalPoint and data.process == 'GS-v2':
		INPUTFILES = data.getFiles(prefix=DH.ROOT_PREFIX)
		OUTPUTFILE = '/afs/cern.ch/work/a/adasgupt/DisplacedDimuons/genOnly_ntuple_' + '_'.join(map(str,signalPoint)) + '.root'
		print '\n\nWill run over', len(INPUTFILES), 'files and attempt to create', OUTPUTFILE, '\n\n'
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
# Gen Only NTupler expects this to be an EDM file with genParticles and GenEventInfoProduct
process.source = cms.Source(
	'PoolSource',
	fileNames = cms.untracked.vstring(*INPUTFILES)
)

############################
##### GEN ONLY NTUPLER #####
############################

# load process.GenOnlyNTupler, the simple nTupler for Gen branches only, and process.TFileService
process.load(MODULES+'GenOnlyNTupler_cfi')
process.TFileService.fileName = cms.string(OUTPUTFILE)

# declare final path
process.nTuplerPath = cms.Path(process.GenOnlyNTupler)
