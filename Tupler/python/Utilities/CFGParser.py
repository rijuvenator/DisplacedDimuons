import sys, os, argparse
import DisplacedDimuons.Tupler.Utilities.dataHandler as DH
from DisplacedDimuons.Common.Utilities import SPStr

# various default parameters; only change if necessary
# (prefer to specify the parameters externally with the parser)
# in particular the default datasets don't have CLI parameters
# so change them here if they're supposed to be different
DEFAULT_SP          = (125, 20, 13)
DEFAULT_OUTDIR      = ''
DEFAULT_OUTFILE     = 'ntuple_{}.root'

# which dataset to use in specific situations
# here, the "dataset" is the dataset key in data.datasets[]
# i.e. could be PAT, EDM, GS-v1, AODSIM-ReHLT_V37-v1...
# eventually, I expect that all of these options should just be PAT
# but as long as we don't have PAT Tuples for everything,
# this should work to make nTuples in the meantime
DEFAULT_DATASETS = {
    'HTo2XTo4Mu'                : {'PAT':'PAT', 'GEN':'GS-v2', 'AOD':'May2018-AOD-v1'},
    'HTo2XTo2Mu2J'              : {'PAT':'PAT', 'GEN':'GS-v1', 'AOD':'May2018-AOD-v1'},
    'DY100to200'                : {'PAT':'PAT', 'GEN':'PAT'  , 'AOD':'EDM'           },
    'DoubleMuonRun2016D-07Aug17': {'PAT':'PAT', 'GEN':'PAT'  , 'AOD':'EDM'           },
    'DEFAULT'                   : {'PAT':'PAT', 'GEN':'PAT'  , 'AOD':'EDM'           },
}

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
    # aodonly    : whether or not to only run over AOD, instead of PAT
    # outdir     : output directory. Common paths should be stored in DisplacedDimuons.Common.Constants
    # outfile    : output file pattern. Can contain {} for later .format use
    # crab       : submit to crab
    # batch      : submit to lxbatch
    # test       : whether or not to run in test mode: restrict max events to 1000 (or as specified), create the output locally, etc
    # maxevents  : maximum events, will be used only if the TEST option is specified
    # verbose    : print debug info
    # nosubmit   : don't actually submit the job, whether it's crab, lxbatch, or local. useful with verbose if just testing.

    parser.add_argument('NAME'         ,                                                            help='sample name'                       )
    parser.add_argument('--signalpoint', dest='SIGNALPOINT', type=int, nargs=3, default=DEFAULT_SP, help='3 ints defining HTo2X signal point')
    parser.add_argument('--genonly'    , dest='GENONLY'    , action='store_true',                   help='run on GEN only'                   )
    parser.add_argument('--aodonly'    , dest='AODONLY'    , action='store_true',                   help='run on AOD only'                   )
    parser.add_argument('--outdir'     , dest='OUTDIR'     , default=DEFAULT_OUTDIR,                help='output directory'                  )
    parser.add_argument('--outfile'    , dest='OUTFILE'    , default=DEFAULT_OUTFILE,               help='output file pattern'               )
    parser.add_argument('--crab'       , dest='CRAB'       , action='store_true',                   help='submit to CRAB'                    )
    parser.add_argument('--batch'      , dest='BATCH'      , action='store_true',                   help='submit to LXBATCH'                 )
    parser.add_argument('--test'       , dest='TEST'       , action='store_true',                   help='run in test mode'                  )
    parser.add_argument('--maxevents'  , dest='MAXEVENTS'  , type=int, default=1000,                help='max events'                        )
    parser.add_argument('--verbose'    , dest='VERBOSE'    , action='store_true',                   help='print debug info'                  )
    parser.add_argument('--nosubmit'   , dest='SUBMIT'     , action='store_false',                  help='don\'t actually submit job'        )

    # this is expected to be run from an external script, for which sys.argv is
    # ['run.py', 'arg1', 'arg2' ... ]
    # So run as usual on sys.argv[1:]
    args = parser.parse_args(sys.argv[1:])

    # make sure only one of --crab, --batch, and --test are set
    if (args.CRAB, args.BATCH, args.TEST).count(True) > 1:
        raise Exception('Only one of --crab, --batch, or --test may be set')

    # make sure only one of --genonly, --aodonly are set
    if (args.GENONLY, args.AODONLY).count(True) > 1:
        raise Exception('Only one of --genonly, --aodonly may be set')

    # now we can get the particular Dataset object
    data = findSample(args)

    # set the dataset and instance
    DKEY = 'PAT'
    if args.GENONLY: DKEY = 'GEN'
    if args.AODONLY: DKEY = 'AOD'
    SKEY = 'DEFAULT'
    if args.NAME in DEFAULT_DATASETS:
        SKEY = args.NAME
    DATASET  = DEFAULT_DATASETS[SKEY][DKEY]
    INSTANCE = DATASET

    # add a prefix if GENONLY or AODONLY
    if args.GENONLY: args.OUTFILE = 'genOnly_' + args.OUTFILE
    if args.AODONLY: args.OUTFILE = 'aodOnly_' + args.OUTFILE

    # set input and output files according to mode: crab, batch, test, or none (local)
    if args.CRAB:
        INPUTFILES = ['file:dummy.root']
        OUTPUTFILE = args.OUTFILE.format(data.name)
    elif args.BATCH:
        INPUTFILES = data.getFiles(prefix=DH.ROOT_PREFIX, dataset=DATASET, instance=INSTANCE)
        OUTPUTFILE = os.path.join(args.OUTDIR, args.OUTFILE.format(data.name))
    elif args.TEST:
        INPUTFILES = data.getFiles(prefix=DH.ROOT_PREFIX, dataset=DATASET, instance=INSTANCE)[0:1]
        OUTPUTFILE = './test.root'
    else:
        INPUTFILES = data.getFiles(prefix=DH.ROOT_PREFIX, dataset=DATASET, instance=INSTANCE)
        OUTPUTFILE = os.path.join(args.OUTDIR, args.OUTFILE.format(data.name))
    
    # create final configuration namespace and return
    CONFIG            = argparse.Namespace()
    for attr in ('NAME', 'TEST', 'CRAB', 'BATCH', 'VERBOSE', 'SUBMIT'):
        setattr(CONFIG, attr, getattr(args, attr))
    CONFIG.MAXEVENTS  = -1 if not args.TEST else args.MAXEVENTS
    CONFIG.INPUTFILES = INPUTFILES
    CONFIG.PLUGIN     = 'SimpleNTupler'
    CONFIG.OUTPUTFILE = OUTPUTFILE
    CONFIG.DATA       = data
    CONFIG.SOURCE     = DKEY

    # set the FINALSTATE, either 4Mu or 2Mu2J; does nothing if not signal
    CONFIG.FINALSTATE = ''
    if CONFIG.DATA.name.startswith('HTo2X'):
        if '4Mu' in CONFIG.DATA.name:
            CONFIG.FINALSTATE = '4Mu'
        elif '2Mu2J' in CONFIG.DATA.name:
            CONFIG.FINALSTATE = '2Mu2J'

    # set the arguments to gens = cms.InputTag(): prunedGenParticles if PAT, else genParticles
    CONFIG.GENS_TAG = ('prunedGenParticles', '', 'PAT')
    if DATASET != 'PAT':
        CONFIG.GENS_TAG = ('genParticles',)

    # print debug info
    if args.VERBOSE:
        print 'ARGS:  \n' + '\n'.join(['   {} : {}'.format(attr, args  .__dict__[attr]) for attr in args  .__dict__])
        print 'CONFIG:\n' + '\n'.join(['   {} : {}'.format(attr, CONFIG.__dict__[attr]) for attr in CONFIG.__dict__])
        print ''

    return CONFIG if not returnArgs else (CONFIG, args)

# get the list of samples and the Dataset object associated with the parameters
def findSample(args):
    # signal
    if args.NAME == 'HTo2XTo4Mu' or args.NAME == 'HTo2XTo2Mu2J':
        samples = getattr(DH, 'get'+args.NAME+'Samples')()
        SIGNALPOINT = tuple(args.SIGNALPOINT)
        DKEY = 'PAT'
        if args.GENONLY: DKEY = 'GEN'
        if args.AODONLY: DKEY = 'AOD'
        DATASET = DEFAULT_DATASETS[args.NAME][DKEY]
        for data in samples:
            if data.signalPoint() == SIGNALPOINT and DATASET in data.datasets:
                return data
        else:
            raise Exception('No {} dataset found with signal point {} and process {}'.format(args.NAME, SIGNALPOINT, DP))

    # data
    elif args.NAME.startswith('DoubleMuon'):
        samples = DH.getDataSamples()
        for data in samples:
            if data.name == args.NAME:
                return data

    # background
    else:
        samples = DH.getBackgroundSamples()
        for data in samples:
            if data.name == args.NAME:
                return data

    # if nothing found yet, raise error
    raise Exception('"' + args.NAME + '" is not a known dataset name; see .dat files in dat/')
