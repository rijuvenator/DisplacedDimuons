import sys, os, argparse
import DisplacedDimuons.Tupler.Utilities.dataHandler as DH
from DisplacedDimuons.Common.Constants import DIR_WS_RIJU, DIR_PAT
from DisplacedDimuons.Common.Utilities import SPStr

DEFAULT_SP          = (125, 20, 13)
DEFAULT_AOD_PROCESS = 'AODSIM-ReHLT_V37-v1'
DEFAULT_GEN_PROCESS = 'GS-v2'
DEFAULT_OUTDIR      = DIR_WS_RIJU
DEFAULT_OUTFILE     = 'output.root'

FILE_PATTERNS = {
	'SIGNAL_PAT'    : 'PAT_{}_{}.root',
	'SIGNAL_NTUPLE' : 'ntuple_{}_{}.root',
	'SIGNAL_GENONLY': 'gen_ntuple_{}_{}.root',
	'BG_PAT'        : 'PAT_{}.root',
	'BG_NTUPLE'     : 'ntuple_{}.root',
	'BG_GENONLY'    : 'gen_ntuple_{}.root',
}

def getConfiguration(returnArgs=False):
	parser = argparse.ArgumentParser()

	# name       : the name of the sample, as defined by the dataHandler, e.g. HTo2XTo4Mu or DY400to500 
	# signalpoint: three integers defining the HTo2XTo4Mu signal point, e.g. 125 20 13
	# genonly    : whether or not to only run the Gen part of the nTuple, e.g. for GEN-SIM
	# test       : whether or not to run in test mode: restrict max events to 1000 (or as specified), create the output locally, etc
	# maxevents  : maximum events, will be used only if the TEST option is specified
	# outdir     : output directory. Common paths should be stored in DisplacedDimuons.Common.Constants
	# outfile    : output file pattern. Can contain {} for later .format use
	# verbose    : print debug info

	parser.add_argument('NAME'         ,                                                            help='sample name'                            )
	parser.add_argument('--signalpoint', dest='SIGNALPOINT', type=int, nargs=3, default=DEFAULT_SP, help='3 ints defining HTo2XTo4Mu signal point')
	parser.add_argument('--genonly'    , dest='GENONLY'    , action='store_true',                   help='run gen only'                           )
	parser.add_argument('--test'       , dest='TEST'       , action='store_true',                   help='run in test mode'                       )
	parser.add_argument('--maxevents'  , dest='MAXEVENTS'  , type=int, default=1000,                help='max events'                             )
	parser.add_argument('--outdir'     , dest='OUTDIR'     , default=DEFAULT_OUTDIR,                help='output directory'                       )
	parser.add_argument('--outfile'    , dest='OUTFILE'    , default=DEFAULT_OUTFILE,               help='output file pattern'                    )
	parser.add_argument('--verbose'    , dest='VERBOSE'    , action='store_true',                   help='print debug info'                       )

	# this is expected to be used only for cmsRun files, for which sys.argv is
	# ['cmsRun', 'Config_cfg.py', 'arg1', 'arg2' ... ]
	# cmsRun doesn't like options, with --
	# So I will indicate options with # and replace them manually
	# So, the list to be parsed is sys.argv[2:], and as follows:

	args = parser.parse_args([s.replace('#', '--') for s in sys.argv[2:]])

	# now we can get the particular Dataset object
	data = findSample(args)

	# define input and output files
	if data.isSignal:
		outKey = 'SIGNAL_'
	else:
		outKey = 'BG_'
	if args.GENONLY:
		outKey += 'GENONLY'
	else:
		outKey += 'NTUPLE'
	OUTPUTFILE =  os.path.join(args.OUTDIR, FILE_PATTERNS[outKey].format(args.NAME, SPStr(args.SIGNALPOINT)))

	if args.GENONLY:
		INPUTFILES = data.getFiles(prefix=DH.ROOT_PREFIX)
	else:
		if data.isSignal:
			inKey = 'SIGNAL_PAT'
		else:
			inKey = 'BG_PAT'
		INPUTFILES = [os.path.join(DIR_PAT, FILE_PATTERNS[inKey].format(args.NAME, SPStr(args.SIGNALPOINT)))]

	# make sure input files have the right protocol
	if ':' not in INPUTFILES[0]:
		for i, f in enumerate(INPUTFILES):
			INPUTFILES[i] = 'file:' + INPUTFILES[i]

	# disregard if we're testing
	if args.TEST:
		OUTPUTFILE = './test.root'
	
	# create final configuration namespace and return
	CONFIG            = argparse.Namespace()
	CONFIG.NAME       = args.NAME
	CONFIG.TEST       = args.TEST
	CONFIG.MAXEVENTS  = -1 if not args.TEST else args.MAXEVENTS
	CONFIG.OUTPUTFILE = OUTPUTFILE
	CONFIG.INPUTFILES = INPUTFILES
	CONFIG.DATA       = data
	CONFIG.PLUGIN     = 'SimpleNTupler' if not args.GENONLY else 'GenOnlyNTupler'

	if args.VERBOSE:
		print 'ARGS:', args
		print 'CONFIG:', CONFIG

	if not returnArgs:
		return CONFIG
	else:
		return CONFIG, args

def findSample(args):
	# get the list of samples and the Dataset object associated with the parameters
	if args.NAME == 'HTo2XTo4Mu':
		SIGNALPOINT = tuple(args.SIGNALPOINT)
		samples = DH.getHTo2XTo4MuSamples()
		DP = DEFAULT_AOD_PROCESS if not args.GENONLY else DEFAULT_GEN_PROCESS
		for data in samples:
			if data.signalPoint() == SIGNALPOINT and data.process == DP:
				return data
	else:
		samples = DH.getBackgroundSamples()
		for data in samples:
			if data.name == args.NAME:
				return data
