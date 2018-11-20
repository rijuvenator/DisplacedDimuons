import os
import re
import subprocess as bash
import argparse
from DisplacedDimuons.Common.Constants import SIGNALPOINTS

#########################################
#### GLOBAL CONFIGURATION PARAMETERS ####
#########################################

# 7 + 136 + 72 = 215 background jobs
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
    ('ttbar'        , (72,  50000)), # 3.60M events
)
# 257 data jobs
DataSampleList = (
    ('DoubleMuonRun2016B-07Aug17-v2', ( 9, 50000)), # 0.41M events
    ('DoubleMuonRun2016C-07Aug17'   , (20, 50000)), # 0.96M events
    ('DoubleMuonRun2016D-07Aug17'   , (34, 50000)), # 1.67M events
    ('DoubleMuonRun2016E-07Aug17'   , (32, 50000)), # 1.59M events
    ('DoubleMuonRun2016F-07Aug17'   , (26, 50000)), # 1.26M events
    ('DoubleMuonRun2016G-07Aug17'   , (63, 50000)), # 3.12M events
    ('DoubleMuonRun2016H-07Aug17'   , (73, 50000)), # 3.63M events
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
parser.add_argument('SCRIPT'   ,                                        help='which script to run'                                            )
parser.add_argument('--local'  , dest='LOCAL'  , action='store_true'  , help='whether to run locally'                                         )
parser.add_argument('--condor' , dest='CONDOR' , action='store_true'  , help='whether to run on condor instead of LXBATCH'                    )
parser.add_argument('--hephy'  , dest='HEPHY'  , action='store_true'  , help='whether to run on HEPHY batch system instead of LXBATCH'        )
parser.add_argument('--one'    , dest='ONE'    , action='store_true'  , help='whether to just do one job (e.g. for testing batch)'            )
parser.add_argument('--samples', dest='SAMPLES', default='S2BD'       , help='which samples to run: S(ignal), (Signal)2, B(ackground), D(ata)')
parser.add_argument('--folder' , dest='FOLDER' , default='analyzers'  , help='which folder the script is located in'                          )
parser.add_argument('--extra'  , dest='EXTRA'  , default=[], nargs='*', help='any extra command-line parameters to be passed to script'       )
args = parser.parse_args()

# this is mostly so that **locals() works later on
SCRIPT = args.SCRIPT
FOLDER = args.FOLDER
EXTRA  = args.EXTRA

# set mode: local, lxbatch, hephy, or condor
if (args.LOCAL, args.HEPHY, args.CONDOR).count(True) > 1:
    print '[RUNALL ERROR]: Only one of --local, --hephy, or --condor may be set'
    exit()
if   args.LOCAL : MODE = 'LOCAL'
elif args.HEPHY : MODE = 'HEPHY'
elif args.CONDOR: MODE = 'CONDOR'
else            : MODE = 'LXBATCH'

# ensure that FOLDER/SCRIPT exists
if not os.path.isfile('{CMSSW_BASE}/src/DisplacedDimuons/Analysis/{FOLDER}/{SCRIPT}'.format(**locals())):
    print '[RUNALL ERROR]: {SCRIPT} does not seem to exist in {FOLDER}. Did you forget to use --folder?'.format(**locals())
    exit()

###############################
#### BUILD INPUT ARGUMENTS ####
###############################

# prepare input arguments
# signal samples are all small 30000 event samples, so they get one job each
# any BG sample less than 100K events will also get one job each
# the other BG samples will be split up
# all data samples are huge and must be split up
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

# if --one is passed, restrict ArgsList to just being one of signal and/or one of the small BG MCs
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
output                 = logs/{logname}_{index}.out
log                    = logs/{logname}_{index}.log
error                  = logs/{logname}_{index}.err
arguments              = {ARGS}
#image_size             = 28000
should_transfer_files  = NO
+JobFlavour            = "microcentury"
queue 1
'''

# get rid of empty lines in the condor scripts
# if condorExecutable starts with a blank line, it won't run at all!!
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
        # leaving this line commented in case fewer jobs are desired
        #queue = '1nh' if 'splitting' not in ARGS else '8nh'
        queue = '1nh'
        bash.call('bsub -q {queue} -J ana_{index} < {scriptName}'.format(**locals()), shell=True)
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
    bash.call('mkdir -p logs', shell=True)
    executableName = 'condorExecutable.sh'
    open(executableName, 'w').write(condorExecutable.format(**locals()))
    submitName = 'condorSubmit'
    try:
        numberOfExistingSubmits = int(bash.check_output('ls logs | grep -c "{}*"'.format(submitName), shell=True).strip('\n'))+1
    except bash.CalledProcessError:
        numberOfExistingSubmits = 1
    submitName = submitName + '_' + str(numberOfExistingSubmits)
    for index, ARGS in enumerate(ArgsList):
        condorSubmit += condorSubmitAdd.format(
            logname = SCRIPT.replace('.py', ''),
            index   = index,
            ARGS    = SCRIPT + ' ' + ARGS,
        )

    open(submitName, 'w').write(condorSubmit)
    bash.call('chmod +x '+executableName                  , shell=True)
    bash.call('condor_submit '+submitName                 , shell=True)
    bash.call('cp '+executableName+' '+submitName+' logs/', shell=True)
    bash.call('rm '+submitName                            , shell=True)

#### Run locally with GNU PARALLEL ####
elif MODE == 'LOCAL':
    parallel_command = ['bash', '-c',  'parallel --colsep " " python {SCRIPT} :::: <(echo -e "{ARGLIST}")'.format(
        SCRIPT  = SCRIPT,
        ARGLIST = r'\n'.join(ArgsList)
    )]
    bash.call(parallel_command)
