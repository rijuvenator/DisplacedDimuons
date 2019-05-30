#!/usr/bin/env python2
import os
import re
import subprocess as bash
import argparse
from DisplacedDimuons.Common.Constants import SIGNALPOINTS, REHLT_SIGNALPOINTS

#########################################
#### GLOBAL CONFIGURATION PARAMETERS ####
#########################################

# 8 + 136 + 73 = 217 background jobs
BGSampleList = (
    ('DY10to50'     , None        ),
    ('WJets'        , None        ),
    ('WW'           , None        ),
    ('WZ'           , None        ),
    ('ZZ'           , None        ),
    ('tW'           , None        ),
    ('tbarW'        , None        ),
    ('QCD20toInf-ME', None        ),
#   ('QCD30to50'    , None        ),
#   ('QCD50to80'    , None        ),
#   ('QCD80to120'   , None        ),
    ('DY50toInf'    , (136, 50000)), # 6.76M events
    ('ttbar'        , (73,  50000)), # 3.65M events
)
# 291 data jobs
DataSampleList = (
    ('DoubleMuonRun2016B-07Aug17-v2', (43, 50000)), # 2.12M events
    ('DoubleMuonRun2016C-07Aug17'   , (20, 50000)), # 0.96M events
    ('DoubleMuonRun2016D-07Aug17'   , (34, 50000)), # 1.67M events
    ('DoubleMuonRun2016E-07Aug17'   , (32, 50000)), # 1.59M events
    ('DoubleMuonRun2016F-07Aug17'   , (26, 50000)), # 1.26M events
    ('DoubleMuonRun2016G-07Aug17'   , (63, 50000)), # 3.12M events
    ('DoubleMuonRun2016H-07Aug17'   , (73, 50000)), # 3.63M events
)

# 33 data jobs when using skim
SkimDataSampleList = (
    ('DoubleMuonRun2016B-07Aug17-v2', ( 5, 50000)), # 211338 events
    ('DoubleMuonRun2016C-07Aug17'   , ( 2, 50000)), # 96535  events
    ('DoubleMuonRun2016D-07Aug17'   , ( 4, 50000)), # 166899 events
    ('DoubleMuonRun2016E-07Aug17'   , ( 4, 50000)), # 158760 events
    ('DoubleMuonRun2016F-07Aug17'   , ( 3, 50000)), # 125439 events
    ('DoubleMuonRun2016G-07Aug17'   , ( 7, 50000)), # 311688 events
    ('DoubleMuonRun2016H-07Aug17'   , ( 8, 50000)), # 363262 events
)

# NoBPTX data: 58 jobs in total
DataSampleList_NoBPTX = (
    ('NoBPTXRun2016D-07Aug17', (31, 25000)), # 752442 events
    ('NoBPTXRun2016E-07Aug17', (27, 25000)), # 669686 events
)

DataSampleList_NoBPTX_reHLTvalidation_run276910 = (
    ('NoBPTXRun2016E-07Aug17_reHLTvalidation_run276910', (15, 25000)), # 373817 events
)

DataSampleList_Cosmics_reHLTvalidation_run276910 = (
    ('CosmicsRun2016E_reAOD-HLT_UGMT-base_HLT-CosmicSeed_reHLTvalidation_run276910', (15, 25000)), # 373617 events
)

DataSampleList_NoBPTX_reHLTvalidation_StoppedPtlsSubsetJSON = (
    ('CosmicsRun2016D_reAOD-HLT_UGMT-base_HLT-CosmicSeed_StoppedPtlsSubsetJSON', (31, 25000)), # 751968 events
    ('CosmicsRun2016E_reAOD-HLT_UGMT-base_HLT-CosmicSeed_StoppedPtlsSubsetJSON', (28, 25000)), # 669410 events
)


DataSampleList_NoBPTX_reHLTvalidation_run276936 = (
    ('NoBPTXRun2016E-07Aug17_reHLTvalidation_run276936', (8, 25000)), # 184824 events
)

DataSampleList_Cosmics_reHLTvalidation_run276936 = (
    ('CosmicsRun2016E_reAOD-HLT_UGMT-base_HLT-CosmicSeed_reHLTvalidation_run276936', (9, 25000)), # 209283 events
)

# NoBPTX data (re-HLT; cosmic seed): 30 jobs in total
DataSampleList_NoBPTX_reHLT_CosmicSeed = (
    ('NoBPTXRun2016D-07Aug17_reAOD-HLT_cosmic-seeded-path', (30, 25000)), # 742904 events
)

# NoBPTX data (re-HLT; pp seed): 15 jobs in total
DataSampleList_NoBPTX_reHLT_ppSeed = (
    ('NoBPTXRun2016D-07Aug17_reAOD-HLT_pp-seeded-path', (15, 25000)), # 370759 events
)

# Cosmcis data: 591 jobs in total
DataSampleList_Cosmics_UGMT_base_bottomOnly_CosmicSeed = (
    ('CosmicsRun2016D_reAOD-HLT_UGMT-base-bottomOnly_HLT-CosmicSeed', (70, 25000)), # 1733944 events
    ('CosmicsRun2016E_reAOD-HLT_UGMT-base-bottomOnly_HLT-CosmicSeed', (104, 25000)), # 2591141 events
)

DataSampleList_Cosmics_UGMT_base_bottomOnly_ppSeed = (
    ('CosmicsRun2016D_reAOD-HLT_UGMT-base-bottomOnly_HLT-ppSeed', (53, 25000)), # 1322612 events
    ('CosmicsRun2016E_reAOD-HLT_UGMT-base-bottomOnly_HLT-ppSeed', (68, 25000)), # 1676444 events
)

DataSampleList_Cosmics_UGMT_base_CosmicSeed = (
    ('CosmicsRun2016D_reAOD-HLT_UGMT-base_HLT-CosmicSeed', (70, 25000)), # 1733944 events
    ('CosmicsRun2016E_reAOD-HLT_UGMT-base_HLT-CosmicSeed', (32, 25000)), # 778138 events
)

DataSampleList_Cosmics_UGMT_base_ppSeed = (
    ('CosmicsRun2016D_reAOD-HLT_UGMT-base_HLT-ppSeed', (53, 25000)), # 1322612 events
    ('CosmicsRun2016E_reAOD-HLT_UGMT-base_HLT-ppSeed', (24, 25000)), # 595818 events
)

DataSampleList_Cosmics_UGMT_bottomOnly_CosmicSeed = (
    # no selected LS in 2016D data
    ('CosmicsRun2016E_reAOD-HLT_UGMT-bottomOnly_HLT-CosmicSeed', (73, 25000)), # 1813003 events
)

DataSampleList_Cosmics_UGMT_bottomOnly_ppSeed = (
    # no selected LS in 2016D data
    ('CosmicsRun2016E_reAOD-HLT_UGMT-bottomOnly_HLT-ppSeed', (44, 25000)), # 1080626 events
)

# specific scripts that should ignore the splitting parameter
# e.g. scripts that do not loop on the tree but use existing histograms
SplittingVetoList = ('tailCumulativePlots.py',)

# set some global variables needed for submission scripts
CMSSW_BASE   = os.environ['CMSSW_BASE']
USER         = os.environ['USER']
USER_INITIAL = os.environ['USER'][0].lower()  # needed for workdir path on HEPHY batch
HOME         = os.environ['HOME']

#########################
#### ARGUMENT PARSER ####
#########################

# parse arguments -- this configures which samples to process, which analyzer to run, and which batch system to use
parser = argparse.ArgumentParser()
parser.add_argument('SCRIPT'   ,                                           help='which script to run'                                            )
parser.add_argument('--local'    , dest='LOCAL'  , action='store_true'   , help='whether to run locally'                                         )
parser.add_argument('--condor'   , dest='CONDOR' , action='store_true'   , help='whether to run on condor'                                       )
parser.add_argument('--lxbatch'  , dest='LXBATCH', action='store_true'   , help='whether to run on LXBATCH (LSF) batch system'                   )
parser.add_argument('--hephy'    , dest='HEPHY'  , action='store_true'   , help='whether to run on HEPHY batch system'                           )
parser.add_argument('--use-proxy', dest='PROXY'  , action='store_true'   , help='whether to ship the GRID certificate with the jobs'             )
parser.add_argument('--one'      , dest='ONE'    , action='store_true'   , help='whether to just do one job (e.g. for testing batch)'            )
parser.add_argument('--samples'  , dest='SAMPLES', default='S2BD'        , help='which samples to run: S(ignal), (Signal)2, B(ackground), D(ata)')
parser.add_argument('--file'     , dest='FILE'   , default=''            , help='file containing a specific list of jobs to be run'              )
parser.add_argument('--folder'   , dest='FOLDER' , default=None          , help='which folder the script is located in'                          )
parser.add_argument('--extra'    , dest='EXTRA'  , default=[], nargs='*' , help='any extra command-line parameters to be passed to script'       )
parser.add_argument('--flavour'  , dest='FLAVOUR', default='microcentury', help='which condor job flavour to use'                                )
parser.add_argument('--queue'    , dest='QUEUE'  , default='1nh'         , help='which LSF job queue to use'                                     )
args = parser.parse_args()

# get current directory automatically
if args.FOLDER is None:
    args.FOLDER = os.path.basename(os.getcwd())

# this is mostly so that **locals() works later on
SCRIPT  = args.SCRIPT
FOLDER  = args.FOLDER
EXTRA   = args.EXTRA
FLAVOUR = args.FLAVOUR
QUEUE   = args.QUEUE

# set mode: local, lxbatch, hephy, or condor
# condor is now the default
if (args.LOCAL, args.CONDOR, args.LXBATCH, args.HEPHY).count(True) > 1:
    print '[RUNALL ERROR]: Only one of --local, --condor, --lxbatch, or --hephy may be set'
    exit()
if   args.LOCAL  : MODE = 'LOCAL'
elif args.LXBATCH: MODE = 'LXBATCH'
elif args.HEPHY  : MODE = 'HEPHY'
else             : MODE = 'CONDOR'

# ensure that FOLDER/SCRIPT exists, if FILE is not given
if args.FILE == '':
    if not os.path.isfile('{CMSSW_BASE}/src/DisplacedDimuons/Analysis/{FOLDER}/{SCRIPT}'.format(**locals())):
        print '[RUNALL ERROR]: {SCRIPT} does not seem to exist in {FOLDER}.'.format(**locals())
        exit()

# ensure that FLAVOUR/QUEUE is an acceptable value
if   MODE == 'CONDOR':
    if FLAVOUR not in ('espresso', 'microcentury', 'longlunch', 'workday', 'tomorrow', 'testmatch', 'nextweek'):
        print '[RUNALL ERROR]: {FLAVOUR} is not a valid condor job flavour.'.format(**locals())
elif MODE == 'LXBATCH':
    if QUEUE not in ('8nm', '1nh', '8nh', '1nd', '2nd', '1nw', '2nw'):
        print '[RUNALL ERROR]: {QUEUE} is not a valid LSF queue.'.format(**locals())

###############################
#### BUILD INPUT ARGUMENTS ####
###############################

# prepare input arguments
# signal samples are all small 30000 event samples, so they get one job each
# any BG sample less than 100K events will also get one job each
# the other BG samples will be split up
# all data samples are huge and must be split up
if args.FILE == '':
    ArgsList = []
    if 'S' in args.SAMPLES and not 'reHLT' in args.SAMPLES:
        ArgsList.extend(['--name HTo2XTo4Mu   --signalpoint {} {} {}'.format(mH, mX, cTau) for mH, mX, cTau in SIGNALPOINTS])
    if '2' in args.SAMPLES and not 'reHLT' in args.SAMPLES:
        ArgsList.extend(['--name HTo2XTo2Mu2J --signalpoint {} {} {}'.format(mH, mX, cTau) for mH, mX, cTau in SIGNALPOINTS])
    if all([a in args.SAMPLES for a in ('2', 'reHLT', 'CosmicSeed')]):
        ArgsList.extend(['--name HTo2XTo2Mu2J_reHLT_CosmicSeed --signalpoint {} {} {}'.format(mH, mX, cTau) for mH, mX, cTau in REHLT_SIGNALPOINTS])
    if all([a in args.SAMPLES for a in ('2', 'reHLT', 'ppSeed')]):
        ArgsList.extend(['--name HTo2XTo2Mu2J_reHLT_ppSeed --signalpoint {} {} {}'.format(mH, mX, cTau) for mH, mX, cTau in REHLT_SIGNALPOINTS])
    if 'B' in args.SAMPLES:
        for NAME, SPLITTING in BGSampleList:
            if SPLITTING is None or SCRIPT in SplittingVetoList:
                ArgsList.append('--name {}'.format(NAME))
            else:
                NJOBS, NEVENTS = SPLITTING
                for i in xrange(NJOBS):
                    ArgsList.append('--name {} --splitting {} {}'.format(NAME, NEVENTS, i))
    if 'D' in args.SAMPLES:
        # if "skim" is in the extra list (passed to Analyzer), use the SkimDataSampleList
        # The Analyzer replaces ntuple with skim in the file name, smaller files
        RealDataSampleList = DataSampleList if '__skim' not in EXTRA else SkimDataSampleList
        for NAME, SPLITTING in RealDataSampleList:
            if SPLITTING is None:
                ArgsList.append('--name {}'.format(NAME))
            else:
                NJOBS, NEVENTS = SPLITTING
                for i in xrange(NJOBS):
                    ArgsList.append('--name {} --splitting {} {}'.format(NAME, NEVENTS, i))
    if 'N_orig' in args.SAMPLES:
        for NAME, SPLITTING in DataSampleList_NoBPTX:
            if SPLITTING is None:
                ArgsList.append('--name {}'.format(NAME))
            else:
                NJOBS, NEVENTS = SPLITTING
                for i in xrange(NJOBS):
                    ArgsList.append('--name {} --splitting {} {}'.format(NAME, NEVENTS, i))
    if 'N_rehlt_cosmicseed' in args.SAMPLES:
        for NAME, SPLITTING in DataSampleList_NoBPTX_reHLT_CosmicSeed:
            if SPLITTING is None:
                ArgsList.append('--name {}'.format(NAME))
            else:
                NJOBS, NEVENTS = SPLITTING
                for i in xrange(NJOBS):
                    ArgsList.append('--name {} --splitting {} {}'.format(NAME, NEVENTS, i))
    if 'N_rehlt_ppseed' in args.SAMPLES:
        for NAME, SPLITTING in DataSampleList_NoBPTX_reHLT_ppSeed:
            if SPLITTING is None:
                ArgsList.append('--name {}'.format(NAME))
            else:
                NJOBS, NEVENTS = SPLITTING
                for i in xrange(NJOBS):
                    ArgsList.append('--name {} --splitting {} {}'.format(NAME, NEVENTS, i))

    cosmics_dict = {
        'C_base_bottomonly_cosmicseed': DataSampleList_Cosmics_UGMT_base_bottomOnly_CosmicSeed,
        'C_base_bottomonly_ppseed'    : DataSampleList_Cosmics_UGMT_base_bottomOnly_ppSeed,
        'C_base_cosmicseed'           : DataSampleList_Cosmics_UGMT_base_CosmicSeed,
        'C_base_ppseed'               : DataSampleList_Cosmics_UGMT_base_ppSeed,
        'C_bottomonly_cosmicseed'     : DataSampleList_Cosmics_UGMT_bottomOnly_CosmicSeed,
        'C_bottomonly_ppseed'         : DataSampleList_Cosmics_UGMT_bottomOnly_ppSeed,
        'C_base_cosmicseed_stoppedptlssubsetjson': DataSampleList_NoBPTX_reHLTvalidation_StoppedPtlsSubsetJSON,
    }
    for identifier in cosmics_dict:
        if identifier in args.SAMPLES:
            for NAME, SPLITTING in cosmics_dict[identifier]:
                if SPLITTING is None:
                    ArgsList.append('--name {}'.format(NAME))
                else:
                    NJOBS, NEVENTS = SPLITTING
                    for i in xrange(NJOBS):
                        ArgsList.append('--name {} --splitting {} {}'.format(NAME, NEVENTS, i))

    if 'N_rehltvalidation_matchinglumisrun' in args.SAMPLES:
        for NAME, SPLITTING in DataSampleList_NoBPTX_reHLTvalidation_run276910:
            if SPLITTING is None:
                ArgsList.append('--name {}'.format(NAME))
            else:
                NJOBS, NEVENTS = SPLITTING
                for i in xrange(NJOBS):
                    ArgsList.append('--name {} --splitting {} {}'.format(NAME, NEVENTS, i))

    if 'C_rehltvalidation_matchinglumisrun' in args.SAMPLES:
        for NAME, SPLITTING in DataSampleList_Cosmics_reHLTvalidation_run276910:
            if SPLITTING is None:
                ArgsList.append('--name {}'.format(NAME))
            else:
                NJOBS, NEVENTS = SPLITTING
                for i in xrange(NJOBS):
                    ArgsList.append('--name {} --splitting {} {}'.format(NAME, NEVENTS, i))

    if 'N_rehltvalidation_differinglumisrun' in args.SAMPLES:
        for NAME, SPLITTING in DataSampleList_NoBPTX_reHLTvalidation_run276936:
            if SPLITTING is None:
                ArgsList.append('--name {}'.format(NAME))
            else:
                NJOBS, NEVENTS = SPLITTING
                for i in xrange(NJOBS):
                    ArgsList.append('--name {} --splitting {} {}'.format(NAME, NEVENTS, i))

    if 'C_rehltvalidation_differinglumisrun' in args.SAMPLES:
        for NAME, SPLITTING in DataSampleList_Cosmics_reHLTvalidation_run276936:
            if SPLITTING is None:
                ArgsList.append('--name {}'.format(NAME))
            else:
                NJOBS, NEVENTS = SPLITTING
                for i in xrange(NJOBS):
                    ArgsList.append('--name {} --splitting {} {}'.format(NAME, NEVENTS, i))

# if a file is given, make the arguments the lines in the file instead
# the script name should be in the arguments, so pass a dummy argument to SCRIPT and set it to nothing here
# you lose the protection of the file check above, though
# below this line, SCRIPT being empty makes everything still work, but be careful
if args.FILE != '':
    if not os.path.isfile(args.FILE):
        print '[RUNALL ERROR]: {FILE} does not seem to be a valid file.'.format(FILE=args.FILE)
        exit()
    SCRIPT = ''
    ArgsList = []
    with open(args.FILE) as f:
        for line in f:
            ArgsList.append(line.strip('\n'))

# if --one is passed, restrict ArgsList to just being one of signal and/or one of the small BG MCs
# this is for testing job submission to condor or LSF, for example, and --test isn't appropriate
if args.ONE:
    ArgsList = []
    if 'S' in args.SAMPLES or '2' in args.SAMPLES:
        ArgsList.extend(['--name HTo2XTo4Mu --signalpoint 125 20 13'])
    if 'B' in args.SAMPLES:
        ArgsList.extend(['--name WJets'])
    if 'C' in args.SAMPLES:
        ArgsList.extend(['--name C_base_ppseed'])

# This is clunky, but I don't have a better way of doing it
# if additional command-line parameters need to be passed to the analyzer script,
# do it with --extra EXTRA PARAMETERS
# if the extra parameters are options, such as --trigger or --blind, you MUST use __ instead of --
# if you do not, then argparse has no way of knowing that --trigger is an argument and not an option
if len(EXTRA) > 0:
    EXTRA = [e.replace('__','--') for e in EXTRA]
    ArgsList = [a+' '+' '.join(EXTRA) for a in ArgsList]

####################################
#### SUBMISSION SCRIPT LITERALS ####
####################################

# Various literal submission scripts with formatting placeholders for use in submission loops below
# Some format specifiers are global; otherwise ARGS will be set during the loop + format
submitScript = '''
#!/bin/bash
#export X509_USER_PROXY=/afs/cern.ch/user/a/adasgupt/x509up_u79337
cd {CMSSW_BASE}/src/
eval `scramv1 runtime -sh`
cd DisplacedDimuons/Analysis/{FOLDER}
python {SCRIPT} {ARGS}
rm -f core.*
'''

submitHephyScript = '''#!/bin/sh
#SBATCH -o /afs/hephy.at/work/{USER_INITIAL}/{USER}/batch_output/batch-runAll.%j.out
export X509_USER_PROXY={HOME}/private/.proxy
cd {CMSSW_BASE}/src/
eval `scramv1 runtime -sh`
cd DisplacedDimuons/Analysis/{FOLDER}
python {SCRIPT} {ARGS}
'''

condorExecutable = '''
#!/bin/bash
export SCRAM_ARCH='slc6_amd64_gcc530'
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd {CMSSW_BASE}/src/
eval `scramv1 runtime -sh`
cd DisplacedDimuons/Analysis/{FOLDER}
python $@
'''

condorSubmit = '''
universe               = vanilla
executable             = condorExecutable.sh
getenv                 = True
'''

condorSubmitAdd = '''
output                 = logs/run{runNum}/{logname}_{index}.out
log                    = logs/run{runNum}/{logname}_{index}.log
error                  = logs/run{runNum}/{logname}_{index}.err
arguments              = {ARGS}
{proxy_literal}
requirements           = (OpSysAndVer =?= "SLCern6")
#image_size             = 28000
should_transfer_files  = NO
+JobFlavour            = "{flavour}"
queue 1
'''

# get rid of empty lines in the condor scripts
# if condorExecutable starts with a blank line, it won't run at all!!
# the other blank lines are just for sanity, at this point
def stripEmptyLines(string):
    if string[0] == '\n':
        string = string[1:]
    return string
condorExecutable = stripEmptyLines(condorExecutable)
condorSubmit     = stripEmptyLines(condorSubmit    )
condorSubmitAdd  = stripEmptyLines(condorSubmitAdd )

#############################
#### SUBMIT AND RUN JOBS ####
#############################

#### Run on LSF LXBATCH ####
if MODE == 'LXBATCH':
    for index, ARGS in enumerate(ArgsList):
        scriptName = 'submit_{index}.sh'                         .format(**locals())
        open(scriptName, 'w').write(submitScript                 .format(**locals()))
        bash.call('bsub -q {QUEUE} -J ana_{index} < {scriptName}'.format(**locals()), shell=True)
        bash.call('rm {scriptName}'                              .format(**locals()), shell=True)

#### Run on HEPHY Batch ####
elif MODE == 'HEPHY':
    if args.PROXY:
        #if the certificate does not exist or is >6h old, create a new one in a place accesible in AFS
        if not os.path.isfile('{HOME}/private/.proxy'.format(**locals())) or \
                int(bash.check_output('echo $(expr $(date +%s) - $(date +%s -r {HOME}/private/.proxy))'.format(
                    **locals()), shell=True)) > 6*3600:
            print('GRID certificate not found or older than 6 hours. You will need a new one.')
            bash.call('voms-proxy-init --voms cms --valid 168:00 -out {HOME}/private/.proxy'.format(**locals()), shell=True) 

    for index, ARGS in enumerate(ArgsList):
        scriptName = 'submit_{index}.sh'                         .format(**locals())
        open(scriptName, 'w').write(submitHephyScript            .format(**locals()))
        bash.call('sbatch -J ana_{index} {scriptName}'.format(**locals()), shell=True)
        bash.call('rm {scriptName}'                              .format(**locals()), shell=True)

#### Run on CONDOR ####
elif MODE == 'CONDOR':
    if args.PROXY:
        # prepare the grid certificate
        proxy = '{HOME}/private/.proxy'.format(**locals())
        if not os.path.isfile(proxy) or \
                int(bash.check_output('echo $(expr $(date +%s) - $(date +%s -r {}))'.format(
                    proxy), shell=True)) > 6*3600:
            print('GRID certificate not found or older than 6 hours. You will need a new one.')
            bash.call('voms-proxy-init --voms cms --valid 168:00 -out {}'.format(proxy), shell=True)
        
        # export the environment variable related to the certificate
        os.environ['X509_USER_PROXY'] = proxy

        PROXY_LITERAL = 'x509userproxy = $ENV(X509_USER_PROXY)\nuse_x509userproxy = true'

    else:
        PROXY_LITERAL = ''

    # make the logs directory if it doesn't exist
    bash.call('mkdir -p logs', shell=True)
    executableName = 'condorExecutable.sh'
    open(executableName, 'w').write(condorExecutable.format(**locals()))

    # get the number of run* directories, and make the next one
    try:
        numberOfExistingRuns = int(bash.check_output('ls -d logs/run* 2>/dev/null | wc -l', shell=True).strip('\n'))
    except bash.CalledProcessError:
        numberOfExistingRuns = 0
    runNum = numberOfExistingRuns+1
    bash.call('mkdir logs/run{}'.format(runNum), shell=True)

    # make the submit file
    submitName = 'condorSubmit'
    for index, ARGS in enumerate(ArgsList):
        condorSubmit += condorSubmitAdd.format(
            runNum        = runNum,
            logname       = SCRIPT.replace('.py', '') if SCRIPT != '' else 'dummy',
            index         = index,
            ARGS          = SCRIPT + ' ' + ARGS,
            flavour       = FLAVOUR,
            proxy_literal = PROXY_LITERAL,
        )

    open(submitName, 'w').write(condorSubmit)
    bash.call('chmod +x '+executableName                                 , shell=True)
    bash.call('condor_submit '+submitName                                , shell=True)
    bash.call('cp '+executableName+' '+submitName+' logs/run'+str(runNum), shell=True)
    bash.call('rm '+submitName                                           , shell=True)

#### Run locally with GNU PARALLEL ####
elif MODE == 'LOCAL':
    parallel_command = ['bash', '-c',  'parallel --colsep " " python {SCRIPT} :::: <(echo -e "{ARGLIST}")'.format(
        SCRIPT  = SCRIPT,
        ARGLIST = r'\n'.join(ArgsList)
    )]
    bash.call(parallel_command)
