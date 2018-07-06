import os
import re
import subprocess as bash
import argparse
from DisplacedDimuons.Common.Constants import SIGNALPOINTS

CMSSW_BASE = os.environ['CMSSW_BASE']

parser = argparse.ArgumentParser()
parser.add_argument('SCRIPT'   ,                                      help='which script to run'                                            )
parser.add_argument('--local'  , dest='LOCAL'  , action='store_true', help='whether to run locally'                                         )
parser.add_argument('--condor' , dest='CONDOR' , action='store_true', help='whether to run on condor instead of LXBATCH'                    )
parser.add_argument('--samples', dest='SAMPLES', default='S2BD'     , help='which samples to run: S(ignal), (Signal)2, B(ackground), D(ata)')
parser.add_argument('--folder' , dest='FOLDER' , default='analyzers', help='which folder the script is located in'                          )
args = parser.parse_args()

SCRIPT = args.SCRIPT
FOLDER = args.FOLDER

BGSampleList = (
    ('DY10to50'  , None        ),
    ('WJets'     , None        ),
    ('WW'        , None        ),
    ('WZ'        , None        ),
    ('ZZ'        , None        ),
    ('tW'        , None        ),
    ('tbarW'     , None        ),
    ('DY50toInf' , (68, 100000)),
    ('ttbar'     , (36, 100000)),
)
DataSampleList = (
    #('DoubleMuonRun2016B-07Aug17-v2', ( 5, 100000)),
    #('DoubleMuonRun2016C-07Aug17'   , (10, 100000)),
    #('DoubleMuonRun2016D-07Aug17'   , (17, 100000)),
    #('DoubleMuonRun2016E-07Aug17'   , (16, 100000)),
    #('DoubleMuonRun2016F-07Aug17'   , (13, 100000)),
    #('DoubleMuonRun2016G-07Aug17'   , (32, 100000)),
    #('DoubleMuonRun2016H-07Aug17'   , (37, 100000)),
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
        if SPLITTING is None:
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
            queue = '1nh' if 'splitting' not in ARGS else '8nh'
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
