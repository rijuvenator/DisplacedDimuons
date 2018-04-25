import os
import subprocess as bash
import argparse
from DisplacedDimuons.Analysis.Constants import RECOSIGNALPOINTS

parser = argparse.ArgumentParser()
parser.add_argument('--local', dest='LOCAL', action='store_true', help='whether to run locally')
args = parser.parse_args()

CMSSW_BASE = os.environ['CMSSW_BASE']

submitScript = '''
#!/bin/bash
#export X509_USER_PROXY=/afs/cern.ch/user/a/adasgupt/x509up_u79337
cd {CMSSW_BASE}/src/
eval `scramv1 runtime -sh`
cd DisplacedDimuons/Analysis/plotters
python cutParameterDistributions.py --signalpoint {mH} {mX} {cTau}
rm -f core.*
'''

if not args.LOCAL:
	for index, (mH, mX, cTau) in enumerate(RECOSIGNALPOINTS):
		scriptName = 'submit_{index}.sh'                     .format(**locals())
		open(scriptName, 'w').write(submitScript             .format(**locals()))
		bash.call('bsub -q 1nh -J ana_{index} < {scriptName}'.format(**locals()), shell=True)
		bash.call('rm {scriptName}'                          .format(**locals()), shell=True)
else:
	parallel_command = ['bash', '-c',  'parallel --colsep " " python cutParameterDistributions.py --signalpoint :::: <(echo -e "{ARGLIST}")'.format(
		ARGLIST  = r'\n'.join(['{} {} {}'.format(mH, mX, cTau) for mH, mX, cTau in RECOSIGNALPOINTS])
	)]
	bash.call(parallel_command)
