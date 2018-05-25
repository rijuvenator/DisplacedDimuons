import os
import subprocess as bash
import argparse
from DisplacedDimuons.Common.Constants import SIGNALPOINTS

CMSSW_BASE = os.environ['CMSSW_BASE']

parser = argparse.ArgumentParser()
parser.add_argument('SCRIPT'   ,                                      help='which script to run'                                            )
parser.add_argument('--local'  , dest='LOCAL'  , action='store_true', help='whether to run locally'                                         )
parser.add_argument('--samples', dest='SAMPLES', default='S2BD'     , help='which samples to run: S(ignal), (Signal)2, B(ackground), D(ata)')
args = parser.parse_args()

SCRIPT = args.SCRIPT

# to be handled more generally later
BGSampleList   = ('DY100to200',)
DataSampleList = ('DoubleMuonRun2016D-07Aug17',)

# prepare input arguments
ArgsList = []
if 'S' in args.SAMPLES:
    ArgsList.extend(['--name HTo2XTo4Mu   --signalpoint {} {} {}'.format(mH, mX, cTau) for mH, mX, cTau in SIGNALPOINTS])
if 'S' in args.SAMPLES:
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
cd DisplacedDimuons/Analysis/analyzers
python {SCRIPT} {ARGS}
rm -f core.*
'''

if not args.LOCAL:
    for index, ARGS in enumerate(ArgsList):
        scriptName = 'submit_{index}.sh'                     .format(**locals())
        open(scriptName, 'w').write(submitScript             .format(**locals()))
        bash.call('bsub -q 1nh -J ana_{index} < {scriptName}'.format(**locals()), shell=True)
        bash.call('rm {scriptName}'                          .format(**locals()), shell=True)
else:
    parallel_command = ['bash', '-c',  'parallel --colsep " " python {SCRIPT} :::: <(echo -e "{ARGLIST}")'.format(
        SCRIPT  = SCRIPT,
        ARGLIST = r'\n'.join(ArgsList)
    )]
    bash.call(parallel_command)
