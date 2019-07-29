#!/usr/bin/env python2
import os
import re
import subprocess as bash
import argparse
import glob

#########################################
#### GLOBAL CONFIGURATION PARAMETERS ####
#########################################

CMSSW_BASE   = os.environ['CMSSW_BASE']
USER         = os.environ['USER']
USER_INITIAL = os.environ['USER'][0].lower()  # needed for workdir path on HEPHY batch
HOME         = os.environ['HOME']

#########################
#### ARGUMENT PARSER ####
#########################

# parse arguments -- this configures which samples to process, which analyzer to run, and which batch system to use
parser = argparse.ArgumentParser()
parser.add_argument('--local'    , dest='LOCAL'    , action='store_true'    , help='whether to run locally'                                  )
parser.add_argument('--condor'   , dest='CONDOR'   , action='store_true'    , help='whether to run on condor'                                )
parser.add_argument('--lxbatch'  , dest='LXBATCH'  , action='store_true'    , help='whether to run on LXBATCH (LSF) batch system'            )
parser.add_argument('--hephy'    , dest='HEPHY'    , action='store_true'    , help='whether to run on HEPHY batch system'                    )
parser.add_argument('--use-proxy', dest='PROXY'    , action='store_true'    , help='whether to ship the GRID certificate with the jobs'      )
parser.add_argument('--method'   , dest='METHOD'   , default=''             , help='which statistical method to use'                         )
parser.add_argument('--file'     , dest='FILE'     , default=''             , help='file containing a specific list of jobs to be run'       )
parser.add_argument('--extra'    , dest='EXTRA'    , default=[], nargs='*'  , help='any extra command-line parameters to be passed to script')
parser.add_argument('--flavour'  , dest='FLAVOUR'  , default='microcentury' , help='which condor job flavour to use'                         )
parser.add_argument('--queue'    , dest='QUEUE'    , default='1nh'          , help='which LSF job queue to use'                              )
parser.add_argument('--splitting', dest='SPLITTING', default=None, type=int , help='whether to split by quantile, and if so, which'          )
args = parser.parse_args()

# this is mostly so that **locals() works later on
METHOD    = args.METHOD
EXTRA     = args.EXTRA
FLAVOUR   = args.FLAVOUR
QUEUE     = args.QUEUE
SPLITTING = args.SPLITTING

# set mode: local, lxbatch, hephy, or condor
# condor is now the default
if (args.LOCAL, args.CONDOR, args.LXBATCH, args.HEPHY).count(True) > 1:
    print '[RUNALL ERROR]: Only one of --local, --condor, --lxbatch, or --hephy may be set'
    exit()
if   args.LOCAL  : MODE = 'LOCAL'
elif args.LXBATCH: MODE = 'LXBATCH'
elif args.HEPHY  : MODE = 'HEPHY'
else             : MODE = 'CONDOR'

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
# glob get the datacards
CARDDIR = CMSSW_BASE+'/src/DisplacedDimuons/Analysis/limits/cards/'
CARDS = glob.glob(CARDDIR+'*')
ArgsList = []
for card in CARDS:
    token = card.replace(CARDDIR+'card_', '').replace('.txt', '')
    relCard = card

    if METHOD == '' or METHOD == 'AsymptoticLimits':
        ArgsList.append('-d {relCard} -n Limits_2Mu_{token}'.format(relCard=relCard, token=token))

    elif METHOD == 'HybridNew':
        appendString = '-H AsymptoticLimits -M HybridNew --testStat LHC --generateNuisances=1 --fitNuisances=0 --toysH=5000 -s -1'

        QUANTILES = ('', '0.025', '0.16', '0.5', '0.84', '0.975')
        THESEQUANTILES = QUANTILES
        if SPLITTING is not None:
            THESEQUANTILES = [QUANTILES[SPLITTING]]

        for quantile in THESEQUANTILES:
            if quantile == '':
                ArgsList.append('-d {relCard} -n Limits_2Mu_{token} {a}'.format(relCard=relCard, token=token, a=appendString))
            else:
                ArgsList.append('-d {relCard} -n Limits_2Mu_{token} {a} --expectedFromGrid={q}'.format(relCard=relCard, token=token, a=appendString, q=quantile))

# if a file is given, make the arguments the lines in the file instead
# you lose the protection of the file check above, though
if args.FILE != '':
    if not os.path.isfile(args.FILE):
        print '[RUNALL ERROR]: {FILE} does not seem to be a valid file.'.format(FILE=args.FILE)
        exit()
    ArgsList = []
    with open(args.FILE) as f:
        for line in f:
            ArgsList.append(line.strip('\n'))

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
cd DisplacedDimuons/Analysis/limits/combineOutput
combine {ARGS}
rm -f core.*
'''

submitHephyScript = '''#!/bin/sh
#SBATCH -o /afs/hephy.at/work/{USER_INITIAL}/{USER}/batch_output/batch-runAll.%j.out
export X509_USER_PROXY={HOME}/private/.proxy
cd {CMSSW_BASE}/src/
eval `scramv1 runtime -sh`
cd DisplacedDimuons/Analysis/limits/combineOutput
combine {ARGS}
'''

condorExecutable = '''
#!/bin/bash
export SCRAM_ARCH='slc7_amd64_gcc530'
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd {CMSSW_BASE}/src/
eval `scramv1 runtime -sh`
cd DisplacedDimuons/Analysis/limits/combineOutput
combine $@
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
        PROXY_LITERAL = '#'

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
            logname       = 'combined{}'.format(METHOD),
            index         = index,
            ARGS          = ARGS,
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
    parallel_command = ['bash', '-c',  'parallel --colsep " " combine :::: <(echo -e "{ARGLIST}")'.format(
        ARGLIST = r'\n'.join(ArgsList)
    )]
    bash.call(parallel_command)
