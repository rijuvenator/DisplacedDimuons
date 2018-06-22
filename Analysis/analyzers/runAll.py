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

# to be handled more generally later
BGSampleList   = ('DY100to200',)
DataSampleList = ('DoubleMuonRun2016D-07Aug17',)

# prepare input arguments
ArgsList = []
if 'S' in args.SAMPLES:
    ArgsList.extend(['--name HTo2XTo4Mu   --signalpoint {} {} {}'.format(mH, mX, cTau) for mH, mX, cTau in SIGNALPOINTS])
if '2' in args.SAMPLES:
    ArgsList.extend(['--name HTo2XTo2Mu2J --signalpoint {} {} {}'.format(mH, mX, cTau) for mH, mX, cTau in SIGNALPOINTS])
if 'B' in args.SAMPLES:
    ArgsList.extend(['--name {}'.format(NAME) for NAME in BGSampleList])
if 'D' in args.SAMPLES:
    ArgsList.extend(['--name {}'.format(NAME) for NAME in DataSampleList])

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
            scriptName = 'submit_{index}.sh'                     .format(**locals())
            open(scriptName, 'w').write(submitScript             .format(**locals()))
            bash.call('bsub -q 1nh -J ana_{index} < {scriptName}'.format(**locals()), shell=True)
            bash.call('rm {scriptName}'                          .format(**locals()), shell=True)
    # run on CONDOR
    else:
        bash.call('mkdir -p logs', shell=True)
        executableName = 'condorExecutable.sh'
        open(executableName, 'w').write(condorExecutable         .format(**locals()))
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
