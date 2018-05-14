import sys, os, argparse
import DisplacedDimuons.Tupler.Utilities.dataHandler as DH
from DisplacedDimuons.Common.Utilities import SPStr

# various default parameters; only change if necessary
# (prefer to specify the parameters externally with the parser)
# in particular the AOD process and GEN process don't have CLI parameters
# so change them here if they're supposed to be different
DEFAULT_SP          = (125, 20, 13)
DEFAULT_AOD_PROCESS = 'AODSIM-ReHLT_V37-v1'
DEFAULT_GEN_PROCESS = 'GS-v2'
DEFAULT_OUTDIR      = ''
DEFAULT_OUTFILE     = 'ntuple_{}.root'

# cmsRun configuration and submission parser
# expected syntax: python runNTupler.py [NAME] [OPTIONS]
# full command line access to most common parameters, more can be added as necessary
# returns a CONFIG Namespace with all the relevant parameters, for use
# in the cmsRun config, in batch scripts, in CRAB config files, and so on
# uses the full dataHandler apparatus
def getConfiguration(returnArgs=False):
	parser = argparse.ArgumentParser()

	# name       : the name of the sample, as defined by the dataHandler, e.g. HTo2XTo4Mu or DY400to500 
	# signalpoint: three integers defining the HTo2XTo4Mu signal point, e.g. 125 20 13
	# genonly    : whether or not to only run the Gen part of the nTuple, e.g. for GEN-SIM
	# outdir     : output directory. Common paths should be stored in DisplacedDimuons.Common.Constants
	# outfile    : output file pattern. Can contain {} for later .format use
	# crab       : submit to crab
	# batch      : submit to lxbatch
	# test       : whether or not to run in test mode: restrict max events to 1000 (or as specified), create the output locally, etc
	# maxevents  : maximum events, will be used only if the TEST option is specified
	# verbose    : print debug info
	# nosubmit   : don't actually submit the job, whether it's crab, lxbatch, or local. useful with verbose if just testing.

	parser.add_argument('NAME'         ,                                                            help='sample name'                            )
	parser.add_argument('--signalpoint', dest='SIGNALPOINT', type=int, nargs=3, default=DEFAULT_SP, help='3 ints defining HTo2XTo4Mu signal point')
	parser.add_argument('--genonly'    , dest='GENONLY'    , action='store_true',                   help='run gen only'                           )
	parser.add_argument('--outdir'     , dest='OUTDIR'     , default=DEFAULT_OUTDIR,                help='output directory'                       )
	parser.add_argument('--outfile'    , dest='OUTFILE'    , default=DEFAULT_OUTFILE,               help='output file pattern'                    )
	parser.add_argument('--crab'       , dest='CRAB'       , action='store_true',                   help='submit to CRAB'                         )
	parser.add_argument('--batch'      , dest='BATCH'      , action='store_true',                   help='submit to LXBATCH'                      )
	parser.add_argument('--test'       , dest='TEST'       , action='store_true',                   help='run in test mode'                       )
	parser.add_argument('--maxevents'  , dest='MAXEVENTS'  , type=int, default=1000,                help='max events'                             )
	parser.add_argument('--verbose'    , dest='VERBOSE'    , action='store_true',                   help='print debug info'                       )
	parser.add_argument('--nosubmit'   , dest='SUBMIT'     , action='store_false',                  help='don\'t actually submit job'             )

	# this is expected to be run from an external script, for which sys.argv is
	# ['run.py', 'arg1', 'arg2' ... ]
	# So run as usual on sys.argv[1:]
	args = parser.parse_args(sys.argv[1:])

	# make sure only one of --crab, --batch, and --test are set
	if (args.CRAB, args.BATCH, args.TEST).count(True) > 1:
		raise Exception('Only one of --crab, --batch, or --test may be set')

	# now we can get the particular Dataset object
	data = findSample(args)

	# if GENONLY, use the "AOD" dataset (i.e. the parent EDM, in this case GEN-SIM)
	DATASET = 'AOD' if args.GENONLY else None

	# set input and output files according to mode: crab, batch, test, or none (local)
	if args.CRAB:
		INPUTFILES = ['file:dummy.root']
		OUTPUTFILE = args.OUTFILE.format(data.name)
	elif args.BATCH:
		INPUTFILES = data.getFiles(prefix=DH.ROOT_PREFIX, dataset=DATASET)
		OUTPUTFILE = os.path.join(args.OUTDIR, args.OUTFILE.format(data.name))
	elif args.TEST:
		INPUTFILES = data.getFiles(prefix=DH.ROOT_PREFIX, dataset=DATASET)[0:1]
		OUTPUTFILE = './test.root'
	else:
		INPUTFILES = data.getFiles(prefix=DH.ROOT_PREFIX, dataset=DATASET)
		OUTPUTFILE = os.path.join(args.OUTDIR, args.OUTFILE.format(data.name))
	
	# create final configuration namespace and return
	CONFIG            = argparse.Namespace()
	for attr in ('NAME', 'TEST', 'CRAB', 'BATCH', 'VERBOSE', 'SUBMIT'):
		setattr(CONFIG, attr, getattr(args, attr))
	CONFIG.MAXEVENTS  = -1 if not args.TEST else args.MAXEVENTS
	CONFIG.OUTPUTFILE = OUTPUTFILE
	CONFIG.INPUTFILES = INPUTFILES
	CONFIG.DATA       = data
	CONFIG.PLUGIN     = 'SimpleNTupler' if not args.GENONLY else 'GenOnlyNTupler'

	if args.VERBOSE:
		print 'ARGS:  \n' + '\n'.join(['   {} : {}'.format(attr, args  .__dict__[attr]) for attr in args  .__dict__])
		print 'CONFIG:\n' + '\n'.join(['   {} : {}'.format(attr, CONFIG.__dict__[attr]) for attr in CONFIG.__dict__])
		print ''

	return CONFIG if not returnArgs else (CONFIG, args)

# get the list of samples and the Dataset object associated with the parameters
def findSample(args):
	if args.NAME == 'HTo2XTo4Mu':
		SIGNALPOINT = tuple(args.SIGNALPOINT)
		samples = DH.getHTo2XTo4MuSamples()
		DP = DEFAULT_AOD_PROCESS if not args.GENONLY else DEFAULT_GEN_PROCESS
		for data in samples:
			if data.signalPoint() == SIGNALPOINT and data.process == DP:
				return data
	elif args.NAME.startswith('DoubleMuon'):
		samples = DH.getDataSamples()
		for data in samples:
			if data.name == args.NAME:
				return data
	else:
		samples = DH.getBackgroundSamples()
		for data in samples:
			if data.name == args.NAME:
				return data
	raise Exception('"' + args.NAME + '" is not a known dataset name; see .dat files in Utilities')
