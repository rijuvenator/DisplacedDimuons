#!/usr/bin/env python2
import os
import re
import subprocess as bash
import argparse
from DisplacedDimuons.Common.Constants import SIGNALPOINTS

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

DataSampleList_NoBPTX = (
    ('NoBPTXRun2016D-07Aug17', (16, 50000)),
    ('NoBPTXRun2016E-07Aug17', (14, 50000)),
)

DataSampleList_Cosmics_UGMT_base_bottomOnly_CosmicSeed = (
    ('CosmicsRun2016D_reAOD-HLT_UGMT-base-bottomOnly_CosmicSeed', (35, 50000)), # 1714889 events
    ('CosmicsRun2016E_reAOD-HLT_UGMT-base-bottomOnly_CosmicSeed', (52, 50000)), # 2591141 events
)

DataSampleList_Cosmics_UGMT_base_bottomOnly_ppSeed = (
    ('CosmicsRun2016D_reAOD-HLT_UGMT-base-bottomOnly_ppSeed', (27, 50000)), # 1308037 events
    ('CosmicsRun2016E_reAOD-HLT_UGMT-base-bottomOnly_ppSeed', (34, 50000)), # 1676444 events
)

DataSampleList_Cosmics_UGMT_base_CosmicSeed = (
    ('CosmicsRun2016D_reAOD-HLT_UGMT-base_CosmicSeed', (35, 50000)), # 1714889 events
    ('CosmicsRun2016E_reAOD-HLT_UGMT-base_CosmicSeed', (52, 50000)), # 2591141 events
)

DataSampleList_Cosmics_UGMT_base_ppSeed = (
    ('CosmicsRun2016D_reAOD-HLT_UGMT-base_ppSeed', (27, 50000)), # 1308037 events
    ('CosmicsRun2016E_reAOD-HLT_UGMT-base_ppSeed', (34, 50000)), # 1676444 events
)

DataSampleList_Cosmics_UGMT_bottomOnly_CosmicSeed = (
    ('CosmicsRun2016D_reAOD-HLT_UGMT-bottomOnly_CosmicSeed', (35, 50000)), # 1714889 events
    ('CosmicsRun2016E_reAOD-HLT_UGMT-bottomOnly_CosmicSeed', (52, 50000)), # 2591141 events
)

DataSampleList_Cosmics_UGMT_bottomOnly_ppSeed = (
    ('CosmicsRun2016D_reAOD-HLT_UGMT-bottomOnly_ppSeed', (27, 50000)), # 1308037 events
    ('CosmicsRun2016E_reAOD-HLT_UGMT-bottomOnly_ppSeed', (34, 50000)), # 1676444 events
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
parser.add_argument('SCRIPT'   ,                                         help='which script to run'                                            )
parser.add_argument('--local'  , dest='LOCAL'  , action='store_true'   , help='whether to run locally'                                         )
parser.add_argument('--condor' , dest='CONDOR' , action='store_true'   , help='whether to run on condor'                                       )
parser.add_argument('--lxbatch', dest='LXBATCH', action='store_true'   , help='whether to run on LXBATCH (LSF) batch system'                   )
parser.add_argument('--hephy'  , dest='HEPHY'  , action='store_true'   , help='whether to run on HEPHY batch system'                           )
parser.add_argument('--one'    , dest='ONE'    , action='store_true'   , help='whether to just do one job (e.g. for testing batch)'            )
parser.add_argument('--samples', dest='SAMPLES', default='S2BD'        , help='which samples to run: S(ignal), (Signal)2, B(ackground), D(ata)')
parser.add_argument('--file'   , dest='FILE'   , default=''            , help='file containing a specific list of jobs to be run'              )
parser.add_argument('--folder' , dest='FOLDER' , default=None          , help='which folder the script is located in'                          )
parser.add_argument('--extra'  , dest='EXTRA'  , default=[], nargs='*' , help='any extra command-line parameters to be passed to script'       )
parser.add_argument('--flavour', dest='FLAVOUR', default='microcentury', help='which condor job flavour to use'                                )
parser.add_argument('--queue'  , dest='QUEUE'  , default='1nh'         , help='which LSF job queue to use'                                     )
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
    if 'S' in args.SAMPLES:
        ArgsList.extend(['--name HTo2XTo4Mu   --signalpoint {} {} {}'.format(mH, mX, cTau) for mH, mX, cTau in SIGNALPOINTS])
    if '2' in args.SAMPLES:
        ArgsList.extend(['--name HTo2XTo2Mu2J --signalpoint {} {} {}'.format(mH, mX, cTau) for mH, mX, cTau in SIGNALPOINTS])
    if 'B' in args.SAMPLES:
        for NAME, SPLITTING in BGSampleList:
            if SPLITTING is None or SCRIPT in SplittingVetoList:
                ArgsList.append('--name {}'.format(NAME))
            else:
                NJOBS, NEVENTS = SPLITTING
                for i in xrange(NJOBS):
                    ArgsList.append('--name {} --splitting {} {}'.format(NAME, NEVENTS, i))
    if 'D' in args.SAMPLES:
        for NAME, SPLITTING in DataSampleList:
            if SPLITTING is None:
                ArgsList.append('--name {}'.format(NAME))
            else:
                NJOBS, NEVENTS = SPLITTING
                for i in xrange(NJOBS):
                    ArgsList.append('--name {} --splitting {} {}'.format(NAME, NEVENTS, i))

    if 'N' in args.SAMPLES:
        for NAME, SPLITTING in DataSampleList_NoBPTX:
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
    #if the certificate does not exist or is >6h old, create a new one in a a place accesible in AFS. .
    if os.path.isfile('{HOME}/private/.proxy'.format(**locals())) == False \
            or int(bash.check_output('echo $(expr $(date +%s) - $(date +%s -r {HOME}/private/.proxy))'.format(
                        **locals()), shell=True)) > 6*3600:
        print "You need a GRID certificate or current certificate is older than 6h..."
        bash.call('voms-proxy-init --voms cms --valid 168:00 -out {HOME}/private/.proxy'.format(**locals()), shell=True) 
    for index, ARGS in enumerate(ArgsList):
        scriptName = 'submit_{index}.sh'                         .format(**locals())
        open(scriptName, 'w').write(submitHephyScript            .format(**locals()))
        bash.call('sbatch -J ana_{index} {scriptName}'.format(**locals()), shell=True)
        bash.call('rm {scriptName}'                              .format(**locals()), shell=True)

#### Run on CONDOR ####
elif MODE == 'CONDOR':
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
            runNum  = runNum,
            logname = SCRIPT.replace('.py', '') if SCRIPT != '' else 'dummy',
            index   = index,
            ARGS    = SCRIPT + ' ' + ARGS,
            flavour = FLAVOUR,
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
