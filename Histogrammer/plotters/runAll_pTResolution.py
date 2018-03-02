import os
import subprocess as bash

CMSSW_BASE = os.environ['CMSSW_BASE']

signalpoints = [
#	(1000, 350,   35),
#	(1000, 350,  350),
#	(1000, 350, 3500),
#	(1000, 150,   10),
#	(1000, 150,  100),
#	(1000, 150, 1000),
#	(1000,  50,    4),
#	(1000,  50,   40),
#	(1000,  50,  400),
	(1000,  20,    2),
	(1000,  20,   20),
	(1000,  20,  200),
	( 400, 150,   40),
	( 400, 150,  400),
	( 400, 150, 4000),
#	( 400,  50,    8),
#	( 400,  50,   80),
#	( 400,  50,  800),
	( 400,  20,    4),
	( 400,  20,   40),
	( 400,  20,  400),
#	( 200,  50,   20),
#	( 200,  50,  200),
#	( 200,  50, 2000),
#	( 200,  20,    7),
#	( 200,  20,   70),
#	( 200,  20,  700),
	( 125,  50,   50),
	( 125,  50,  500),
	( 125,  50, 5000),
	( 125,  20,   13),
	( 125,  20,  130),
	( 125,  20, 1300),
]

submitScript = '''
#!/bin/bash
#export X509_USER_PROXY=/afs/cern.ch/user/a/adasgupt/x509up_u79337
cd {CMSSW_BASE}/src/
eval `scramv1 runtime -sh`
cd DisplacedDimuons/Histogrammer/plotters
python pTResolution.py {mH} {mX} {cTau}
rm -f core.*
'''

for index, (mH, mX, cTau) in enumerate(signalpoints):
	scriptName = 'submit_{index}.sh'.format(**locals())
	open(scriptName, 'w').write(submitScript.format(**locals()))
	bash.call('bsub -q 8nm -J ana_{index} < {scriptName}'.format(**locals()), shell=True)
	bash.call('rm {scriptName}'.format(**locals()), shell=True)
