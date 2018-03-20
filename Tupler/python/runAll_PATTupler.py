import os
import subprocess as bash
from DisplacedDimuons.Analysis.Constants import RECOSIGNALPOINTS

CMSSW_BASE = os.environ['CMSSW_BASE']

submitScript = '''
#!/bin/bash
export X509_USER_PROXY=/afs/cern.ch/user/a/adasgupt/x509up_u79337
cd {CMSSW_BASE}/src/
eval `scramv1 runtime -sh`
cd DisplacedDimuons/Tupler/python
cmsRun PATTupler_cfg.py {mH} {mX} {cTau}
rm -f core.*
'''

for index, (mH, mX, cTau) in enumerate(RECOSIGNALPOINTS):
	scriptName = 'submit_{index}.sh'.format(**locals())
	open(scriptName, 'w').write(submitScript.format(**locals()))
	bash.call('bsub -q 8nh -J ana_{index} < {scriptName}'.format(**locals()), shell=True)
	bash.call('rm {scriptName}'.format(**locals()), shell=True)
