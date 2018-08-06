import os
import re
import subprocess as bash
import argparse
from DisplacedDimuons.Common.Constants import SIGNALPOINTS

CMSSW_BASE = os.environ['CMSSW_BASE']

parser = argparse.ArgumentParser()
parser.add_argument('SCRIPT'   ,                                        help='which script to run'                                            )
parser.add_argument('--local'  , dest='LOCAL'  , action='store_true'  , help='whether to run locally'                                         )
parser.add_argument('--condor' , dest='CONDOR' , action='store_true'  , help='whether to run on condor instead of LXBATCH'                    )
parser.add_argument('--samples', dest='SAMPLES', default='S2BD'       , help='which samples to run: S(ignal), (Signal)2, B(ackground), D(ata)')
parser.add_argument('--folder' , dest='FOLDER' , default='analyzers'  , help='which folder the script is located in'                          )
parser.add_argument('--extra'  , dest='EXTRA'  , default=[], nargs='*', help='any extra command-line parameters to be passed to script'       )
args = parser.parse_args()

SCRIPT = args.SCRIPT
FOLDER = args.FOLDER
EXTRA  = args.EXTRA

# specific scripts that should ignore the splitting parameter
# e.g. scripts that do not loop on the tree but use existing histograms
SplittingVetoList = ('tailCumulativePlots.py',)

# 7 + 136 + 72 = 215 background jobs
BGSampleList = (
    ('DY10to50'  , None        ),
    ('WJets'     , None        ),
    ('WW'        , None        ),
    ('WZ'        , None        ),
    ('ZZ'        , None        ),
    ('tW'        , None        ),
    ('tbarW'     , None        ),
    ('DY50toInf' , (136, 50000)), # 6.76M events
    ('ttbar'     , (72,  50000)), # 3.60M events
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

# This is clunky, but I don't have a better way of doing it
# if additional command-line parameters need to be passed to the analyzer script,
# do it with --extra EXTRA PARAMETERS
# if the extra parameters are options, such as --trigger or --blind, you MUST use __ instead of --
# if you do not, then argparse has no way of knowing that --trigger is an argument and not an option
if len(EXTRA) > 0:
    EXTRA = [e.replace('__','--') for e in EXTRA]
    ArgsList = [a+' '+' '.join(EXTRA) for a in ArgsList]

submitScript = '''
#!/bin/bash
#export X509_USER_PROXY=/afs/cern.ch/user/a/adasgupt/x509up_u79337
cd {CMSSW_BASE}/src/
eval `scramv1 runtime -sh`
cd DisplacedDimuons/Analysis/{FOLDER}
python {SCRIPT} {ARGS}
rm -f core.*
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
'''

condorSubmitAdd = '''
output                 = logs/{logname}_{index}.out
log                    = logs/{logname}_{index}.log
error                  = logs/{logname}_{index}.err
arguments              = {ARGS}
#transfer_output_files  = {OUTPUT}
#transfer_output_remaps = "{REMAP}"
queue 1
'''

def getRootOutputFile(SCRIPT, ARGS):
    line = bash.check_output('grep writeHistograms '+SCRIPT, shell=True)
    matches = re.search(r'roots/.*\.root', line)
    args = ARGS.split()
    sample = args[1]
    if sample.startswith('HTo2X'):
        sp = '_{}_{}_{}'.format(*args[3:6])
        sample += sp
    fname = matches.group(0).replace('{}', sample)
    return fname

if not args.LOCAL:
    # run on LSF LXBATCH
    if not args.CONDOR:
        for index, ARGS in enumerate(ArgsList):
            scriptName = 'submit_{index}.sh'                         .format(**locals())
            open(scriptName, 'w').write(submitScript                 .format(**locals()))
            # leaving this line commented in case fewer jobs are desired
            #queue = '1nh' if 'splitting' not in ARGS else '8nh'
            queue = '1nh'
            bash.call('bsub -q {queue} -J ana_{index} < {scriptName}'.format(**locals()), shell=True)
            bash.call('rm {scriptName}'                              .format(**locals()), shell=True)
    # run on CONDOR
    else:
        bash.call('mkdir -p logs', shell=True)
        executableName = 'condorExecutable.sh'
        open(executableName, 'w').write(condorExecutable             .format(**locals()))
        submitName = 'condorSubmit'
        for index, ARGS in enumerate(ArgsList):
            if FOLDER == 'analyzers':
                OUTPUT = getRootOutputFile(SCRIPT, ARGS)
                REMAP  = OUTPUT.replace('roots/', '') + '=' + OUTPUT
            else:
                OUTPUT = '""'
                REMAP  = ''

            condorSubmit += condorSubmitAdd.format(
                logname = SCRIPT.replace('.py', ''),
                index   = index,
                ARGS    = SCRIPT + ' ' + ARGS,
                OUTPUT  = OUTPUT,
                REMAP   = REMAP,
            )

        open(submitName, 'w').write(condorSubmit)
        bash.call('chmod +x '+executableName                  , shell=True)
       #bash.call('condor_submit '+submitName                 , shell=True)
        bash.call('cp '+executableName+' '+submitName+' logs/', shell=True)
        bash.call('rm '+submitName                            , shell=True)

else:
    # run locally with GNU PARALLEL
    parallel_command = ['bash', '-c',  'parallel --colsep " " python {SCRIPT} :::: <(echo -e "{ARGLIST}")'.format(
        SCRIPT  = SCRIPT,
        ARGLIST = r'\n'.join(ArgsList)
    )]
    bash.call(parallel_command)
